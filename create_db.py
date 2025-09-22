import sqlite3
import argparse
from faker import Faker
import random

def init_db(n=10, db_path="sample.db"):
    fake = Faker()

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS products")
    cur.execute("""
    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        price REAL,
        discount REAL,
        image_path TEXT
    )
    """)

    for i in range(1, n + 1):
        name = fake.word().title()
        # 値段をランダムに欠損させる
        price = None if i % 5 == 0 else round(random.uniform(500, 5000), 2)
        # 割引をランダムに入れる
        discount = round(random.uniform(0, 0.3), 2) if price is None else None
        image_path = f"/images/{name.lower()}.png"

        cur.execute(
            "INSERT INTO products (id, name, price, discount, image_path) VALUES (?, ?, ?, ?, ?)",
            (i, name, price, discount, image_path)
        )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=10, help="Number of records to insert")
    args = parser.parse_args()

    init_db(n=args.n)
    print(f"Database created with {args.n} records.")
