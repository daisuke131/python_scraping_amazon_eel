import os
from concurrent.futures import ThreadPoolExecutor
from time import sleep

import eel
import pandas as pd
from dotenv import load_dotenv

from common.csv import write_csv
from common.driver import driver_setting
from common.log import log_setting

THREAD_COUNT = None  # スレッド数Noneで自動
PG2_QUERY = "ref=zg_bs_pg_2?ie=UTF8&pg=2"

log = log_setting()


class Scraping:
    def __init__(self, ranking_url: str) -> None:
        self.category_name: str
        self.df = pd.DataFrame()
        self.df_list = []
        self.item_urls = []
        self.data_count: int = 0
        self.fetch_item_urls(ranking_url)

    def fetch_item_urls(self, ranking_url: str) -> None:
        ranking_pg2_url = self.fetch_ranking_pg2_url(ranking_url)
        self.fetch_urls(ranking_url)
        self.fetch_urls(ranking_pg2_url)

    def fetch_urls(self, ranking_url: str) -> None:
        # ログインしてprime情報と各URL取得
        driver = driver_setting(headless_flg=True)
        driver.get(ranking_url)
        login_url = driver.find_element_by_id("nav-link-accountList").get_attribute(
            "href"
        )
        driver.get(login_url)
        sleep(1)

        self.login(driver)

        self.category_name = driver.find_element_by_css_selector(
            "#zg-right-col > h1 > span"
        ).text
        elements = driver.find_elements_by_css_selector(".aok-inline-block.zg-item")
        for element in elements:
            self.data_count += 1
            is_prime = False
            if element.find_elements_by_css_selector(
                ".a-icon.a-icon-jp.a-icon-prime-jp.a-icon-small"
            ):
                is_prime = True
            self.item_urls.append(
                (
                    self.data_count,
                    element.find_element_by_css_selector("a").get_attribute("href"),
                    is_prime,
                )
            )
        logout_url = driver.find_element_by_id("nav-item-signout").get_attribute("href")
        driver.get(logout_url)
        sleep(1)
        driver.quit()

    def login(self, driver):
        try:
            load_dotenv()
            login_id = os.getenv("LOGIN_ID")
            password = os.getenv("PASSWORD")
            driver.find_element_by_id("ap_email").send_keys(login_id)
            driver.find_element_by_id("continue").click()
            sleep(1)
            driver.find_element_by_id("ap_password").send_keys(password)
            driver.find_element_by_id("signInSubmit").click()
            sleep(1)
        except Exception:
            eel.alert_js("ログイン失敗")
            return

    def fetch_ranking_pg2_url(self, ranking_url: str) -> str:
        split_list = ranking_url.split("/")
        split_list[-1] = PG2_QUERY
        return "/".join(split_list)

    def scraping(self) -> None:
        with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
            for ranking, item_url, is_prime in self.item_urls:
                executor.submit(
                    self.fetch_scraping_data,
                    ranking=ranking,
                    item_url=item_url,
                    is_prime=is_prime,
                )
        for df_data in self.df_list:
            self.df = self.df.append(df_data, ignore_index=True)
        self.df = self.df.sort_values(["ランキング"])

    def fetch_scraping_data(self, ranking: int, item_url: str, is_prime: bool) -> None:
        driver = driver_setting(headless_flg=True)
        driver.get(item_url)
        prime = ""
        if is_prime:
            prime = "prime対象"
        try:
            self.df_list.append(
                {
                    "ランキング": ranking,
                    "商品名": self.fetch_product_name(driver),
                    "価格": self.fetch_prise(driver),
                    "発送リードタイム": self.fetch_read_time(driver),
                    "Prime": prime,
                    "ASIN": self.fetch_asin(driver),
                    "URL": item_url,
                }
            )
        except Exception:
            self.df_list.append(
                {
                    "ランキング": ranking,
                    "商品名": "",
                    "価格": "",
                    "発送リードタイム": "",
                    "Prime": prime,
                    "ASIN": "",
                    "URL": item_url,
                }
            )
        sleep(0.1)
        driver.quit()

    def fetch_product_name(self, driver) -> str:
        try:
            product_name = driver.find_element_by_css_selector("#productTitle").text
        except Exception:
            product_name = "失敗"
        return product_name

    def fetch_prise(self, driver) -> str:
        price = "-"
        try:
            if driver.find_elements_by_id("priceblock_ourprice"):
                price = driver.find_element_by_id("priceblock_ourprice").text
            elif driver.find_elements_by_id("priceblock_dealprice"):
                price = driver.find_element_by_id("priceblock_dealprice").text
            elif driver.find_elements_by_id("priceblock_saleprice"):
                price = driver.find_element_by_id("priceblock_saleprice").text
            elif driver.find_elements_by_css_selector(
                "#availability > span.a-size-medium.a-color-price"
            ):
                price = driver.find_element_by_css_selector(
                    "#availability > span.a-size-medium.a-color-price"
                ).text
            elif driver.find_elements_by_css_selector(".a-size-base.a-color-price"):
                price = driver.find_element_by_css_selector(
                    ".a-size-base.a-color-price"
                ).text
            else:
                price = "失敗"
        except Exception:
            price = "失敗"
        return price

    def fetch_read_time(self, driver) -> str:
        read_time = "-"
        try:
            if driver.find_elements_by_id("mir-layout-DELIVERY_BLOCK-slot-UPSELL"):
                if driver.find_element_by_id(
                    "mir-layout-DELIVERY_BLOCK-slot-UPSELL"
                ).text:
                    read_time = driver.find_element_by_id(
                        "mir-layout-DELIVERY_BLOCK-slot-UPSELL"
                    ).text
            if driver.find_elements_by_id(
                "mir-layout-DELIVERY_BLOCK-slot-DELIVERY_MESSAGE"
            ):
                if driver.find_element_by_id(
                    "mir-layout-DELIVERY_BLOCK-slot-DELIVERY_MESSAGE"
                ).text:
                    read_time = driver.find_element_by_id(
                        "mir-layout-DELIVERY_BLOCK-slot-DELIVERY_MESSAGE"
                    ).text
            if driver.find_elements_by_id("dynamicDeliveryMessage"):
                if driver.find_element_by_id("dynamicDeliveryMessage").text:
                    read_time = driver.find_element_by_id("dynamicDeliveryMessage").text
            if driver.find_elements_by_css_selector(
                "#outOfStock > div > div.a-section.a-spacing-small"
                + ".a-text-center > span.a-color-price.a-text-bold"
            ):
                if driver.find_element_by_css_selector(
                    "#outOfStock > div > div.a-section.a-spacing-small"
                    + ".a-text-center > span.a-color-price.a-text-bold"
                ).text:
                    read_time = driver.find_element_by_css_selector(
                        "#outOfStock > div > div.a-section.a-spacing-small"
                        + ".a-text-center > span.a-color-price.a-text-bold"
                    ).text
        except Exception:
            read_time = "失敗"
        return read_time

    def fetch_asin(self, driver) -> str:
        try:
            asin_element = driver.find_element_by_id("ASIN")
            asin = asin_element.get_attribute("value")
        except Exception:
            asin = "失敗"
        return asin

    def write_csv(self):
        if len(self.df) > 0:
            write_csv(self.category_name, self.df)
            log.info(f"{len(self.df)}件出力しました。")
        else:
            log.info("データが0件です。")


def scraping(ranking_url: str):
    my_scraping = Scraping(ranking_url)
    my_scraping.scraping()
    my_scraping.write_csv()
    eel.output_oder_list("抽出完了")
    eel.enable_btn()
