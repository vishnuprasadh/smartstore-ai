"""
SmartStore store master schema.

One record represents one physical retail store.
Store-specific product pricing and inventory are maintained
in item_listings, not in this table.
"""

STORES_TABLE = {
    "table_name": "stores",

    "partition_key": {
        "name": "storeId",
        "type": "STRING",
    },

    "sort_key": None,

    "billing_mode": "PAY_PER_REQUEST",

    "global_secondary_indexes": [],

    "attributes": {
        "storeName": "STRING",
        "ownerId": "STRING",
        "phoneNumber": "STRING",

        "address": {
            "type": "MAP",
            "fields": {
                "addressLine1": "STRING",
                "addressLine2": "STRING",
                "area": "STRING",
                "city": "STRING",
                "state": "STRING",
                "postalCode": "STRING",
                "country": "STRING",
            },
        },

        "latitude": "NUMBER",
        "longitude": "NUMBER",
        "storeType": "STRING",
        "status": "STRING",
        "createdAt": "STRING",
        "updatedAt": "STRING",
    },
}
