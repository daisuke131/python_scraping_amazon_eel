import eel

from common.desktop import start
from ranking_fetch_data import scraping

app_name = "web"
end_point = "ranking_fetch_data.html"
size = (600, 700)


@eel.expose
def fetch_data(ranking_url: str) -> None:
    scraping(ranking_url=ranking_url)


if __name__ == "__main__":
    start(app_name, end_point, size)
