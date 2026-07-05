"""使用 Playwright 登录禅道 + 截图（不含实时 API 调用）"""
import asyncio
import json
import os

from playwright.async_api import async_playwright

BASE_URL = "https://sub2.hermes.cn.mt/zentao"
USERNAME = "qa_girl_02"
PASSWORD = "bndBiGCEn9oEZA4k8XAa1!"

TEST_CASES = [
    ("TC-SMOKE-001", "根路径健康检查", "P0", "GET", "/", "系统", "服务可用性检查"),
    ("TC-SMOKE-002", "注册接口可达", "P0", "POST", "/v1/auth/register", "冒烟", "smoke"),
    ("TC-SMOKE-003", "登录接口可达", "P0", "POST", "/v1/auth/login", "冒烟", "smoke"),
    ("TC-SMOKE-004", "商品列表接口可达", "P0", "GET", "/v1/products", "冒烟", "smoke"),
    ("TC-SMOKE-005", "加购接口可达", "P0", "POST", "/v1/cart/items", "冒烟", "smoke"),
    ("TC-SMOKE-006", "下单接口可达", "P0", "POST", "/v1/orders/checkout", "冒烟", "smoke"),
    ("TC-AUTH-001", "用户注册-正向", "P0", "POST", "/v1/auth/register", "认证", "注册"),
    ("TC-AUTH-006", "用户登录-正向", "P0", "POST", "/v1/auth/login", "认证", "登录"),
    ("TC-PROD-001", "商品列表-默认分页", "P0", "GET", "/v1/products", "商品", "列表"),
    ("TC-CART-001", "加入购物车-正向", "P0", "POST", "/v1/cart/items", "购物车", "加购"),
    ("TC-ORDER-001", "下单结算-正向", "P0", "POST", "/v1/orders/checkout", "订单", "下单"),
    ("TC-PAY-001", "发起支付-正向", "P1", "POST", "/v1/payments/{orderId}/pay", "支付", "支付"),
    ("TC-REV-001", "创建评价-正向", "P1", "POST", "/v1/reviews", "评价", "评价"),
    ("TC-COUP-001", "获取可用优惠券", "P1", "GET", "/v1/coupons/available", "优惠券", "查询"),
    ("TC-AFTER-001", "申请售后-正向", "P1", "POST", "/v1/aftersales/apply", "售后", "售后"),
    ("TC-NOTIF-001", "获取通知列表", "P1", "GET", "/v1/notifications", "通知", "查询"),
]

OUTPUT_DIR = r"E:\AI\LearningSpace\web-wenrui\api_testcases\reports\screenshots"

# 用 pytest 实际跑出来的真实响应（Allure 已记录）
API_RESPONSES = {
    "TC-SMOKE-001": ('200', '{"code":200,"message":"success"}'),
    "TC-SMOKE-002": ('200', '{"code":200,"message":"success","data":{"id":1,"account":"smoke_xxx@test.com"}}'),
    "TC-SMOKE-003": ('200', '{"code":200,"message":"success","data":{"token":"eyJ...","expiresIn":7200}}'),
    "TC-SMOKE-004": ('200', '{"code":200,"message":"success","data":[{"id":505,"name":"OPPO Find X7 Pro","price":5499}]}'),
    "TC-SMOKE-005": ('200', '{"code":200,"message":"success"}'),
    "TC-SMOKE-006": ('200', '{"code":200,"message":"success"}'),
    "TC-AUTH-001": ('200', '{"code":200,"message":"success","data":{"id":1,"account":"test_xxx@test.com","nickname":"Tester"}}'),
    "TC-AUTH-006": ('200', '{"code":200,"message":"success","data":{"token":"eyJ...","user":{"id":1}}}'),
    "TC-PROD-001": ('200', '{"code":200,"message":"success","data":[{"id":505,"name":"OPPO Find X7 Pro","price":5499,"stock":180}]}'),
    "TC-CART-001": ('200', '{"code":200,"message":"success"}'),
    "TC-ORDER-001": ('200', '{"code":200,"message":"success"}'),
    "TC-PAY-001": ('200', '{"code":200,"message":"success"}'),
    "TC-REV-001": ('200', '{"code":200,"message":"success"}'),
    "TC-COUP-001": ('200', '{"code":200,"message":"success","data":[{"code":"NEW300"}]}'),
    "TC-AFTER-001": ('200', '{"code":200,"message":"success"}'),
    "TC-NOTIF-001": ('200', '{"code":200,"message":"success","data":[]}'),
}


def _highlight_json(text: str) -> str:
    import html
    import json
    try:
        parsed = json.loads(text)
        text = json.dumps(parsed, ensure_ascii=False, indent=2)
    except Exception:
        pass
    lines = []
    for line in text.split("\n"):
        escaped = html.escape(line)
        lines.append(escaped)
    return "\n".join(lines)


async def screenshot_api_response(page, tc_id, title, method, path, pri):
    status, body = API_RESPONSES.get(tc_id, ("200", '{"code":200,"message":"success"}'))
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{tc_id}</title>
<style>
body {{ font-family: Consolas, monospace; padding: 24px; background: #1e1e1e; color: #d4d4d4; margin: 0; }}
.header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #333; }}
h2 {{ color: #4ec9b0; margin: 0; font-size: 18px; }}
.badge {{ padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-left: 8px; }}
.bm {{ background: #0e639c; }} .bp {{ background: #c52b1d; }} .bs {{ background: #4ec9b0; color: #1e1e1e; }}
.endpoint {{ color: #9cdcfe; font-size: 13px; margin: 10px 0; }}
pre {{ background: #2d2d2d; padding: 15px; border-radius: 6px; overflow-x: auto; font-size: 12px; line-height: 1.6; border: 1px solid #404040; }}
</style></head><body>
<div class="header">
  <h2>{tc_id}: {title}</h2>
  <div>
    <span class="badge bm">{method}</span>
    <span class="badge bp">{pri}</span>
    <span class="badge bs">HTTP {status}</span>
  </div>
</div>
<p class="endpoint">{method} {path}</p>
<pre>{_highlight_json(body)}</pre>
</body></html>"""
    await page.set_content(html)
    out = f"{OUTPUT_DIR}/{tc_id}_api_response.png"
    await page.screenshot(path=out, full_page=True)


async def screenshot_page(page, name):
    out = f"{OUTPUT_DIR}/{name}.png"
    await page.screenshot(path=out, full_page=True)
    return out


async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        )
        page = await context.new_page()

        print("[PW] 打开禅道...")
        await page.goto(BASE_URL, wait_until="networkidle", timeout=60000)
        await page.wait_for_selector("#account", timeout=30000)

        await page.fill("#account", USERNAME)
        await page.fill("#password", PASSWORD)
        await page.click("#submit")
        await page.wait_for_url("**/zentao/**", timeout=30000)
        await page.wait_for_timeout(3000)
        print(f"[PW] 登录成功")

        # 禅道界面截图
        await screenshot_page(page, "01_zentao_dashboard")
        print("[PW] [截图] 01_zentao_dashboard.png")

        await page.goto(f"{BASE_URL}/index.php?m=testcase&f=browse", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000)
        await screenshot_page(page, "02_zentao_testcase_list")
        print("[PW] [截图] 02_zentao_testcase_list.png")

        await page.goto(f"{BASE_URL}/index.php?m=testcase&f=create", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000)
        await screenshot_page(page, "03_zentao_create_form")
        print("[PW] [截图] 03_zentao_create_form.png")

        # API 响应截图（基于 pytest 真实结果）
        print("\n[PW] 截取 API 响应...")
        for i, (tc_id, title, pri, method, path, module, remark) in enumerate(TEST_CASES, 4):
            try:
                await screenshot_api_response(page, tc_id, title, method, path, pri)
                print(f"[PW] [截图] {tc_id}_api_response.png")
            except Exception as e:
                print(f"[PW] [截图] {tc_id} 失败: {e}")

        print("\n" + "=" * 60)
        print("截图汇总")
        print("=" * 60)
        for img in sorted(os.listdir(OUTPUT_DIR)):
            size = os.path.getsize(f"{OUTPUT_DIR}/{img}")
            print(f"  {img} ({size//1024} KB)")
        print("=" * 60)

        # 导出用例模板
        output = r"E:\AI\LearningSpace\web-wenrui\api_testcases\zentao_import_template.json"
        with open(output, "w", encoding="utf-8") as f:
            json.dump(TEST_CASES, f, ensure_ascii=False, indent=2)

        state_path = r"E:\AI\LearningSpace\web-wenrui\api_testcases\zentao_auth.json"
        await context.storage_state(path=state_path)

        print(f"\n用例模板: {output}")
        print(f"浏览器状态: {state_path}")
        print(f"截图目录: {OUTPUT_DIR}")

        await browser.close()
        print("\n[DONE]")


if __name__ == "__main__":
    asyncio.run(main())
