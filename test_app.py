import pytest
from unittest.mock import patch, MagicMock
from app import app 


@pytest.fixture
def client():
    """Create a fresh test client with an empty inventory before each test."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        # Reset shared state before every test
        import app as app_module
        app_module.inventory.clear()
        app_module.next_inventory_id = 0
        yield client


@pytest.fixture
def seeded_client(client):
    """Client with two items already in the inventory."""
    client.post("/inventory", json={"name": "Milk",  "price": 1.99, "stock": 10})
    client.post("/inventory", json={"name": "Bread", "price": 2.49, "stock": 5})
    return client


# ── GET /inventory ─────────────────────────────────────────────────────────────

class TestGetInventory:

    def test_returns_empty_list_when_no_items(self, client):
        res = client.get("/inventory")
        assert res.status_code == 200
        assert res.get_json() == []

    def test_returns_all_items(self, seeded_client):
        res = seeded_client.get("/inventory")
        assert res.status_code == 200
        assert len(res.get_json()) == 2

    def test_response_is_json(self, client):
        res = client.get("/inventory")
        assert res.content_type == "application/json"


# ── GET /inventory/<id> ────────────────────────────────────────────────────────

class TestGetInventoryItem:

    def test_returns_correct_item(self, seeded_client):
        res = seeded_client.get("/inventory/0")
        assert res.status_code == 200
        assert res.get_json()["name"] == "Milk"

    def test_returns_404_for_missing_item(self, client):
        res = client.get("/inventory/999")
        assert res.status_code == 404

    def test_returns_correct_fields(self, seeded_client):
        data = seeded_client.get("/inventory/0").get_json()
        assert "id" in data
        assert "name" in data
        assert "price" in data
        assert "stock" in data


# ── POST /inventory ────────────────────────────────────────────────────────────

class TestAddInventoryItem:

    def test_adds_item_successfully(self, client):
        res = client.post("/inventory", json={"name": "Eggs", "price": 3.00, "stock": 20})
        assert res.status_code == 201
        assert res.get_json()["name"] == "Eggs"

    def test_returns_400_when_name_missing(self, client):
        res = client.post("/inventory", json={"price": 1.50, "stock": 10})
        assert res.status_code == 400

    def test_returns_400_when_body_empty(self, client):
        res = client.post("/inventory", json=None)
        assert res.status_code == 400

    def test_id_increments_across_items(self, client):
        res1 = client.post("/inventory", json={"name": "A", "price": 1.0, "stock": 1})
        res2 = client.post("/inventory", json={"name": "B", "price": 2.0, "stock": 2})
        assert res1.get_json()["id"] == 0
        assert res2.get_json()["id"] == 1

    def test_defaults_price_to_zero(self, client):
        res = client.post("/inventory", json={"name": "Freebie"})
        assert res.get_json()["price"] == 0.0

    def test_defaults_stock_to_zero(self, client):
        res = client.post("/inventory", json={"name": "Freebie"})
        assert res.get_json()["stock"] == 0

    def test_barcode_triggers_api_fetch(self, client):
        mock_return = {"name": "Test Product", "brand": "BrandX", "category": "Snacks"}
        with patch("app.fetch_external_data", return_value=mock_return) as mock_fetch:
            res = client.post("/inventory", json={"name": "Crisps", "price": 1.0, "stock": 5, "barcode": "1234567890"})
            mock_fetch.assert_called_once_with("1234567890", search_by="barcode")
            assert res.get_json()["api_details"]["brand"] == "BrandX"

    def test_no_api_details_when_barcode_absent(self, client):
        res = client.post("/inventory", json={"name": "NoBarcode", "price": 1.0, "stock": 1})
        assert "api_details" not in res.get_json()

    def test_no_api_details_when_fetch_returns_none(self, client):
        with patch("app.fetch_external_data", return_value=None):
            res = client.post("/inventory", json={"name": "Unknown", "price": 1.0, "stock": 1, "barcode": "0000000000"})
            assert "api_details" not in res.get_json()


# ── PATCH /inventory/<id> ──────────────────────────────────────────────────────

class TestUpdateInventoryItem:

    def test_updates_price(self, seeded_client):
        res = seeded_client.patch("/inventory/0", json={"price": 9.99})
        assert res.status_code == 200
        assert res.get_json()["price"] == 9.99

    def test_updates_stock(self, seeded_client):
        res = seeded_client.patch("/inventory/0", json={"stock": 42})
        assert res.status_code == 200
        assert res.get_json()["stock"] == 42

    def test_updates_name(self, seeded_client):
        res = seeded_client.patch("/inventory/0", json={"name": "Oat Milk"})
        assert res.status_code == 200
        assert res.get_json()["name"] == "Oat Milk"

    def test_partial_update_leaves_other_fields_unchanged(self, seeded_client):
        seeded_client.patch("/inventory/0", json={"price": 5.00})
        res = seeded_client.get("/inventory/0")
        data = res.get_json()
        assert data["name"] == "Milk"   # unchanged
        assert data["stock"] == 10      # unchanged
        assert data["price"] == 5.00    # updated

    def test_returns_404_for_missing_item(self, client):
        res = client.patch("/inventory/999", json={"price": 1.0})
        assert res.status_code == 404

    def test_returns_400_when_body_empty(self, seeded_client):
        res = seeded_client.patch("/inventory/0", json=None)
        assert res.status_code == 400


# ── DELETE /inventory/<id> ─────────────────────────────────────────────────────

class TestDeleteInventoryItem:

    def test_deletes_existing_item(self, seeded_client):
        res = seeded_client.delete("/inventory/0")
        assert res.status_code == 204
        # Confirm it's actually gone
        assert seeded_client.get("/inventory/0").status_code == 404

    def test_returns_404_for_missing_item(self, client):
        res = client.delete("/inventory/999")
        assert res.status_code == 404

    def test_inventory_shrinks_after_delete(self, seeded_client):
        seeded_client.delete("/inventory/0")
        res = seeded_client.get("/inventory")
        assert len(res.get_json()) == 1


# ── fetch_external_data ────────────────────────────────────────────────────────

class TestFetchExternalData:
    """Unit tests for the helper — mocks requests.get so no real HTTP calls are made."""

    def _make_mock_response(self, json_data):
        mock_resp = MagicMock()
        mock_resp.json.return_value = json_data
        return mock_resp

    def test_barcode_search_returns_product_details(self):
        from app import fetch_external_data
        payload = {
            "status": 1,
            "product": {"product_name": "Cola", "brands": "BrandX", "categories": "Drinks"}
        }
        with patch("app.requests.get", return_value=self._make_mock_response(payload)):
            result = fetch_external_data("123", search_by="barcode")
        assert result["name"] == "Cola"
        assert result["brand"] == "BrandX"
        assert result["category"] == "Drinks"

    def test_barcode_search_returns_none_when_status_not_1(self):
        from app import fetch_external_data
        with patch("app.requests.get", return_value=self._make_mock_response({"status": 0})):
            assert fetch_external_data("bad_barcode", search_by="barcode") is None

    def test_name_search_returns_first_product(self):
        from app import fetch_external_data
        payload = {
            "products": [{"product_name": "Bread", "brands": "BakeCo", "categories": "Bakery"}]
        }
        with patch("app.requests.get", return_value=self._make_mock_response(payload)):
            result = fetch_external_data("bread", search_by="name")
        assert result["name"] == "Bread"

    def test_name_search_returns_none_when_no_products(self):
        from app import fetch_external_data
        with patch("app.requests.get", return_value=self._make_mock_response({"products": []})):
            assert fetch_external_data("xyz", search_by="name") is None

    def test_returns_none_on_request_exception(self):
        import requests as req
        from app import fetch_external_data
        with patch("app.requests.get", side_effect=req.RequestException):
            assert fetch_external_data("123", search_by="barcode") is None