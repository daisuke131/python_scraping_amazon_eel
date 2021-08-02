# import math
from concurrent.futures import ThreadPoolExecutor
from time import sleep

import eel
import pandas as pd

from common.csv import write_csv
from common.driver import driver_setting
from common.log import log_setting

# from bs4 import BeautifulSoup


THREAD_COUNT = None  # スレッド数Noneで自動
SEARCH_QUERY_URL = "https://www.amazon.co.jp/s?k={query_word}"
PAGE_QUERY_URL = SEARCH_QUERY_URL + "&page={page_count}"

log = log_setting()


class Scraping:
    def __init__(self, search_word) -> None:
        self.search_words: str
        self.query_word: str
        self.page_count = 0
        self.df = pd.DataFrame()
        self.df_list = []
        self.search_word_formating(search_word)
        self.all_data_count = 0

    def search_word_formating(self, search_word: str) -> None:
        # クエリパラメータの形に整形
        self.search_words = search_word.split()
        query_words = []
        for word in self.search_words:
            query_words.append(word)
        self.query_word = "+".join(query_words)
        log.info(f"検索ワード：{self.search_words}")

    def fetch_page_count(self) -> None:
        query_url = SEARCH_QUERY_URL.format(query_word=self.query_word)
        driver = driver_setting(headless_flg=True)
        driver.get(query_url)
        a_disabled_elements = driver.find_elements_by_css_selector(".a-disabled")
        if len(a_disabled_elements) == 3:
            self.page_count = int(a_disabled_elements[-1].text)
        else:
            self.page_count = int(
                driver.find_elements_by_css_selector(".a-normal")[-1].text
            )
        driver.quit()

    def scraping(self) -> None:
        with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
            for i in range(self.page_count):
                executor.submit(self.fetch_scraping_data, page_count=i + 1)
        for df_data in self.df_list:
            self.df = self.df.append(df_data, ignore_index=True)
        self.df = self.df.sort_values(["page", "index"])
        for asin in self.df["ASIN"]:
            eel.output_oder_list(f"ASIN: {asin}")
        eel.output_oder_list(f"{self.all_data_count}件抽出しました。")

    def fetch_scraping_data(self, page_count: int) -> None:
        query_url = PAGE_QUERY_URL.format(
            query_word=self.query_word, page_count=page_count
        )
        driver = driver_setting(headless_flg=True)
        driver.get(query_url)
        data_counter = 0
        elements = driver.find_elements_by_css_selector(".s-result-item.s-asin")
        for element in elements:
            self.all_data_count += 1
            data_counter += 1
            element.get_attribute("data-asin")
            try:
                product_name = element.find_element_by_css_selector("span").text
            except Exception:
                product_name = "失敗"

            try:
                asin = element.get_attribute("data-asin")
            except Exception:
                asin = "失敗"

            self.df_list.append(
                {
                    "page": page_count,
                    "index": data_counter,
                    "product_name": product_name,
                    "ASIN": asin,
                }
            )
            sleep(0.1)
        driver.quit()

    def write_csv(self):
        if len(self.df) > 0:
            write_csv("_".join(self.search_words), self.df)
            log.info(f"{len(self.df)}件出力しました。")
        else:
            log.info("データが0件です。")


def scraping(search_word: str):
    my_scraping = Scraping(search_word)
    my_scraping.fetch_page_count()
    my_scraping.scraping()
    my_scraping.write_csv()


# if __name__ == "__main__":
#     main()
