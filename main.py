import time
import use_json
import use_pandas

def main():
    # 標準ライブラリ版
    start = time.time()
    use_json.main()
    end = time.time()
    print(f"標準ライブラリ版処理時間: {end - start:.4f} 秒")

    # pandas版
    start = time.time()
    use_pandas.main()
    end = time.time()
    print(f"pandas版処理時間: {end - start:.4f} 秒")

if __name__ == "__main__":
    main()