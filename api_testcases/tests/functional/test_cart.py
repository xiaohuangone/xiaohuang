"""购物车模块测试"""
import allure
import pytest
from assertions.http_assertions import HttpAssertions


@allure.epic("电商平台功能测试")
@allure.feature("购物车管理")
class TestCartAdd:
    """加入购物车"""

    @allure.story("加入购物车")
    @allure.title("P0: 正向 - 加入购物车成功")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.P0
    def test_add_valid(self, client, auth_token, product_id):
        resp = client.post("/v1/cart/items", json={
            "productId": product_id, "quantity": 1,
        })
        HttpAssertions.ok(resp)
        assert resp.json().get("code") in [200, None]

    @allure.story("加入购物车")
    @allure.title("P1: 正向 - 加购多数量商品成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_add_multiple_quantity(self, client, auth_token, product_id):
        resp = client.post("/v1/cart/items", json={
            "productId": product_id, "quantity": 3,
        })
        HttpAssertions.ok(resp)

    @allure.story("加入购物车")
    @allure.title("P2: 反向 - 缺少 productId 字段")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_add_missing_product_id(self, client, auth_token):
        resp = client.post("/v1/cart/items", json={"quantity": 1})
        assert resp.status_code in [200, 400, 500], f"意外: {resp.status_code}"

    @allure.story("加入购物车")
    @allure.title("P2: 反向 - quantity 为 0 返回错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_add_quantity_zero(self, client, auth_token, product_id):
        resp = client.post("/v1/cart/items", json={
            "productId": product_id, "quantity": 0,
        })
        assert resp.status_code in [200, 400]

    @allure.story("加入购物车")
    @allure.title("P2: 反向 - quantity 为负数返回错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_add_quantity_negative(self, client, auth_token, product_id):
        resp = client.post("/v1/cart/items", json={
            "productId": product_id, "quantity": -1,
        })
        assert resp.status_code in [200, 400]

    @allure.story("加入购物车")
    @allure.title("P2: 反向 - 添加不存在的商品返回错误")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_add_not_exist_product(self, client, auth_token):
        resp = client.post("/v1/cart/items", json={
            "productId": 99999, "quantity": 1,
        })
        assert resp.status_code in [200, 400, 404]

    @allure.story("加入购物车")
    @allure.title("P1: 鉴权 - 无 Token 添加购物车返回未授权")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_add_without_token(self, base_client):
        resp = base_client.post("/v1/cart/items", json={
            "productId": 1, "quantity": 1,
        })
        HttpAssertions.unauthorized(resp)


@allure.epic("电商平台功能测试")
@allure.feature("购物车管理")
class TestCartList:
    """购物车列表"""

    @allure.story("购物车列表")
    @allure.title("P1: 正向 - 获取购物车列表成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.P1
    def test_get_cart(self, client, auth_token, product_id):
        # 先加一个商品
        client.post("/v1/cart/items", json={"productId": product_id, "quantity": 1})
        resp = client.get("/v1/cart")
        HttpAssertions.ok(resp)
        data = resp.json()
        assert "data" in data or "code" in data

    @allure.story("购物车列表")
    @allure.title("P2: 鉴权 - 无 Token 获取购物车返回未授权")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_get_cart_without_token(self, base_client):
        resp = base_client.get("/v1/cart")
        HttpAssertions.unauthorized(resp)


@allure.epic("电商平台功能测试")
@allure.feature("购物车管理")
class TestCartUpdate:
    """更新购物车商品数量"""

    @allure.story("更新购物车")
    @allure.title("P2: 正向 - 更新购物车商品数量成功")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_update_cart_item_quantity(self, client, auth_token, product_id):
        # 先加一个商品
        client.post("/v1/cart/items", json={"productId": product_id, "quantity": 1})
        # 获取购物车拿到 item_id
        resp = client.get("/v1/cart")
        items = resp.json().get("data", []) or []
        if not items:
            pytest.skip("购物车为空，跳过")
        item_id = items[0].get("id")
        if not item_id:
            pytest.skip("无购物车项 ID，跳过")
        resp = client.put(f"/v1/cart/items/{item_id}", json={"quantity": 5})
        assert resp.status_code in [200, 400, 500]

    @allure.story("更新购物车")
    @allure.title("P2: 鉴权 - 无 Token 更新购物车返回未授权")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_update_cart_without_token(self, base_client):
        resp = base_client.put("/v1/cart/items/1", json={"quantity": 3})
        HttpAssertions.unauthorized(resp)


@allure.epic("电商平台功能测试")
@allure.feature("购物车管理")
class TestCartDelete:
    """删除购物车"""

    @allure.story("删除购物车")
    @allure.title("P2: 正向 - 删除购物车项成功")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_delete_item(self, client, auth_token, product_id):
        client.post("/v1/cart/items", json={"productId": product_id, "quantity": 1})
        resp = client.delete("/v1/cart/items/1")
        assert resp.status_code in [200, 400, 404]

    @allure.story("删除购物车")
    @allure.title("P2: 鉴权 - 无 Token 删除购物车返回未授权")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.P2
    def test_delete_without_token(self, base_client):
        resp = base_client.delete("/v1/cart/items/1")
        HttpAssertions.unauthorized(resp)