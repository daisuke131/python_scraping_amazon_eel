import os
import random

from dotenv import load_dotenv
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.utils import ChromeType


def driver_setting(headless_flg: bool):
    load_dotenv()
    browser_name = os.getenv("BROWSER")
    # user_agent = os.getenv("USER_AGENT")
    user_agent = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        + "(KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
        + "(KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        + "(KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        + "(KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
    ]
    user_agent_random = user_agent[random.randrange(0, len(user_agent), 1)]
    # ドライバーの読み込み
    if "firefox" in browser_name:
        options = webdriver.FirefoxOptions()
    else:
        options = webdriver.ChromeOptions()

    # ヘッドレスモードの設定
    if os.name == "posix" or headless_flg:  # Linux　➙　本番環境のためHeadless
        options.add_argument("--headless")

    # options.add_argument("--user-agent=" + user_agent)
    options.add_argument("--user-agent=" + user_agent_random)
    # self.options.add_argument('log-level=3')
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")
    options.add_argument("--incognito")  # シークレットモードの設定を付与
    options.add_argument("disable-infobars")  # AmazonLinux用
    # options.add_argument("--start-maximized")  # 画面最大化
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("log-level=3")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-desktop-notifications")
    options.add_argument("--disable-application-cache")
    options.add_argument("--lang=ja")

    try:
        if "firefox" in browser_name:
            driver = webdriver.Firefox(
                executable_path=GeckoDriverManager().install(), options=options
            )
        elif "chromium" in browser_name:
            driver = webdriver.Chrome(
                ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install(),
                options=options,
            )
        else:
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        return driver
    except Exception:
        return None
