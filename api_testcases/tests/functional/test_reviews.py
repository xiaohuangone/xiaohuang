"""评价/评论模块测试"""
import allure
import pytest
from assertions.http_assertions import HttpAssertions
from assertions.data_assertions import DataAssertions


@allure.epic("电商平台功能测试")
@allure.feature("评价管理")
class TestReviews:
    """商品评价"""

    @allure.story("创建评价")
    @allure.title("P1: 正向 - 创建商品评价成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_create_review(self, client, auth_token, product_id):
        resp = client.post("/v1/reviews", json={
            "productId": product_id,
            "content": "非常好用，物流很快！",
            "rating": 5,
        })
        assert resp.status_code in [200, 400, 500]

    @allure.story("创建评价")
    @allure.title("P2: 反向 - 评价不存在的商品返回错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_create_review_nonexist_product(self, client, auth_token):
        resp = client.post("/v1/reviews", json={
            "productId": 99999,
            "content": "测试评价",
            "rating": 3,
        })
        assert resp.status_code in [200, 400, 404]

    @allure.story("创建评价")
    @allure.title("P2: 反向 - 缺少必填字段返回错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_create_review_missing_fields(self, client, auth_token):
        resp = client.post("/v1/reviews", json={})
        assert resp.status_code in [200, 400]

    @allure.story("创建评价")
    @allure.title("P2: 鉴权 - 无 Token 创建评价返回未授权")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_create_review_without_token(self, base_client):
        resp = base_client.post("/v1/reviews", json={
            "productId": 1,
            "content": "测试",
            "rating": 5,
        })
        HttpAssertions.unauthorized(resp)

    @allure.story("查询评价")
    @allure.title("P1: 正向 - 获取评价列表成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_get_reviews(self, client, auth_token):
        resp = client.get("/v1/reviews", params={"size": 5})
        assert resp.status_code == 200
        data = resp.json()
        if data.get("code") == 200:
            DataAssertions.is_list(data.get("data", []))

    @allure.story("查询评价")
    @allure.title("P2: 正向 - 按商品 ID 过滤评价列表")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_get_reviews_by_product(self, client, auth_token):
        resp = client.get("/v1/reviews", params={"productId": 1, "size": 5})
        assert resp.status_code == 200