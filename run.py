import eel

from common.desktop import start
from scraping import scraping

# import sys


app_name = "web"
end_point = "index.html"
size = (600, 700)


@eel.expose
def fetch_data(search_word: str) -> None:
    scraping(search_word=search_word)
    # my_api.execute_api()


if __name__ == "__main__":
    start(app_name, end_point, size)
