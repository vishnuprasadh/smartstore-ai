"""
Canonical SmartStore Product Table Definition.

Source:
    PackSense India product catalogue.

Principles:
    - Preserve all PackSense source attributes.
    - Keep source fields separate from derived fields.
    - Keep store-level pricing and inventory out of products.
    - Use code as the canonical source identifier.
"""

PRODUCTS_TABLE = {

    # --------------------------------------------------
    # TABLE CONFIGURATION
    # --------------------------------------------------

    "table_name": "products",

    "partition_key": {
        "name": "code",
        "type": "STRING",
    },

    "sort_key": None,

    "billing_mode": "PAY_PER_REQUEST",

    # --------------------------------------------------
    # SOURCE ATTRIBUTES
    # --------------------------------------------------

    "source_attributes": {

        # Product identity
        "code": "STRING",
        "product_name": "STRING",
        "brands": "STRING",

        # Quantity
        "quantity_amount": "NUMBER",
        "quantity_unit": "STRING",
        "product_quantity": "NUMBER",
        "product_quantity_unit": "STRING",

        # Serving
        "serving_amount": "NUMBER",
        "serving_unit": "STRING",

        # Classification
        "pnns_groups_1": "STRING",
        "pnns_groups_2": "STRING",

        # Nutrition metadata
        "nutrition_format": "STRING",
        "nutrition_preparation": "STRING",
        "nutrition_per": "STRING",

        # Nutrition measurements
        "energy_kj": "NUMBER",
        "energy_kcal": "NUMBER",
        "fat": "NUMBER",
        "saturated_fat": "NUMBER",
        "carbohydrates": "NUMBER",
        "sugars": "NUMBER",
        "fiber": "NUMBER",
        "proteins": "NUMBER",
        "salt": "NUMBER",
        "sodium": "NUMBER",

        # Nutrition classifications
        "nutriscore_grade": "STRING",
        "nova_group": "NUMBER",

        # Environmental
        "environmental_score_grade": "STRING",

        # Classification tags
        "categories_tags": "STRING",
        "labels_tags": "STRING",

        # Allergy information
        "allergens_tags": "STRING",
        "traces_tags": "STRING",

        # Source quality indicators
        "open_error_flags": "NUMBER",
        "open_warning_flags": "NUMBER",
        "open_info_flags": "NUMBER",
        "existence_status": "STRING",

        # Source timestamp
        "last_modified_t": "NUMBER",
    },

    # --------------------------------------------------
    # SMARTSTORE DERIVED ATTRIBUTES
    # --------------------------------------------------

    "derived_attributes": {
        "pnns_groups_1_key": "STRING",
        "pnns_groups_2_key": "STRING",
        "brands_key": "STRING",
        "product_name_sort": "STRING",
    },

    # --------------------------------------------------
    # SMARTSTORE OPERATIONAL METADATA
    # --------------------------------------------------

    "metadata_attributes": {
        "source": "STRING",
        "ingested_at": "STRING",
        "updated_at": "STRING",
        "schema_version": "STRING",
    },

    # --------------------------------------------------
    # GLOBAL SECONDARY INDEXES
    # --------------------------------------------------

    "global_secondary_indexes": [

        {
            "name": "gsi-products-by-category",
            "partition_key": "pnns_groups_1_key",
            "sort_key": "product_name_sort",
            "projection": "ALL",
        },

        {
            "name": "gsi-products-by-subcategory",
            "partition_key": "pnns_groups_2_key",
            "sort_key": "product_name_sort",
            "projection": "ALL",
        },

        {
            "name": "gsi-products-by-brand",
            "partition_key": "brands_key",
            "sort_key": "product_name_sort",
            "projection": "ALL",
        },
    ],
}
