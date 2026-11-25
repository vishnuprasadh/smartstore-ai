import argparse
import sys
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

import boto3
import pandas as pd

# Resolve project root before importing project modules.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from infrastructure.dynamodb.products_table import PRODUCTS_TABLE


CSV_PATH = PROJECT_ROOT / "data/raw/packsense/india_products.csv"
DYNAMODB_ENDPOINT = "http://localhost:8001"
AWS_REGION = "ap-south-1"
TABLE_NAME = PRODUCTS_TABLE["table_name"]

SOURCE_ATTRIBUTES = PRODUCTS_TABLE["source_attributes"]
DERIVED_ATTRIBUTES = PRODUCTS_TABLE["derived_attributes"]
METADATA_ATTRIBUTES = PRODUCTS_TABLE["metadata_attributes"]

SCHEMA_VERSION = "1.0"
SOURCE_NAME = "PackSense India"


def create_dynamodb_resource():
    return boto3.resource(
        "dynamodb",
        endpoint_url=DYNAMODB_ENDPOINT,
        region_name=AWS_REGION,
        aws_access_key_id="local",
        aws_secret_access_key="local",
    )


def is_missing(value):
    return value is None or str(value).strip() == ""


def convert_source_value(attribute, value, attribute_type):
    """Convert CSV values according to the authoritative DynamoDB schema."""

    if is_missing(value):
        return None

    if attribute_type == "STRING":
        # Preserve the original source string.
        return str(value)

    if attribute_type == "NUMBER":
        try:
            # Decimal avoids floating-point precision loss.
            return Decimal(str(value).strip())
        except InvalidOperation as exc:
            raise ValueError(
                f"Invalid numeric value for {attribute}: {value!r}"
            ) from exc

    raise ValueError(
        f"Unsupported schema type {attribute_type!r} for {attribute}"
    )


def make_index_key(value):
    """Normalize a source value for a derived GSI partition key."""

    if is_missing(value):
        return None

    normalized = str(value).strip()

    if normalized.casefold() == "unknown":
        return None

    return normalized


def build_product_item(row, ingested_at):
    item = {}

    # 1. Preserve all original source attributes.
    for attribute, attribute_type in SOURCE_ATTRIBUTES.items():
        value = convert_source_value(
            attribute,
            row.get(attribute, ""),
            attribute_type,
        )
        if value is not None:
            item[attribute] = value

    # 2. Validate the primary key.
    if not item.get("code"):
        raise ValueError("Product record has no barcode/code")

    # 3. Always generate the GSI sort key.
    # Use the product name when available; otherwise use its barcode.
    product_name = item.get("product_name")

    if product_name and product_name.strip():
        item["product_name_sort"] = product_name.strip().casefold()
    else:
        item["product_name_sort"] = item["code"]

    # 4. Generate GSI partition keys independently.
    category = make_index_key(item.get("pnns_groups_1"))
    subcategory = make_index_key(item.get("pnns_groups_2"))
    brand = make_index_key(item.get("brands"))

    if category:
        item["pnns_groups_1_key"] = category

    if subcategory:
        item["pnns_groups_2_key"] = subcategory

    if brand:
        item["brands_key"] = brand

    # 5. Add ingestion metadata.
    item["source"] = SOURCE_NAME
    item["ingested_at"] = ingested_at
    item["updated_at"] = ingested_at
    item["schema_version"] = SCHEMA_VERSION

    return item


def main():
    parser = argparse.ArgumentParser(
        description="Ingest PackSense India products into DynamoDB Local."
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually write records. Without this flag, only performs a dry run.",
    )
    args = parser.parse_args()

    print(f"Reading dataset: {CSV_PATH}")

    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {CSV_PATH}")

    # Read every column as text to preserve barcodes and source strings.
    df = pd.read_csv(
        CSV_PATH,
        dtype=str,
        keep_default_na=False,
        na_filter=False,
    )

    print(f"Rows found: {len(df)}")
    print(f"Columns found: {len(df.columns)}")

    # Validate source columns against the authoritative schema.
    expected_columns = set(SOURCE_ATTRIBUTES)
    actual_columns = set(df.columns)

    missing_columns = expected_columns - actual_columns
    unexpected_columns = actual_columns - expected_columns

    if missing_columns:
        raise ValueError(f"Missing source columns: {sorted(missing_columns)}")

    if unexpected_columns:
        raise ValueError(
            f"Unexpected source columns: {sorted(unexpected_columns)}"
        )

    # Prevent accidental overwrites from duplicate barcodes.
    if df["code"].str.strip().eq("").any():
        raise ValueError("Dataset contains empty product codes")

    if df["code"].duplicated().any():
        raise ValueError("Duplicate product codes detected; ingestion stopped")

    ingested_at = datetime.now(timezone.utc).isoformat()

    print("\nBuilding and validating product records...")

    items = []
    for row in df.to_dict(orient="records"):
        items.append(build_product_item(row, ingested_at))

    print(f"Validated records: {len(items)}")
    print(f"Unique product codes: {len({item['code'] for item in items})}")

    # Report derived-index coverage.
    print("\nDerived GSI key coverage:")
    for attribute in DERIVED_ATTRIBUTES:
        count = sum(1 for item in items if attribute in item)
        print(f"  {attribute}: {count}")

    # Report numeric attribute conversion.
    numeric_attributes = [
        name
        for name, attribute_type in SOURCE_ATTRIBUTES.items()
        if attribute_type == "NUMBER"
    ]
    decimal_count = sum(
        1
        for item in items
        for attribute in numeric_attributes
        if isinstance(item.get(attribute), Decimal)
    )
    print(f"\nNumeric values converted to Decimal: {decimal_count}")

    print("\nSample product:")
    sample = items[0]
    for key in ("code", "product_name", "brands",
                "pnns_groups_1", "pnns_groups_1_key",
                "product_name_sort", "energy_kcal"):
        print(f"  {key}: {sample.get(key)!r}")

    if not args.execute:
        print("\nDRY RUN COMPLETE. No DynamoDB records were written.")
        print("Review the output, then rerun with --execute to ingest.")
        return

    dynamodb = create_dynamodb_resource()
    table = dynamodb.Table(TABLE_NAME)

    print(f"\nWriting {len(items)} records to DynamoDB table: {TABLE_NAME}")

    written = 0

    # DynamoDB batch_writer automatically handles batches of up to 25 items
    # and retries unprocessed items.
    with table.batch_writer(overwrite_by_pkeys=["code"]) as batch:
        for item in items:
            batch.put_item(Item=item)
            written += 1

            if written % 2500 == 0:
                print(f"  Submitted {written} records...")

    print(f"\nIngestion write completed: {written} records submitted.")

    # Verify actual stored record count using a paginated scan.
    response = table.scan(Select="COUNT")
    stored_count = response["Count"]

    while "LastEvaluatedKey" in response:
        response = table.scan(
            Select="COUNT",
            ExclusiveStartKey=response["LastEvaluatedKey"],
        )
        stored_count += response["Count"]

    print(f"Records found in DynamoDB: {stored_count}")

    if stored_count != len(items):
        raise RuntimeError(
            f"Record count mismatch: expected {len(items)}, found {stored_count}"
        )

    print("\nSUCCESS: PackSense ingestion and count validation passed.")


if __name__ == "__main__":
    main()
