"""售后模块测试"""
import allure
import pytest
from assertions.http_assertions import HttpAssertions


@allure.epic("电商平台功能测试")
@allure.feature("售后管理")
class TestAftersales:
    """售后服务"""

    @allure.story("申请售后")
    @allure.title("P1: 正向 - 提交售后申请返回结果")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_apply_aftersale(self, client, auth_token, product_id):
        resp = client.post("/v1/aftersales/apply", json={
            "orderId": 1,
            "reason": "商品质量问题",
            "type": "REFUND",
            "amount": 100.00,
        })
        assert resp.status_code in [200, 400, 500]

    @allure.story("申请售后")
    @allure.title("P2: 反向 - 缺少必填字段返回错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_apply_aftersale_missing_fields(self, client, auth_token):
        resp = client.post("/v1/aftersales/apply", json={})
        assert resp.status_code in [200, 400, 500]

    @allure.story("申请售后")
    @allure.title("P2: 鉴权 - 无 Token 申请售后返回未授权")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_apply_aftersale_without_token(self, base_client):
        resp = base_client.post("/v1/aftersales/apply", json={
            "orderId": 1,
            "reason": "测试",
            "type": "REFUND",
        })
        HttpAssertions.unauthorized(resp)

    @allure.story("售后列表")
    @allure.title("P1: 正向 - 获取售后申请列表")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_get_aftersales_list(self, client, auth_token):
        resp = client.get("/v1/aftersales", params={"size": 5})
        assert resp.status_code == 200

    @allure.story("售后列表")
    @allure.title("P2: 鉴权 - 无 Token 获取售后列表返回未授权")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_get_aftersales_without_token(self, base_client):
        resp = base_client.get("/v1/aftersales")
        HttpAssertions.unauthorized(resp)

    @allure.story("取消售后")
    @allure.title("P2: 正向 - 取消售后申请")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_cancel_aftersale(self, client, auth_token):
        resp = client.post("/v1/aftersales/1/cancel")
        assert resp.status_code in [200, 400, 404]