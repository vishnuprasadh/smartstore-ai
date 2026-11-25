"""
SmartStore item listing history schema.

Records price and inventory changes for each
store-product relationship.

The history is append-only at the application level.
"""

ITEM_LISTING_HISTORY_TABLE = {
    "table_name": "item-listing-history",

    "partition_key": {
        "name": "listingId",
        "type": "STRING",
    },

    "sort_key": {
        "name": "eventKey",
        "type": "STRING",
    },

    "billing_mode": "PAY_PER_REQUEST",

    "global_secondary_indexes": [],

    "attributes": {
        "storeId": "STRING",
        "code": "STRING",

        "eventType": "STRING",

        "oldPrice": "NUMBER",
        "newPrice": "NUMBER",

        "oldQuantity": "NUMBER",
        "newQuantity": "NUMBER",
        "quantityChanged": "NUMBER",

        "source": "STRING",
        "createdAt": "STRING",
    },
}
