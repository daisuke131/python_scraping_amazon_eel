from concurrent.futures import ThreadPoolExecutor
from time import sleep

import eel
import pandas as pd

from common.csv import write_csv
from common.driver import driver_setting
from common.log import log_setting

THREAD_COUNT = None  # スレッド数Noneで自動
PG2_QUERY = "ref=zg_bs_pg_2?ie=UTF8&pg=2"
# SEARCH_QUERY_URL = "https://www.amazon.co.jp/s?k={query_word}"
# PAGE_QUERY_URL = SEARCH_QUERY_URL + "&page={page_count}"

log = log_setting()


class Scraping:
    def __init__(self, ranking_url: str) -> None:
        # self.search_words: str
        # self.query_word: str
        # self.page_count: int = 0
        self.category_name: str
        self.df = pd.DataFrame()
        self.df_list = []
        # self.search_word_formating(search_word)
        self.item_urls = []
        self.data_count: int = 0
        self.fetch_item_urls(ranking_url)

    # def search_word_formating(self, search_word: str) -> None:
    #     # クエリパラメータの形に整形
    #     self.search_words = search_word.split()
    #     query_words = []
    #     for word in self.search_words:
    #         query_words.append(word)
    #     self.query_word = "+".join(query_words)
    #     log.info(f"検索ワード：{self.search_words}")

    def fetch_item_urls(self, ranking_url: str) -> None:
        ranking_pg2_url = self.fetch_ranking_pg2_url(ranking_url)
        self.fetch_urls(ranking_url)
        self.fetch_urls(ranking_pg2_url)

    def fetch_urls(self, ranking_url: str) -> None:
        driver = driver_setting(headless_flg=True)
        driver.get(ranking_url)
        self.category_name = driver.find_element_by_css_selector(
            "#zg-right-col > h1 > span"
        ).text
        elements = driver.find_elements_by_css_selector(".aok-inline-block.zg-item")
        for element in elements:
            self.data_count += 1
            self.item_urls.append(
                (
                    self.data_count,
                    element.find_element_by_css_selector("a").get_attribute("href"),
                )
            )
        driver.quit()

    def fetch_ranking_pg2_url(self, ranking_url: str) -> str:
        split_list = ranking_url.split("/")
        split_list[-1] = PG2_QUERY
        return "/".join(split_list)

    # def fetch_page_count(self) -> None:
    #     driver = driver_setting(headless_flg=True)
    #     driver.get(self.ranking_pg1_url)
    #     a_disabled_elements = driver.find_elements_by_css_selector(".a-disabled")
    #     if len(a_disabled_elements) == 3:
    #         self.page_count = int(a_disabled_elements[-1].text)
    #     else:
    #         self.page_count = int(
    #             driver.find_elements_by_css_selector(".a-normal")[-1].text
    #         )
    #     driver.quit()

    def scraping(self) -> None:
        with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
            for ranking, item_url in self.item_urls:
                executor.submit(
                    self.fetch_scraping_data, ranking=ranking, item_url=item_url
                )
        # for item_url in self.item_urls:
        #     self.fetch_scraping_data(item_url=item_url)
        for df_data in self.df_list:
            self.df = self.df.append(df_data, ignore_index=True)
        self.df = self.df.sort_values(["ランキング"])
        # for asin in self.df["ASIN"]:
        #     eel.output_oder_list(f"ASIN: {asin}")
        eel.output_oder_list("抽出完了")

    def fetch_scraping_data(self, ranking: int, item_url: str) -> None:
        if ranking == 9:
            True
        driver = driver_setting(headless_flg=True)
        driver.get(item_url)

        try:
            asin_element = driver.find_element_by_id("ASIN")
            asin = asin_element.get_attribute("value")
        except Exception:
            asin = ""
        try:
            read_time_element = driver.find_element_by_id(
                "mir-layout-DELIVERY_BLOCK-slot-DELIVERY_MESSAGE"
            )
            read_time = read_time_element.text
        except Exception:
            read_time_element = driver.find_element_by_id("dynamicDeliveryMessage")
            read_time = read_time_element.text
        try:
            driver.find_element_by_css_selector("#priceBadging_feature_div > i")
            prime = "prime適用商品"
        except Exception:
            prime = ""
        if driver.find_elements_by_css_selector("#priceblock_ourprice"):
            price = driver.find_element_by_css_selector("#priceblock_ourprice").text
        elif driver.find_elements_by_css_selector("#priceblock_dealprice"):
            price = driver.find_element_by_css_selector("#priceblock_dealprice").text
        elif driver.find_elements_by_css_selector("#priceblock_saleprice"):
            price = driver.find_element_by_css_selector("#priceblock_saleprice").text
        else:
            price = ""

        self.df_list.append(
            {
                "ランキング": ranking,
                "商品名": driver.find_element_by_css_selector("#productTitle").text,
                "価格": price,
                "発送リードタイム": read_time,
                "Prime": prime,
                "ASIN": asin,
            }
        )
        sleep(0.1)
        driver.quit()

    def write_csv(self):
        if len(self.df) > 0:
            write_csv(self.category_name, self.df)
            log.info(f"{len(self.df)}件出力しました。")
        else:
            log.info("データが0件です。")


def scraping(ranking_url: str):
    my_scraping = Scraping(ranking_url)
    # my_scraping.fetch_page_count()
    my_scraping.scraping()
    my_scraping.write_csv()


# if __name__ == "__main__":
#     main()
