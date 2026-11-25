from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from infrastructure.dynamodb.products_table import PRODUCTS_TABLE

DATA_FILE = (
    PROJECT_ROOT
    / "data/raw/packsense/india_products.csv"
)

df = pd.read_csv(DATA_FILE, dtype={"code": str})

numeric_fields = [
    name
    for name, field_type in PRODUCTS_TABLE["source_attributes"].items()
    if field_type == "NUMBER"
]

string_fields = [
    name
    for name, field_type in PRODUCTS_TABLE["source_attributes"].items()
    if field_type == "STRING"
]

print("Records:", len(df))
print("Numeric fields:", len(numeric_fields))
print("String fields:", len(string_fields))

print("\nNUMERIC FIELD VALIDATION")

for field in numeric_fields:
    values = pd.to_numeric(df[field], errors="coerce")
    invalid = df[field].notna() & values.isna()

    print(
        f"{field}: populated={values.notna().sum()}, "
        f"invalid={invalid.sum()}"
    )

    assert invalid.sum() == 0, f"Invalid numeric values in {field}"

print("\nSTRING FIELD VALIDATION")

for field in string_fields:
    non_string = df[field].dropna().map(
        lambda value: not isinstance(value, str)
    )

    assert not non_string.any(), f"Non-string values in {field}"

    print(f"{field}: populated={df[field].notna().sum()}")

print("\nPackSense type validation passed.")