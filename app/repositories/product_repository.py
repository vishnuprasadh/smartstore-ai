from boto3.dynamodb.conditions import Key

from app.core.config import settings
from app.database.dynamodb import get_table


class ProductRepository:

    def __init__(self, table=None):
        self.table = table or get_table(
            settings.products_table_name
        )

    # ------------------------------------------------
    # 1. Retrieve product by barcode
    # ------------------------------------------------

    def get_product(self, code: str):
        response = self.table.get_item(
            Key={"code": code}
        )

        return response.get("Item")

    # ------------------------------------------------
    # 2. Query products by category
    # ------------------------------------------------

    def get_products_by_category(
        self,
        category: str,
        limit: int = 20,
    ):
        response = self.table.query(
            IndexName="gsi-products-by-category",
            KeyConditionExpression=Key(
                "pnns_groups_1_key"
            ).eq(category),
            Limit=limit,
        )

        return response.get("Items", [])

    # ------------------------------------------------
    # 3. Query products by subcategory
    # ------------------------------------------------

    def get_products_by_subcategory(
        self,
        subcategory: str,
        limit: int = 20,
    ):
        response = self.table.query(
            IndexName="gsi-products-by-subcategory",
            KeyConditionExpression=Key(
                "pnns_groups_2_key"
            ).eq(subcategory),
            Limit=limit,
        )

        return response.get("Items", [])

    # ------------------------------------------------
    # 4. Query products by brand
    # ------------------------------------------------

    def get_products_by_brand(
        self,
        brand: str,
        limit: int = 20,
    ):
        response = self.table.query(
            IndexName="gsi-products-by-brand",
            KeyConditionExpression=Key(
                "brands_key"
            ).eq(brand),
            Limit=limit,
        )

        return response.get("Items", [])

    # ------------------------------------------------
    # 5. Product-name prefix search
    # ------------------------------------------------

    def search_products_by_prefix(
        self,
        prefix: str,
        limit: int = 20,
    ):
        response = self.table.scan(
            FilterExpression=Key(
                "product_name_sort"
            ).begins_with(prefix.casefold()),
            Limit=limit,
        )

        return response.get("Items", [])

    def list_products_by_category(
        self,
        category: str,
        page_size: int = 20,
        cursor=None,
    ):
        kwargs = {
            "IndexName": "gsi-products-by-category",
            "KeyConditionExpression": Key(
                "pnns_groups_1_key"
            ).eq(category),
            "Limit": page_size,
        }

        if cursor:
            kwargs["ExclusiveStartKey"] = cursor

        response = self.table.query(**kwargs)

        return {
            "items": response.get("Items", []),
            "next_cursor": response.get("LastEvaluatedKey"),
            "count": response.get("Count", 0),
        }