
import sys
from pathlib import Path

import aws_cdk as cdk
from aws_cdk.assertions import Template

# Make the SmartStore project root available for imports.
PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))

from infrastructure.dynamodb.products_table import PRODUCTS_TABLE
from infrastructure.dynamodb.stores_table import STORES_TABLE
from infrastructure.dynamodb.item_listings_table import ITEM_LISTINGS_TABLE
from infrastructure.dynamodb.item_listing_history_table import (
    ITEM_LISTING_HISTORY_TABLE,
)

from cdk.cdk_stack import SmartStoreStack


SCHEMAS = [
    PRODUCTS_TABLE,
    STORES_TABLE,
    ITEM_LISTINGS_TABLE,
    ITEM_LISTING_HISTORY_TABLE,
]


EXPECTED_TABLES = {
    "products-dev": 3,
    "stores-dev": 0,
    "item-listings-dev": 1,
    "item-listing-history-dev": 0,
}


EXPECTED_KEYS = {
    "products-dev": [
        {"AttributeName": "code", "KeyType": "HASH"}
    ],
    "stores-dev": [
        {"AttributeName": "storeId", "KeyType": "HASH"}
    ],
    "item-listings-dev": [
        {"AttributeName": "storeId", "KeyType": "HASH"},
        {"AttributeName": "code", "KeyType": "RANGE"},
    ],
    "item-listing-history-dev": [
        {"AttributeName": "listingId", "KeyType": "HASH"},
        {"AttributeName": "eventKey", "KeyType": "RANGE"},
    ],
}


def build_template(stage):
    app = cdk.App()

    stack = SmartStoreStack(
        app,
        f"SmartStore-{stage}",
        stage=stage,
        schemas=SCHEMAS,
    )

    return Template.from_stack(stack).to_json()


def get_tables(template):
    return {
        logical_id: resource
        for logical_id, resource in template["Resources"].items()
        if resource["Type"] == "AWS::DynamoDB::Table"
    }


def test_dev_creates_exactly_four_tables():
    template = build_template("dev")
    tables = get_tables(template)

    assert len(tables) == 4

    actual_names = {
        resource["Properties"]["TableName"]
        for resource in tables.values()
    }

    assert actual_names == set(EXPECTED_TABLES.keys())


def test_dev_table_indexes():
    template = build_template("dev")
    tables = get_tables(template)

    for resource in tables.values():
        props = resource["Properties"]
        table_name = props["TableName"]

        indexes = props.get("GlobalSecondaryIndexes", [])

        assert len(indexes) == EXPECTED_TABLES[table_name]


def test_dev_primary_keys():
    template = build_template("dev")
    tables = get_tables(template)

    for resource in tables.values():
        props = resource["Properties"]
        table_name = props["TableName"]

        assert props["KeySchema"] == EXPECTED_KEYS[table_name]


def test_dev_billing_encryption_and_protection():
    template = build_template("dev")
    tables = get_tables(template)

    for resource in tables.values():
        props = resource["Properties"]

        assert props["BillingMode"] == "PAY_PER_REQUEST"
        assert props["SSESpecification"]["SSEEnabled"] is True
        assert props["DeletionProtectionEnabled"] is False

        assert (
            props["PointInTimeRecoverySpecification"]
            ["PointInTimeRecoveryEnabled"]
            is False
        )

        assert resource["DeletionPolicy"] == "Delete"
        assert resource["UpdateReplacePolicy"] == "Delete"


def test_prod_has_backup_and_deletion_protection():
    template = build_template("prod")
    tables = get_tables(template)

    assert len(tables) == 4

    for resource in tables.values():
        props = resource["Properties"]

        assert props["DeletionProtectionEnabled"] is True

        pitr = props["PointInTimeRecoverySpecification"]

        assert pitr["PointInTimeRecoveryEnabled"] is True
        assert pitr["RecoveryPeriodInDays"] == 35

        assert resource["DeletionPolicy"] == "Retain"
        assert resource["UpdateReplacePolicy"] == "Retain"
