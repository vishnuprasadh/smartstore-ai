import boto3
from boto3.dynamodb.conditions import Key

ENDPOINT = "http://localhost:8001"
REGION = "ap-south-1"
TABLE_NAME = "products"

dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url=ENDPOINT,
    region_name=REGION,
    aws_access_key_id="local",
    aws_secret_access_key="local",
)

table = dynamodb.Table(TABLE_NAME)

# --------------------------------------------------
# TEST 1: Direct lookup using a leading-zero barcode
# --------------------------------------------------

print("\nTEST 1: GetItem by barcode")

barcode = "0000000000000"

response = table.get_item(Key={"code": barcode})
product = response.get("Item")

assert product is not None, f"Product {barcode} not found"
assert product["code"] == barcode

print("PASS: Product retrieved")
print("Barcode:", product["code"])
print("Barcode type:", type(product["code"]).__name__)
print("Product name:", product.get("product_name"))
print("Source:", product.get("source"))

# --------------------------------------------------
# Find a representative record for each GSI.
# --------------------------------------------------

def find_index_sample(partition_key):
    scan_kwargs = {
        "ProjectionExpression": "#pk, #sk, #code",
        "ExpressionAttributeNames": {
            "#pk": partition_key,
            "#sk": "product_name_sort",
            "#code": "code",
        },
        "Limit": 100,
    }

    while True:
        response = table.scan(**scan_kwargs)

        for item in response.get("Items", []):
            if partition_key in item and "product_name_sort" in item:
                return item

        if "LastEvaluatedKey" not in response:
            return None

        scan_kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]


# --------------------------------------------------
# TEST 2-4: Query all three GSIs
# --------------------------------------------------

indexes = [
    ("gsi-products-by-category", "pnns_groups_1_key"),
    ("gsi-products-by-subcategory", "pnns_groups_2_key"),
    ("gsi-products-by-brand", "brands_key"),
]

for index_name, partition_key in indexes:
    print(f"\nTEST: {index_name}")

    sample = find_index_sample(partition_key)

    assert sample is not None, (
        f"No representative record found for {partition_key}"
    )

    index_value = sample[partition_key]

    response = table.query(
        IndexName=index_name,
        KeyConditionExpression=Key(partition_key).eq(index_value),
        Limit=5,
    )

    results = response.get("Items", [])

    assert results, f"No results returned from {index_name}"

    print("PASS: GSI query successful")
    print("Index value:", index_value)
    print("Products returned:", len(results))
    print("Sample product code:", results[0]["code"])
    print("Sample product name:", results[0].get("product_name"))

print("\nALL PRODUCT RETRIEVAL AND GSI TESTS PASSED.")
