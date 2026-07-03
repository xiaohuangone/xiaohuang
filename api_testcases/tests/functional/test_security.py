"""安全测试：XSS、SQL注入、边界值"""
import allure
import pytest
from assertions.http_assertions import HttpAssertions


@allure.epic("电商平台安全测试")
@allure.feature("输入安全")
class TestXSS:
    """XSS 跨站脚本"""

    @allure.story("XSS 防护")
    @allure.title("P3: 安全 - 商品搜索含 XSS 脚本不报错")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P3
    @pytest.mark.security
    def test_search_xss(self, client, auth_token):
        resp = client.get("/v1/products", params={
            "keyword": "<script>alert('xss')</script>"
        })
        HttpAssertions.ok(resp)

    @allure.story("XSS 防护")
    @allure.title("P3: 安全 - 注册账号含 XSS 脚本")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P3
    @pytest.mark.security
    def test_register_xss(self, client):
        from helpers.data_factory import DataFactory
        resp = client.post("/v1/auth/register", json={
            "account": f"xss_{DataFactory.random_string(4)}@test.com",
            "password": "Test@123",
            "nickname": "<img src=x onerror=alert(1)>",
        })
        assert resp.status_code in [200, 400]

    @allure.story("XSS 防护")
    @allure.title("P3: 安全 - 评价内容含 XSS 脚本")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P3
    @pytest.mark.security
    def test_review_xss(self, client, auth_token, product_id):
        resp = client.post("/v1/reviews", json={
            "productId": product_id,
            "content": "<script>alert('xss')</script>",
            "rating": 1,
        })
        assert resp.status_code in [200, 400, 500]


@allure.epic("电商平台安全测试")
@allure.feature("输入安全")
class TestSQLInjection:
    """SQL 注入防护"""

    @allure.story("SQL 注入防护")
    @allure.title("P3: 安全 - 商品搜索含 SQL 注入语句")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P3
    @pytest.mark.security
    def test_search_sql_injection(self, client, auth_token):
        payloads = [
            "' OR '1'='1",
            "1; DROP TABLE products",
            "' UNION SELECT * FROM users --",
            "1' AND 1=1 --",
        ]
        for payload in payloads:
            resp = client.get("/v1/products", params={"keyword": payload})
            HttpAssertions.ok(resp)

    @allure.story("SQL 注入防护")
    @allure.title("P3: 安全 - 登录接口 SQL 注入")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P3
    @pytest.mark.security
    def test_login_sql_injection(self, client):
        resp = client.post("/v1/auth/login", json={
            "account": "' OR '1'='1",
            "password": "' OR '1'='1",
        })
        assert resp.status_code in [200, 400]


@allure.epic("电商平台安全测试")
@allure.feature("边界与压力")
class TestBoundary:
    """边界值测试"""

    @allure.story("边界值")
    @allure.title("P3: 边界 - 超长关键字搜索")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P3
    def test_long_keyword(self, client, auth_token):
        long_keyword = "A" * 5000
        resp = client.get("/v1/products", params={"keyword": long_keyword})
        assert resp.status_code in [200, 400, 414]

    @allure.story("边界值")
    @allure.title("P3: 边界 - 超大分页参数")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P3
    def test_extreme_pagination(self, client, auth_token):
        resp = client.get("/v1/products", params={"page": 999999, "size": 1000})
        assert resp.status_code == 200

    @allure.story("边界值")
    @allure.title("P3: 边界 - 注册超长密码")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P3
    def test_long_password(self, client):
        from helpers.data_factory import DataFactory
        long_pwd = "A" * 200
        resp = client.post("/v1/auth/register", json={
            "account": f"longpwd_{DataFactory.random_string(4)}@test.com",
            "password": long_pwd,
            "nickname": "LongPwdTest",
        })
        assert resp.status_code in [200, 400]

    @allure.story("边界值")
    @allure.title("P3: 边界 - 商品数量为超大值")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P3
    def test_cart_max_quantity(self, client, auth_token, product_id):
        resp = client.post("/v1/cart/items", json={
            "productId": product_id,
            "quantity": 99999,
        })
        assert resp.status_code in [200, 400]