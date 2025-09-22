import sqlite3
import pandas as pd
import os

DB_PATH = "sample.db"
CURRENT_JSON = "current.json"
OUTPUT_JSON = "new.json"

def fetch_from_db(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(
        "SELECT id, name, price, discount, image_path FROM products", conn
    )
    conn.close()
    return df

def transform(df: pd.DataFrame) -> pd.DataFrame:
    # 値段補完
    df["price"] = df.apply(
        lambda r: round(1000 * (1 - r["discount"]), 2) if pd.isna(r["price"]) and pd.notna(r["discount"]) else r["price"],
        axis=1
    )

    # 画像URL変換
    df["image_url"] = "https://example.com" + df["image_path"].astype(str)

    # 出力カラムだけに絞る
    return df[["id", "name", "price", "image_url"]]

def load_current(path=CURRENT_JSON) -> pd.DataFrame:
    if not os.path.exists(path):
        return pd.DataFrame(columns=["id", "name", "price", "image_url"])
    return pd.read_json(path, orient="records")

def save_json(df: pd.DataFrame, path=OUTPUT_JSON):
    df.to_json(path, orient="records", indent=2, force_ascii=False)

def main():
    df = fetch_from_db()
    transformed = transform(df)
    save_json(transformed)

    current = load_current()
    if current.empty:
        print(f"{len(transformed)} records found. Writing to {OUTPUT_JSON}")
    else:
        # 差分チェック
        merged = transformed.merge(current, on="id", how="left", suffixes=("", "_old"))
        changed_count = 0
        for _, row in merged.iterrows():
            if pd.isna(row.get("name_old")):
                changed_count += 1
            else:
                old = {c: row[f"{c}_old"] for c in ["name", "price", "image_url"]}
                new = {c: row[c] for c in ["name", "price", "image_url"]}
                if old != new:
                    changed_count += 1

        if changed_count:
            print(f"{changed_count} records with changes found. Writing to {OUTPUT_JSON}")
        else:
            print("No differences found.")

def lambda_handler(event=None, context=None):
    main()
    return {"status": "done"}

if __name__ == "__main__":
    main()
