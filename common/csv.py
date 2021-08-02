# import datetime
from pathlib import Path

from common.common import hyphen_now

dir = Path("./csv")
dir.mkdir(parents=True, exist_ok=True)
CSV_FILE_PATH = "./csv/{searchword}_{datetime}_data.csv"


# CSV書き込み
def write_csv(search_word, df):
    # csvファイル名に検索ワードを加える。
    csv_path = CSV_FILE_PATH.format(searchword=search_word, datetime=hyphen_now())
    # 行番号なしで出力
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
