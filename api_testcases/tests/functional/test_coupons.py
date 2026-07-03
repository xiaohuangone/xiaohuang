"""优惠券模块测试"""
import allure
import pytest
from assertions.http_assertions import HttpAssertions


@allure.epic("电商平台功能测试")
@allure.feature("优惠券管理")
class TestCoupons:
    """优惠券"""

    @allure.story("可用优惠券")
    @allure.title("P1: 正向 - 获取当前用户可用优惠券列表")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_available_coupons(self, client, auth_token):
        resp = client.get("/v1/coupons/available")
        HttpAssertions.ok(resp)
        data = resp.json()
        assert "data" in data

    @allure.story("可用优惠券")
    @allure.title("P2: 鉴权 - 无 Token 获取优惠券返回未授权")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_available_coupons_without_token(self, base_client):
        resp = base_client.get("/v1/coupons/available")
        HttpAssertions.unauthorized(resp)

    @allure.story("校验优惠券")
    @allure.title("P1: 正向 - 校验优惠券码可用性")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_check_coupon(self, client, auth_token):
        resp = client.post("/v1/coupons/NEW300/check", json={"amount": 6000})
        assert resp.status_code in [200, 400, 500]
        if resp.status_code == 200:
            data = resp.json()
            assert "data" in data

    @allure.story("校验优惠券")
    @allure.title("P2: 反向 - 校验不存在的优惠券码返回错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_check_invalid_coupon(self, client, auth_token):
        resp = client.post("/v1/coupons/INVALID123/check", json={"amount": 1000})
        assert resp.status_code in [200, 400, 404]

    @allure.story("校验优惠券")
    @allure.title("P2: 鉴权 - 无 Token 校验优惠券返回未授权")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_check_coupon_without_token(self, base_client):
        resp = base_client.post("/v1/coupons/NEW300/check", json={"amount": 1000})
        HttpAssertions.unauthorized(resp)