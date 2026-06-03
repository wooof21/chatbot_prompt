import re
from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from sqlalchemy.dialects.postgresql import insert

from app.models import Product, Store, Inventory, CustomerSearch
from app.utils import calculate_final_price, format_price


NO_AREA_VALUES = {"", "all", "anywhere", "any"}

STOP_WORDS = {
    "do", "you", "have", "the", "a", "an", "in", "near", "for",
    "what", "about", "is", "are", "any", "with", "of",
}

PRODUCT_NAME_REMOVE_PATTERNS = [
    r"\bsize\s+\w+\b",
    r"\b\d+\s*gb\b",
    r"\b\d+\s*tb\b",
    r"\bblack\b",
    r"\bwhite\b",
    r"\bblue\b",
    r"\bpink\b",
    r"\bgray\b",
    r"\bgrey\b",
    r"\bred\b",
    r"\bgreen\b",
    r"\byellow\b",
    r"\bsilver\b",
    r"\bgold\b",
]

ATTRIBUTE_MATCH_TYPE = {
    "size": "exact",
    "storage_size": "exact",
    "capacity": "exact",
    "gender": "exact",
    "sport_type": "exact",

    "color": "partial",
    "material": "partial",
    "shade": "partial",
    "brand": "partial",
    "model": "partial",
    "author": "partial",
}

ATTRIBUTE_FILTER_KEYS = {
    "size",
    "color",
    "storage_size",
    "shade",
    "material",
    "model",
}


def normalize(value: str | None) -> str | None:
    if value is None:
        return None
    return value.strip().lower()

r'''
Remove attributes from product names:

black size 10 nike shoes -> nike shoes
    * r"\bsize\s+\w+\b" -> size 10, size XL, size 42
    * r"\b\d+\s*gb\b" -> 256 GB, 512GB, 128 gb
    * r"\b\d+\s*tb\b" -> 1TB, 2 TB
    * color match -> remove
'''
def clean_product_name(product_name: str) -> str:
    cleaned = product_name.strip()

    for pattern in PRODUCT_NAME_REMOVE_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

    return " ".join(cleaned.split())

'''
Break product name into searchable keywords.

Input: "Nike Air Max Shoes"
Output: ["Nike", "Air", "Max", "Shoes"]

Stop words are removed:
    - do you have nike shoes -> ["nike", "shoes"]
'''
def product_tokens(product_name: str) -> list[str]:
    '''
    list comprehension
    syntax:
        [
            expression
            for item in iterable
            if condition
        ]

    equivalent to:

        result = []

        for token in re.findall(r"[a-zA-Z0-9']+", product_name):
            if token.lower() not in stop_words:
                result.append(token.lower())

        return result
    '''
    return [
        token.lower()
        for token in re.findall(r"[a-zA-Z0-9']+", product_name)
        if token.lower() not in STOP_WORDS
    ]


def get_condition(attributes: dict[str, Any]) -> str:
    if attributes.get("open_boxed"):
        return "OPEN BOX"
    if attributes.get("refurbished"):
        return "REFURBISHED"
    if attributes.get("used"):
        return "USED"
    if attributes.get("clearance"):
        return "CLEARANCE"
    if attributes.get("display_model"):
        return "DISPLAY MODEL"
    if attributes.get("floor_model"):
        return "FLOOR MODEL"

    return "NEW"


def has_meaningful_attribute(value: Any) -> bool:
    return value not in [None, "", False]


def has_attribute_filters(attributes: dict[str, Any]) -> bool:
    return any(key in attributes for key in ATTRIBUTE_FILTER_KEYS)

# Track which product customer searched
def record_customer_search(
    db: Session,
    product_name: str,
    area: str | None,
    product_status: str,
) -> None:
    normalized_product = normalize(product_name)
    normalized_area = normalize(area)

    # insert product
    stmt = insert(CustomerSearch).values(
        searched_product_name=product_name,
        normalized_product_name=normalized_product,
        area=area,
        normalized_area=normalized_area,
        product_status=product_status,
        search_count=1,
    )

    # upsert: if record exist (nike shoes + downtown), search_count += 1
    stmt = stmt.on_conflict_do_update(
        constraint="uq_customer_search_product_area",
        set_={
            "searched_product_name": product_name,
            "area": area,
            "product_status": product_status,
            "search_count": CustomerSearch.search_count + 1,
            "last_searched_at": func.now(),
        },
    )

    db.execute(stmt)
    db.commit()


def apply_area_filter(query, area: str | None):
    # add area filter
    if area and area.strip().lower() not in NO_AREA_VALUES:
        return query.filter(func.lower(Store.area).like(f"%{area.lower()}%"))

    return query


def apply_product_filter(query, db: Session, product_name: str):
    # find exact match product first
    exact_product = (
        db.query(Product)
        .filter(func.lower(Product.name) == product_name.lower())
        .first()
    )

    # if exact match found, filter by product id
    if exact_product:
        return query.filter(Product.id == exact_product.id), exact_product

    # if no exact match, generate search tokens
    tokens = product_tokens(product_name)

    '''
    OR query:
        SQL:
            WHERE
            name LIKE '%nike%'
            OR name LIKE '%running%'
            OR name LIKE '%shoes%'
    '''
    if tokens:
        query = query.filter(
            and_(
                *[
                    func.lower(Product.name).like(f"%{token}%")
                    for token in tokens
                ]
            )
        )

    return query, None


def apply_attribute_filters(query, attributes: dict[str, Any]):
    for key, value in attributes.items():
        if not has_meaningful_attribute(value):
            continue

        '''
        attributes:
            {
              "size":"10",
              "color":"black"
            }
        -> PostgreSQL JSON Operators:
            AND attributes->>'size' = '%10%'
            AND attributes->>'color' = '%black%'

        e.g
        A table has a JSONB column: {"size":"10","color":"black"}
            * PostgreSQL provides operators to access JSON fields.
            * ->: return JSON
                * attributes->'size': result "10" (JSON)
            * ->>: return text
                * attributes->>'size': result 10 (plain text) 
            * Find rows whose JSON size field contains 10.

        ATTRIBUTE_MATCH_TYPE: 
            - some attributes like size, capacity should be exact match
                * dont want 1 to match 10, 110 ...
            - other attributes can do partial match
                * use ilike(): case insensitive match

        '''
        value = str(value).strip()
        match_type = ATTRIBUTE_MATCH_TYPE.get(key, "partial")

        if match_type == "exact":
            query = query.filter(
                func.lower(Inventory.attributes[key].as_string()) == value.lower()
            )
        else:
            query = query.filter(
                Inventory.attributes[key].as_string().ilike(f"%{value}%")
            )

    return query


def base_inventory_query(db: Session):
    # query individual columns
    return (
        db.query(
            Product.name.label("product_name"),
            Product.product_type.label("product_type"),
            Product.base_price.label("base_price"),
            Store.name.label("store_name"),
            Store.area.label("area"),
            Store.address.label("address"),
            Inventory.quantity.label("quantity"),
            Inventory.attributes.label("attributes"),
        )
        # join Inventory and Store into Product
        .join(Inventory, Inventory.product_id == Product.id)
        .join(Store, Store.id == Inventory.store_id)
        .filter(Inventory.quantity > 0)
    )


def build_product_results_with_attribute_filter(
    rows,
    exact_product: bool,
    include_price: bool,
    include_attributes: bool,
) -> list[dict]:
    results = []

    for row in rows:
        attrs = row.attributes or {}

        item = {
            "product_name": row.product_name,
            "store_name": row.store_name,
            "area": row.area,
            "address": row.address,
            "quantity": row.quantity,
            "exact_match": exact_product,
        }

        if include_attributes:
            item["attributes"] = attrs

        if include_price:
            final_price = calculate_final_price(
                base_price=row.base_price,
                product_type=row.product_type,
                attributes=attrs,
            )

            item["condition"] = get_condition(attrs)
            item["base_price_cents"] = row.base_price
            item["final_price_cents"] = final_price
            item["base_price"] = format_price(row.base_price)
            item["final_price"] = format_price(final_price)

        results.append(item)

    return sorted(results, key=lambda x: x["quantity"], reverse=True)

# aggregate total quantity if product in same store
def aggregate_products_results_without_filter(
    rows,
    exact_product: bool,
    include_price: bool,
    include_attributes: bool,
) -> list[dict]:
    grouped = {}

    for row in rows:
        key = (
            row.product_name,
            row.store_name,
            row.area,
            row.address,
        )

        attrs = row.attributes or {}

        if key not in grouped:
            grouped[key] = {
                "product_name": row.product_name,
                "store_name": row.store_name,
                "area": row.area,
                "address": row.address,
                "quantity": 0,
                "exact_match": exact_product,
            }

            if include_attributes:
                grouped[key]["attributes"] = []

            if include_price:
                grouped[key]["prices"] = []

        grouped[key]["quantity"] += row.quantity

        if include_attributes:
            grouped[key]["attributes"].append(attrs)

        if include_price:
            final_price = calculate_final_price(
                base_price=row.base_price,
                product_type=row.product_type,
                attributes=attrs,
            )

            grouped[key]["prices"].append(
                {
                    "condition": get_condition(attrs),
                    "quantity": row.quantity,
                    "base_price_cents": row.base_price,
                    "final_price_cents": final_price,
                    "base_price": format_price(row.base_price),
                    "final_price": format_price(final_price),
                }
            )

    return sorted(grouped.values(), key=lambda x: x["quantity"], reverse=True)


'''
Search DB:
search_inventory(
    db,
    product_name="Nike Shoes",
    area="Downtown",
    attributes={
        "size":"10",
        "color":"black"
    },
    include_price=True
)

'''
def search_inventory(
    db: Session,
    product_name: str,
    area: str | None = None,
    attributes: dict | None = None,
    limit: int = 10,
    include_attributes: bool = False,
    include_price: bool = False,
) -> list[dict]:
    attributes = attributes or {}
    limit = max(3, min(limit, 10))

    original_product_name = product_name
    cleaned_product_name = clean_product_name(product_name)

    print("PRODUCT:", product_name)
    print("ATTRIBUTES:", attributes)

    '''
    db.query(Product): query the entire model, return <product object>

    query individual columns: only query by provided columns, return <Row object> = [Row(), Row()]
    '''

    query = base_inventory_query(db)
    query = apply_area_filter(query, area)
    query, exact_product = apply_product_filter(query, db, cleaned_product_name)
    query = apply_attribute_filters(query, attributes)

    rows = query.order_by(desc(Inventory.quantity)).limit(limit).all()

    product_status = "EXISTING_PRODUCT" if rows else "NO_STOCK"

    record_customer_search(
        db=db,
        product_name=original_product_name,
        area=area,
        product_status=product_status,
    )

    if has_attribute_filters(attributes):
        return build_product_results_with_attribute_filter(
            rows=rows,
            exact_product=bool(exact_product),
            include_price=include_price,
            include_attributes=include_attributes,
        )

    return aggregate_products_results_without_filter(
        rows=rows,
        exact_product=bool(exact_product),
        include_price=include_price,
        include_attributes=include_attributes,
    )