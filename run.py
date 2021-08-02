import eel

from common.desktop import start
from scraping import scraping

app_name = "web"
end_point = "index.html"
size = (600, 700)


@eel.expose
def fetch_data(search_word: str) -> None:
    scraping(search_word=search_word)


if __name__ == "__main__":
    start(app_name, end_point, size)
