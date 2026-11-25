import json
import sys
from pathlib import Path

# IMPORTANT: Add project root BEFORE importing infrastructure.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from infrastructure.dynamodb.products_table import PRODUCTS_TABLE
from infrastructure.dynamodb.stores_table import STORES_TABLE
from infrastructure.dynamodb.item_listings_table import ITEM_LISTINGS_TABLE
from infrastructure.dynamodb.item_listing_history_table import (
    ITEM_LISTING_HISTORY_TABLE,
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "infrastructure"
    / "dynamodb"
    / "local"
    / "definitions"
)

SCHEMAS = [
    PRODUCTS_TABLE,
    STORES_TABLE,
    ITEM_LISTINGS_TABLE,
    ITEM_LISTING_HISTORY_TABLE,
]

TYPE_MAPPING = {
    "STRING": "S",
    "NUMBER": "N",
    "BINARY": "B",
}


def get_attribute_type(schema, attribute_name):
    definitions = {}

    definitions.update(schema.get("source_attributes", {}))
    definitions.update(schema.get("derived_attributes", {}))

    for name, definition in schema.get("attributes", {}).items():
        if isinstance(definition, str):
            definitions[name] = definition

    for key_name in ("partition_key", "sort_key"):
        key = schema.get(key_name)
        if key:
            definitions[key["name"]] = key["type"]

    if attribute_name not in definitions:
        raise ValueError(
            f"Undefined key attribute '{attribute_name}' "
            f"in {schema['table_name']}"
        )

    declared_type = definitions[attribute_name]

    if declared_type not in TYPE_MAPPING:
        raise ValueError(
            f"Unsupported key type '{declared_type}' "
            f"for {attribute_name}"
        )

    return TYPE_MAPPING[declared_type]


def build_table_definition(schema):
    attribute_types = {}

    def register_attribute(name):
        attribute_types[name] = get_attribute_type(schema, name)

    partition_key = schema["partition_key"]
    sort_key = schema.get("sort_key")

    register_attribute(partition_key["name"])

    key_schema = [{
        "AttributeName": partition_key["name"],
        "KeyType": "HASH",
    }]

    if sort_key:
        register_attribute(sort_key["name"])
        key_schema.append({
            "AttributeName": sort_key["name"],
            "KeyType": "RANGE",
        })

    global_secondary_indexes = []

    for index in schema.get("global_secondary_indexes", []):
        index_partition = index["partition_key"]
        index_sort = index.get("sort_key")

        register_attribute(index_partition)

        index_key_schema = [{
            "AttributeName": index_partition,
            "KeyType": "HASH",
        }]

        if index_sort:
            register_attribute(index_sort)
            index_key_schema.append({
                "AttributeName": index_sort,
                "KeyType": "RANGE",
            })

        global_secondary_indexes.append({
            "IndexName": index["name"],
            "KeySchema": index_key_schema,
            "Projection": {
                "ProjectionType": index.get("projection", "ALL")
            },
        })

    definition = {
        "TableName": schema["table_name"],
        "AttributeDefinitions": [
            {
                "AttributeName": name,
                "AttributeType": attribute_type,
            }
            for name, attribute_type in sorted(attribute_types.items())
        ],
        "KeySchema": key_schema,
        "BillingMode": schema.get("billing_mode", "PAY_PER_REQUEST"),
    }

    if global_secondary_indexes:
        definition["GlobalSecondaryIndexes"] = global_secondary_indexes

    return definition


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for schema in SCHEMAS:
        definition = build_table_definition(schema)

        output_file = OUTPUT_DIR / f"{schema['table_name']}.json"

        output_file.write_text(
            json.dumps(definition, indent=2) + "\n"
        )

        print(
            f"{schema['table_name']} | "
            f"Keys: {len(definition['KeySchema'])} | "
            f"GSIs: {len(definition.get('GlobalSecondaryIndexes', []))}"
        )

    print("\nAll four local table definitions generated successfully.")


if __name__ == "__main__":
    main()
