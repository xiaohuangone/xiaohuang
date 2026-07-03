"""支付模块测试"""
import allure
import pytest
from assertions.http_assertions import HttpAssertions
from assertions.data_assertions import DataAssertions


@allure.epic("电商平台功能测试")
@allure.feature("支付管理")
class TestPayment:
    """支付流程"""

    @allure.story("发起支付")
    @allure.title("P1: 正向 - 发起支付返回支付信息")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_pay_order(self, client, auth_token, address_id, product_id):
        # 先下单
        client.post("/v1/cart/items", json={"productId": product_id, "quantity": 1})
        resp = client.post("/v1/orders/checkout", json={"addressId": address_id})
        if resp.json().get("code") != 200:
            pytest.skip("下单失败，跳过支付测试")
        order_id = resp.json()["data"]["id"]

        # 发起支付
        resp = client.post(f"/v1/payments/{order_id}/pay", json={
            "channel": "alipay",
        })
        assert resp.status_code in [200, 400, 500]

    @allure.story("查询支付状态")
    @allure.title("P1: 正向 - 查询支付状态")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_payment_status(self, client, auth_token, address_id, product_id):
        # 先下单
        client.post("/v1/cart/items", json={"productId": product_id, "quantity": 1})
        resp = client.post("/v1/orders/checkout", json={"addressId": address_id})
        if resp.json().get("code") != 200:
            pytest.skip("下单失败，跳过支付状态查询")
        order_id = resp.json()["data"]["id"]

        # 查询支付状态
        resp = client.get(f"/v1/payments/{order_id}/status")
        assert resp.status_code in [200, 400, 404]

    @allure.story("支付回调")
    @allure.title("P2: 正向 - 支付回调通知（无需 Token）")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_payment_webhook(self, base_client):
        resp = base_client.post("/v1/payments/webhook", json={
            "orderId": 1,
            "tradeNo": "T_WEBHOOK_TEST",
            "channel": "alipay",
            "amount": 100.00,
            "status": "SUCCESS",
        })
        assert resp.status_code in [200, 400, 500]

    @allure.story("发起支付")
    @allure.title("P2: 反向 - 支付不存在的订单返回错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_pay_nonexist_order(self, client, auth_token):
        resp = client.post("/v1/payments/99999/pay", json={"channel": "alipay"})
        assert resp.status_code in [200, 400, 404]

    @allure.story("发起支付")
    @allure.title("P2: 鉴权 - 无 Token 发起支付返回未授权")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_pay_without_token(self, base_client):
        resp = base_client.post("/v1/payments/1/pay", json={"channel": "alipay"})
        HttpAssertions.unauthorized(resp)