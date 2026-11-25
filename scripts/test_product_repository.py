from unittest.mock import Mock

from app.repositories.product_repository import ProductRepository


def test_get_product():
    mock_table = Mock()

    mock_table.get_item.return_value = {
        "Item": {
            "code": "8906005611352",
            "product_name": "Mini Toast",
        }
    }

    repository = ProductRepository(table=mock_table)

    result = repository.get_product("8906005611352")

    assert result["code"] == "8906005611352"
    assert result["product_name"] == "Mini Toast"

    mock_table.get_item.assert_called_once_with(
        Key={"code": "8906005611352"}
    )


def test_get_products_by_category():
    mock_table = Mock()

    mock_table.query.return_value = {
        "Items": [
            {
                "code": "00002316",
                "product_name": "Sample Product",
            }
        ]
    }

    repository = ProductRepository(table=mock_table)

    result = repository.get_products_by_category(
        "Cereals and potatoes"
    )

    assert len(result) == 1
    assert result[0]["code"] == "00002316"

    mock_table.query.assert_called_once()


def test_get_products_by_brand():
    mock_table = Mock()

    mock_table.query.return_value = {
        "Items": [
            {
                "code": "8906005611352",
                "product_name": "Mini Toast",
            }
        ]
    }

    repository = ProductRepository(table=mock_table)

    result = repository.get_products_by_brand("Lite Bite")

    assert len(result) == 1
    assert result[0]["product_name"] == "Mini Toast"

    mock_table.query.assert_called_once()