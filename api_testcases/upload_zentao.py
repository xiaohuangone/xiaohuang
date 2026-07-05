"""上传测试用例到禅道"""
import json
import time
import re
import sys
import hashlib
import requests

BASE_URL = "https://sub2.hermes.cn.mt/zentao"
USERNAME = "qa_girl_02"
PASSWORD = "bndBiGCEn9oEZA4k8XAa1!"

session = requests.Session()
session.verify = False
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
})
import urllib3
urllib3.disable_warnings()


def md5(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def web_login():
    """浏览器方式登录"""
    print("[WEB] 登录禅道...")

    # 1. 访问首页
    r = session.get(BASE_URL, timeout=30)
    r.encoding = "utf-8"

    # 2. 获取 verifyRand
    rand_match = re.search(r'<input[^>]+name="verifyRand"[^>]+value="(\d+)"', r.text)
    if rand_match:
        rand = rand_match.group(1)
    else:
        r2 = session.get(f"{BASE_URL}/index.php?m=user&f=refreshRandom", timeout=30)
        rand_match = re.search(r'(\d{9,})', r2.text)
        rand = rand_match.group(1) if rand_match else ""

    print(f"[WEB] verifyRand: {rand}")

    # 3. 加密密码 md5(md5(密码) + rand)
    pwd_md5 = md5(PASSWORD)
    encrypted = md5(pwd_md5 + rand)
    print(f"[WEB] encrypted: {encrypted}")

    # 4. 提交登录
    payload = {
        "account": USERNAME,
        "password": encrypted,
        "referer": "/",
        "verifyRand": rand,
        "keepLogin": "0",
    }
    r = session.post(
        f"{BASE_URL}/index.php?m=user&f=login",
        data=payload,
        headers={"X-Requested-With": "XMLHttpRequest"},
        timeout=30,
    )
    print(f"[WEB] 登录状态: {r.status_code}")

    try:
        data = r.json()
        if data.get("result") == "success":
            print("[WEB] 登录成功!")
            return True
        print(f"[WEB] 登录返回: {data}")
    except Exception:
        if "/zentao/" in r.text and "loginForm" not in r.text:
            print("[WEB] 登录成功(页面跳转)!")
            return True
        print(f"[WEB] 响应: {r.text[:200]}")

    return False


def api_login():
    """REST API 登录"""
    print("[API] 尝试 API 登录...")
    url = f"{BASE_URL}/api.php/v1/tokens"
    data = {"account": USERNAME, "password": md5(PASSWORD)}

    try:
        r = session.post(url, json=data, timeout=30)
        result = r.json()
        print(f"[API] 响应: {result}")
        if "token" in result:
            token = result["token"]
            session.headers["Authorization"] = f"Token {token}"
            print(f"[API] 登录成功! Token: {token[:20]}...")
            return True
    except Exception as e:
        print(f"[API] 异常: {e}")

    return False


def get_session_id():
    """获取 zentaosid"""
    for c in session.cookies:
        if c.name == "zentaosid":
            return c.value
    return None


def check_api():
    """检查 API 可用性"""
    sid = get_session_id()
    print(f"\n[INFO] Session ID (zentaosid): {sid}")

    # 尝试获取产品列表
    for name, url in [
        ("products", f"{BASE_URL}/api.php/v1/products?limit=5"),
        ("projects", f"{BASE_URL}/api.php/v1/projects?limit=5"),
    ]:
        try:
            r = session.get(url, timeout=30)
            print(f"[API] {name}: {r.status_code} - {r.text[:200]}")
        except Exception as e:
            print(f"[API] {name} 请求失败: {e}")


def upload_test_cases():
    """导出测试用例模板"""
    test_cases = [
        ("TC-SMOKE-001", "根路径健康检查", "P0", "GET", "/", "系统", "服务可用性检查"),
        ("TC-SMOKE-002", "注册接口可达", "P0", "POST", "/v1/auth/register", "冒烟", "smoke: 核心接口可达"),
        ("TC-SMOKE-003", "登录接口可达", "P0", "POST", "/v1/auth/login", "冒烟", "smoke: 认证可用"),
        ("TC-SMOKE-004", "商品列表接口可达", "P0", "GET", "/v1/products", "冒烟", "smoke: 商品服务"),
        ("TC-SMOKE-005", "加购接口可达", "P0", "POST", "/v1/cart/items", "冒烟", "smoke: 购物车服务"),
        ("TC-SMOKE-006", "下单接口可达", "P0", "POST", "/v1/orders/checkout", "冒烟", "smoke: 订单服务"),
        ("TC-AUTH-001", "用户注册-正向", "P0", "POST", "/v1/auth/register", "认证", "新用户注册"),
        ("TC-AUTH-006", "用户登录-正向", "P0", "POST", "/v1/auth/login", "认证", "有效凭证登录"),
        ("TC-PROD-001", "商品列表-默认分页", "P0", "GET", "/v1/products", "商品", "分页查询"),
        ("TC-CART-001", "加入购物车-正向", "P0", "POST", "/v1/cart/items", "购物车", "加购"),
        ("TC-ORDER-001", "下单结算-正向", "P0", "POST", "/v1/orders/checkout", "订单", "正常下单"),
        ("TC-PAY-001", "发起支付-正向", "P1", "POST", "/v1/payments/{orderId}/pay", "支付", "发起支付"),
        ("TC-REV-001", "创建评价-正向", "P1", "POST", "/v1/reviews", "评价", "创建评价"),
        ("TC-COUP-001", "获取可用优惠券", "P1", "GET", "/v1/coupons/available", "优惠券", "列表查询"),
        ("TC-AFTER-001", "申请售后-正向", "P1", "POST", "/v1/aftersales/apply", "售后", "提交售后"),
        ("TC-NOTIF-001", "获取通知列表", "P1", "GET", "/v1/notifications", "通知", "列表查询"),
    ]

    # 导出 ZenTao 导入模板
    output = r"E:\AI\LearningSpace\web-wenrui\api_testcases\zentao_import_template.json"
    with open(output, "w", encoding="utf-8") as f:
        json.dump(test_cases, f, ensure_ascii=False, indent=2)

    print(f"\n[INFO] 已导出: {output}")
    print(f"[INFO] 共 {len(test_cases)} 条用例")

    # 同时输出 Excel 友好格式摘要
    print("\n" + "=" * 80)
    print(f"{'ID':<15} {'标题':<25} {'优先级':<6} {'方法':<6} {'路径'}")
    print("=" * 80)
    for tc in test_cases:
        print(f"{tc[0]:<15} {tc[1]:<25} {tc[2]:<6} {tc[3]:<6} {tc[4]}")
    print("=" * 80)


def main():
    print("=" * 50)
    print("禅道测试用例上传工具")
    print("=" * 50)

    # 先尝试 API 登录
    api_login()
    time.sleep(1)

    # 再尝试 Web 登录（补充 cookie）
    web_login()
    time.sleep(1)

    # 检查 API 可用性
    check_api()

    # 导出用例
    upload_test_cases()

    print("\n" + "=" * 50)
    print("[手动步骤]")
    print("1. 打开 https://sub2.hermes.cn.mt/zentao/")
    print("2. 登录账号: qa_girl_02 / bndBiGCEn9oEZA4k8XAa1!")
    print("3. 进入 测试 -> 用例")
    print("4. 选择产品，点击'导入'，上传 Excel 或 JSON")
    print("=" * 50)


if __name__ == "__main__":
    main()
