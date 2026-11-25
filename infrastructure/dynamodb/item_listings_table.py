"""
SmartStore item listing schema.

An item listing represents one PackSense product
being sold by one store.

Current price and inventory are maintained here.
"""

ITEM_LISTINGS_TABLE = {
    "table_name": "item-listings",

    "partition_key": {
        "name": "storeId",
        "type": "STRING",
    },

    "sort_key": {
        "name": "code",
        "type": "STRING",
    },

    "billing_mode": "PAY_PER_REQUEST",

    "global_secondary_indexes": [
        {
            "name": "gsi-item-listings-by-product",
            "partition_key": "code",
            "sort_key": "storeId",
            "projection": "ALL",
        },
    ],

    "attributes": {
        "sellingPrice": "NUMBER",
        "mrp": "NUMBER",
        "purchasePrice": "NUMBER",
        "currency": "STRING",

        "availableQuantity": "NUMBER",
        "reservedQuantity": "NUMBER",
        "reorderThreshold": "NUMBER",

        "unitOfMeasure": "STRING",
        "listingStatus": "STRING",

        "lastPriceUpdated": "STRING",
        "lastStockUpdated": "STRING",

        "createdAt": "STRING",
        "updatedAt": "STRING",
    },
}
