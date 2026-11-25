from app.repositories.product_repository import ProductRepository

repository = ProductRepository()

category = "Cereals and potatoes"
page_size = 10

page_number = 1
cursor = None
total_products = 0

while True:
    result = repository.list_products_by_category(
        category=category,
        page_size=page_size,
        cursor=cursor,
    )

    products = result["items"]

    print(
        f"Page {page_number}: "
        f"{len(products)} products"
    )

    total_products += len(products)

    cursor = result["next_cursor"]

    if not cursor:
        break

    page_number += 1

print("\nPagination completed.")
print("Pages retrieved:", page_number)
print("Total products retrieved:", total_products)

assert total_products > 0

print("PASS: Pagination works.")
