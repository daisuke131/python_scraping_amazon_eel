import math

import pandas as pd
from bs4 import BeautifulSoup

# from common.csv import write_csv
from common.driver import driver_setting
from common.log import log_setting

# from concurrent.futures import ThreadPoolExecutor


THREAD_COUNT = None  # スレッド数Noneで自動
SEARCH_QUERY_URL = "https://www.amazon.co.jp/s?k={query_word}"
PAGE_QUERY_URL = SEARCH_QUERY_URL + "&page={page_count}"

log = log_setting()


class Scraping:
    def __init__(self, search_word) -> None:
        self.search_words: str
        self.query_word: str
        self.page_count: int
        self.df = pd.DataFrame()
        self.df_list = []
        self.search_word_formating(search_word)

    def search_word_formating(self, search_word):
        # クエリパラメータの形に整形
        self.search_words = search_word.split()
        query_words = []
        for word in self.search_words:
            query_words.append(word)
        self.query_word = "+".join(query_words)
        log.info(f"検索ワード：{self.search_words}")

    def fetch_page_count(self):
        query_url = SEARCH_QUERY_URL.format(query_word=self.query_word)
        driver = driver_setting(headless_flg=True)
        driver.get(query_url)
        soup = BeautifulSoup(driver.page_source, features="html.parser")
        s = soup.select_one("#search > script:nth-child(8)").next.split('"')
        s_index = s.index("totalResultCount")
        data_count = int(s[s_index + 1].replace(":", "").replace(",", ""))
        self.page_count = math.ceil(data_count / 48)
        if self.page_count > 10:
            self.page_count = 10
        driver.quit()

    # def scraping(self):
    #     with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
    #         for page_counter in range(self.page_count):
    #             executor.submit(self.fetch_scraping_data, page_counter + 1)
    #     for df_data in self.df_list:
    #         self.df = self.df.append(df_data, ignore_index=True)
    #     self.df = self.df.sort_values(["page", "index"])

    def fetch_scraping_data(self, page_counter):
        query_url = PAGE_QUERY_URL.format(
            query_word=self.query_word, page_counter=page_counter
        )
        driver = driver_setting(headless_flg=True)
        driver.get(query_url)
        try:
            # ポップアップを閉じる
            driver.execute_script('document.querySelector(".karte-close").click()')
            driver.execute_script('document.querySelector(".karte-close").click()')
        except Exception:
            pass
        data_counter = 0
        corps_list = driver.find_elements_by_class_name("cassetteRecruit__content")
        for corp in corps_list:
            data_counter += 1
            self.df_list.append(
                {
                    "page": page_counter,
                    "index": data_counter,
                    "会社名": self.fetch_corp_name(corp, "div > section > h3"),
                    "勤務地": self.find_table_target_word(corp, "勤務地"),
                    "給与": self.find_table_target_word(corp, "給与"),
                }
            )
        driver.quit()

    def fetch_corp_name(self, driver, css_selector):
        try:
            return driver.find_element_by_css_selector(css_selector).text
        except Exception:
            pass

    def find_table_target_word(self, driver, target):
        table_headers = driver.find_elements_by_class_name("tableCondition__head")
        table_bodies = driver.find_elements_by_class_name("tableCondition__body")
        for table_header, table_body in zip(table_headers, table_bodies):
            if table_header.text == target:
                return table_body.text

    # def write_csv(self):
    #     if len(self.df) > 0:
    #         write_csv("_".join(self.search_words), self.df)
    #         log.info(f"{len(self.df)}件出力しました。")
    #     else:
    #         log.info("データが0件です。")


def scraping(search_word: str):
    my_scraping = Scraping(search_word)
    my_scraping.fetch_page_count()
    # my_scraping.scraping()
    # my_scraping.write_csv()


# if __name__ == "__main__":
#     main()
