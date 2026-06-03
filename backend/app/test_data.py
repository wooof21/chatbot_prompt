from app.database import Base, engine, SessionLocal
from app.models import Product, Store, Inventory

Base.metadata.create_all(bind=engine)

db = SessionLocal()

db.query(Inventory).delete()
db.query(Product).delete()
db.query(Store).delete()

products = [
    Product(
        name="Nike Air Max Shoes",
        product_type="shoes",
        description="Running shoes",
        base_price=16999,
    ),
    Product(
        name="Nike Air Min Shoes",
        product_type="shoes",
        description="Running shoes",
        base_price=13999,
    ),
    Product(
        name="Nike Running Shoes",
        product_type="shoes",
        description="Lightweight running shoes",
        base_price=13999,
    ),
    Product(
        name="Adidas Hoodie",
        product_type="clothing",
        description="Cotton hoodie",
        base_price=7999,
    ),
    Product(
        name="Nike Hoodie",
        product_type="clothing",
        description="Cotton hoodie",
        base_price=7999,
    ),
    Product(
        name="Levi's 501 Jeans",
        product_type="clothing",
        description="Classic jeans",
        base_price=8999,
    ),
    Product(
        name="Levi's 301 Jeans",
        product_type="clothing",
        description="Classic jeans",
        base_price=5999,
    ),
    Product(
        name="Levi's 601 Jeans",
        product_type="clothing",
        description="Classic jeans",
        base_price=9999,
    ),
    Product(
        name="Apple iPhone 15",
        product_type="electronics",
        description="Smartphone",
        base_price=112900,
    ),
    Product(
        name="Apple iPhone 16",
        product_type="electronics",
        description="Smartphone",
        base_price=132900,
    ),
    Product(
        name="Apple AirPods Pro",
        product_type="electronics",
        description="Wireless earbuds",
        base_price=32900,
    ),
    Product(
        name="IKEA Office Chair",
        product_type="furniture",
        description="Office chair",
        base_price=14999,
    ),
    Product(
        name="Maybelline Foundation",
        product_type="beauty",
        description="Liquid foundation",
        base_price=1599,
    ),
    Product(
        name="Wilson Tennis Racket",
        product_type="sports",
        description="Adult tennis racket",
        base_price=12999,
    ),
    Product(
        name="Harry Potter Paperback",
        product_type="books",
        description="Paperback book",
        base_price=1599,
    ),
    Product(
        name="Dyson Vacuum Cleaner",
        product_type="appliances",
        description="Cordless vacuum cleaner",
        base_price=59999,
    ),
    Product(
        name="DeWalt Cordless Drill",
        product_type="tools",
        description="Power drill",
        base_price=19999,
    ),
    Product(
        name="LEGO City Police Set",
        product_type="toys",
        description="Kids building toy",
        base_price=6999,
    ),
]

stores = [
    Store(name="Downtown Flagship", area="Downtown", address="100 Queen St W, Toronto, ON"),
    Store(name="Eaton Centre Store", area="Downtown", address="220 Yonge St, Toronto, ON"),
    Store(name="King West Store", area="Downtown", address="500 King St W, Toronto, ON"),
    Store(name="North York Centre", area="North York", address="5150 Yonge St, Toronto, ON"),
    Store(name="Scarborough Town", area="Scarborough", address="300 Borough Dr, Toronto, ON"),
    Store(name="Yorkdale Store", area="Yorkdale", address="3401 Dufferin St, Toronto, ON"),
]

db.add_all(products + stores)
db.commit()

products = db.query(Product).all()
stores = db.query(Store).all()

product_by_name = {p.name: p for p in products}
store_by_name = {s.name: s for s in stores}

inventory = [
    ("Nike Air Max Shoes", "Downtown Flagship", 24, {"size": "10", "color": "Black"}),
    ("Nike Air Max Shoes", "Eaton Centre Store", 18, {"size": "10", "color": "White", "last_season": True}),
    ("Nike Air Max Shoes", "King West Store", 7, {"size": "9", "color": "Black", "display_model": True}),
    ("Nike Air Min Shoes", "North York Centre", 5, {"size": "11", "color": "Red"}),

    ("Adidas Hoodie", "Downtown Flagship", 12, {"size": "M", "color": "Black"}),
    ("Adidas Hoodie", "Eaton Centre Store", 9, {"size": "M", "color": "Blue", "clearance": True}),
    ("Nike Hoodie", "Yorkdale Store", 4, {"size": "L", "color": "Black", "minor_defect": True}),

    ("Levi's 501 Jeans", "Downtown Flagship", 14, {"size": "32", "color": "Blue"}),
    ("Levi's 501 Jeans", "Downtown Flagship", 22, {"size": "32", "color": "Pink"}),
    ("Levi's 501 Jeans", "Eaton Centre Store", 17, {"size": "33", "color": "Brown"}),
    ("Levi's 301 Jeans", "Eaton Centre Store", 11, {"size": "34", "color": "Blue", "clearance": True}),
    ("Levi's 601 Jeans", "Scarborough Town", 8, {"size": "40", "color": "Black", "clearance": True}),

    ("Apple iPhone 15", "Downtown Flagship", 20, {"storage_size": "128GB", "color": "Black"}),
    ("Apple iPhone 15", "Eaton Centre Store", 16, {"storage_size": "256GB", "color": "Blue", "open_boxed": True}),
    ("Apple iPhone 15", "King West Store", 8, {"storage_size": "128GB", "color": "Pink", "refurbished": True}),
    ("Apple iPhone 16", "Yorkdale Store", 9, {"storage_size": "128GB", "color": "Glod"}),

    ("Apple AirPods Pro", "Downtown Flagship", 30, {}),
    ("Apple AirPods Pro", "King West Store", 9, {"open_boxed": True}),

    ("IKEA Office Chair", "Downtown Flagship", 6, {"color": "Black", "material": "Mesh"}),
    ("IKEA Office Chair", "North York Centre", 10, {"color": "Gray", "material": "Fabric", "floor_model": True}),
    ("IKEA Office Chair", "Eaton Centre Store", 3, {"color": "Black", "material": "Mesh", "scratch_and_dent": True}),

    ("Maybelline Foundation", "Downtown Flagship", 13, {"shade": "Natural Beige", "skin_type": "Normal"}),
    ("Maybelline Foundation", "Eaton Centre Store", 8, {"shade": "Ivory", "skin_type": "Dry", "clearance": True}),

    ("Wilson Tennis Racket", "Downtown Flagship", 9, {"sport_type": "tennis", "grip_size": "4 3/8"}),
    ("Wilson Tennis Racket", "Yorkdale Store", 5, {"sport_type": "tennis", "clearance": True}),

    ("Harry Potter Paperback", "Eaton Centre Store", 22, {"format": "paperback", "used": False}),
    ("Harry Potter Paperback", "North York Centre", 8, {"format": "paperback", "used": True}),

    ("Dyson Vacuum Cleaner", "Downtown Flagship", 7, {"model": "V11", "open_boxed": True}),
    ("Dyson Vacuum Cleaner", "Scarborough Town", 4, {"model": "V10", "refurbished": True}),

    ("DeWalt Cordless Drill", "King West Store", 10, {"power_type": "battery", "model": "DCD771"}),
    ("DeWalt Cordless Drill", "Yorkdale Store", 6, {"power_type": "battery", "refurbished": True}),

    ("LEGO City Police Set", "Downtown Flagship", 13, {"age_range": "6+", "battery_required": False}),
    ("LEGO City Police Set", "Eaton Centre Store", 11, {"age_range": "6+", "battery_required": False}),
]

for product_name, store_name, qty, attrs in inventory:
    db.add(
        Inventory(
            product_id=product_by_name[product_name].id,
            store_id=store_by_name[store_name].id,
            quantity=qty,
            attributes=attrs,
        )
    )

db.commit()
db.close()

print("Seed data inserted.")