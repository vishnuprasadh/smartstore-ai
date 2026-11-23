import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.schemas.product import Product

client = TestClient(app)


# ---------------------------------------------------------------------------
# Product schema tests
# ---------------------------------------------------------------------------

class TestProductSchema:
    def test_valid_product(self):
        p = Product(id="P1001", name="iPhone 17", price=79900, currency="INR")
        assert p.id == "P1001"
        assert p.name == "iPhone 17"
        assert p.price == 79900
        assert p.currency == "INR"

    def test_currency_normalised_to_uppercase(self):
        p = Product(id="P1002", name="Pixel 9", price=59999, currency="inr")
        assert p.currency == "INR"

    def test_currency_whitespace_stripped(self):
        p = Product(id="P1003", name="Galaxy S25", price=74999, currency="  USD  ")
        assert p.currency == "USD"

    def test_currency_defaults_to_inr(self):
        p = Product(id="P1004", name="MacBook Air", price=99900)
        assert p.currency == "INR"

    def test_all_allowed_currencies_accepted(self):
        for ccy in ("INR", "USD", "GBP", "SGD"):
            p = Product(id="P1005", name="Test", price=100, currency=ccy)
            assert p.currency == ccy

    def test_unsupported_currency_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            Product(id="P1006", name="Test", price=100, currency="EUR")
        assert "Unsupported Currency Value" in str(exc_info.value)

    def test_price_must_be_positive(self):
        with pytest.raises(ValidationError):
            Product(id="P1007", name="Test", price=0, currency="INR")

    def test_negative_price_raises(self):
        with pytest.raises(ValidationError):
            Product(id="P1008", name="Test", price=-1, currency="INR")

    def test_empty_id_raises(self):
        with pytest.raises(ValidationError):
            Product(id="", name="Test", price=100, currency="INR")

    def test_empty_name_raises(self):
        with pytest.raises(ValidationError):
            Product(id="P1009", name="", price=100, currency="INR")

    def test_missing_id_raises(self):
        with pytest.raises(ValidationError):
            Product(name="Test", price=100, currency="INR")

    def test_missing_name_raises(self):
        with pytest.raises(ValidationError):
            Product(id="P1010", price=100, currency="INR")

    def test_missing_price_raises(self):
        with pytest.raises(ValidationError):
            Product(id="P1011", name="Test", currency="INR")

    def test_get_allowed_currencies_returns_expected_set(self):
        allowed = Product.get_allowedcurrencies()
        assert allowed == {"INR", "USD", "GBP", "SGD"}


# ---------------------------------------------------------------------------
# GET /products endpoint tests
# ---------------------------------------------------------------------------

class TestGetProductsEndpoint:
    def test_returns_200(self):
        response = client.get("/products")
        assert response.status_code == 200

    def test_returns_list(self):
        response = client.get("/products")
        data = response.json()
        assert isinstance(data, list)

    def test_returns_non_empty_list(self):
        response = client.get("/products")
        assert len(response.json()) > 0

    def test_each_product_has_required_fields(self):
        response = client.get("/products")
        for product in response.json():
            assert "id" in product
            assert "name" in product
            assert "price" in product
            assert "currency" in product

    def test_product_ids_are_unique(self):
        response = client.get("/products")
        ids = [p["id"] for p in response.json()]
        assert len(ids) == len(set(ids))

    def test_all_prices_are_positive(self):
        response = client.get("/products")
        for product in response.json():
            assert float(product["price"]) > 0

    def test_all_currencies_are_valid(self):
        allowed = Product.get_allowedcurrencies()
        response = client.get("/products")
        for product in response.json():
            assert product["currency"] in allowed

    def test_response_conforms_to_product_schema(self):
        response = client.get("/products")
        for item in response.json():
            # Pydantic will raise if any field is invalid
            Product(**item)

    def test_known_product_iphone_present(self):
        response = client.get("/products")
        names = [p["name"] for p in response.json()]
        assert "iPhone 17" in names

    def test_known_product_macbook_present(self):
        response = client.get("/products")
        names = [p["name"] for p in response.json()]
        assert "MacBook Air" in names
