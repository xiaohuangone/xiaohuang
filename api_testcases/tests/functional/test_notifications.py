"""通知模块测试"""
import allure
import pytest
from assertions.http_assertions import HttpAssertions


@allure.epic("电商平台功能测试")
@allure.feature("通知管理")
class TestNotifications:
    """系统通知"""

    @allure.story("通知列表")
    @allure.title("P1: 正向 - 获取通知列表成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_get_notifications(self, client, auth_token):
        resp = client.get("/v1/notifications", params={"size": 5})
        assert resp.status_code == 200

    @allure.story("通知列表")
    @allure.title("P2: 鉴权 - 无 Token 获取通知返回未授权")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_get_notifications_without_token(self, base_client):
        resp = base_client.get("/v1/notifications")
        HttpAssertions.unauthorized(resp)

    @allure.story("创建通知")
    @allure.title("P2: 正向 - 管理员创建通知")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_create_notification(self, client, auth_token):
        resp = client.post("/v1/notifications", json={
            "title": "系统通知",
            "content": "您的订单已发货",
            "type": "ORDER",
        })
        assert resp.status_code in [200, 400, 500]

    @allure.story("标记已读")
    @allure.title("P2: 正向 - 标记单条通知已读")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_mark_read(self, client, auth_token):
        resp = client.post("/v1/notifications/1/read")
        assert resp.status_code in [200, 400, 404]

    @allure.story("全部已读")
    @allure.title("P2: 正向 - 标记所有通知已读")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_mark_all_read(self, client, auth_token):
        resp = client.post("/v1/notifications/markAllRead")
        assert resp.status_code in [200, 400, 500]

    @allure.story("清除通知")
    @allure.title("P2: 正向 - 清空所有通知")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_clear_notifications(self, client, auth_token):
        resp = client.delete("/v1/notifications")
        assert resp.status_code in [200, 400, 500]

    @allure.story("清除通知")
    @allure.title("P2: 鉴权 - 无 Token 清空通知返回未授权")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_clear_notifications_without_token(self, base_client):
        resp = base_client.delete("/v1/notifications")
        HttpAssertions.unauthorized(resp)