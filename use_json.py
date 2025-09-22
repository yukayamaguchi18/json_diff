import sqlite3
import json
import os

DB_PATH = "sample.db"
CURRENT_JSON = "current.json"
OUTPUT_JSON = "new.json"

def fetch_from_db(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, discount, image_path FROM products")
    rows = cur.fetchall()
    conn.close()
    return rows

def transform_record(row):
    id_, name, price, discount, image_path = row

    # 値段補完
    if price is None and discount is not None:
        price = round(1000 * (1 - discount), 2)

    # 画像URL変換
    image_url = f"https://example.com{image_path}"

    return {
        "id": id_,
        "name": name,
        "price": price,
        "image_url": image_url
    }

def load_current(path=CURRENT_JSON):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def detect_diff(current, new_records):
    """新規 or 値が変わったレコードを抽出"""
    current_map = {item["id"]: item for item in current}
    diff = []

    for rec in new_records:
        old = current_map.get(rec["id"])
        if old is None:
            # 新規
            diff.append(rec)
        else:
            # 値の差分チェック
            if json.dumps(old, sort_keys=True) != json.dumps(rec, sort_keys=True):
                diff.append(rec)

    return diff

def save_json(data, path=OUTPUT_JSON):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def main():
    db_rows = fetch_from_db()
    transformed = [transform_record(r) for r in db_rows]
    current = load_current()
    diff = detect_diff(current, transformed)

    if diff:
        print(f"{len(diff)} records with changes found. Writing to {OUTPUT_JSON}")
        save_json(diff)
    else:
        print("No differences found.")

# Lambda互換
def lambda_handler(event=None, context=None):
    main()
    return {"status": "done"}

if __name__ == "__main__":
    main()
