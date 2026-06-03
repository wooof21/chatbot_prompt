import re

def calculate_final_price(base_price: int, product_type: str, attributes: dict) -> int:
    discount = 0

    if product_type == "electronics":
        if attributes.get("open_boxed") is True:
            discount += 0.10
        if attributes.get("refurbished") is True:
            discount += 0.20

    elif product_type == "shoes":
        if attributes.get("last_season") is True:
            discount += 0.15
        if attributes.get("display_model") is True:
            discount += 0.10

    elif product_type == "clothing":
        if attributes.get("clearance") is True:
            discount += 0.25
        if attributes.get("minor_defect") is True:
            discount += 0.15

    elif product_type == "furniture":
        if attributes.get("floor_model") is True:
            discount += 0.20
        if attributes.get("scratch_and_dent") is True:
            discount += 0.30

    elif product_type == "beauty":
        if attributes.get("clearance") is True:
            discount += 0.20

    elif product_type == "books":
        if attributes.get("used") is True:
            discount += 0.30

    elif product_type == "sports":
        if attributes.get("clearance") is True:
            discount += 0.20

    elif product_type == "appliances":
        if attributes.get("open_boxed") is True:
            discount += 0.10
        if attributes.get("refurbished") is True:
            discount += 0.25

    elif product_type == "tools":
        if attributes.get("refurbished") is True:
            discount += 0.20

    discount = min(discount, 0.50)
    return int(base_price * (1 - discount))


def format_price(cents: int) -> str:
    return f"${cents / 100:.2f}"

def clean_product_name(product_name: str) -> str:
    cleaned = product_name.strip()

    patterns = [
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
    ]

    for pattern in patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

    return " ".join(cleaned.split())