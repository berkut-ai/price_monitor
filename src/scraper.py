import logging
import yaml
import time
import requests
from bs4 import BeautifulSoup
from logging_settings.logging_setup import setup_logger
from pathlib import Path
from urllib.parse import urljoin
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

setup_logger()

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


with open(BASE_DIR / "config.yaml") as conf_f:
    config = yaml.safe_load(conf_f)
    BASE_URL = config["scraping"]["website_to_scrape"]
    PAGES2SCRAPE = config['scraping']["amount_of_pages_to_scrape"]
    DELAY = config["scraping"]["delay"]


PAGE_URL = BASE_URL + "/catalogue/page-{}.html"

def fetch_page(session: requests.Session, page: int) -> str:
    response = session.get(PAGE_URL.format(page), timeout=10)
    response.raise_for_status()
    response.encoding = 'utf-8'

    return response.text

def make_session() -> requests.Session:
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (portfolio demo scraper)"
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def parse_page(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")


    books = []
    for book in soup.select("article.product_pod"):
        title = book.select_one("h3 a")['title']
        price = book.select_one('p.price_color').get_text(strip=True)
        availability = book.select_one("p.availability").get_text(strip=True)
        rating = book.select_one("p.star-rating")['class'][1]
        link = book.select_one("h3 a")

        books.append({
            "title": title,
            "price": price,
            "availability": "In stock" in availability,
            "rating": RATINGS[rating],
            "url": urljoin(BASE_URL, link["href"])
        })

    return books


def scrape_all() -> list[dict[str, str]]:
    all_books = []
    session = make_session()

    logger.info(f"Start scraping {PAGES2SCRAPE} pages from URL: {BASE_URL}")

    for page_num in range(1, PAGES2SCRAPE+1):
        try:
            html = fetch_page(session, page_num)
            books = parse_page(html)
        except Exception as err:
            logger.error(f"Error with page {page_num}. Moving to next page...", exc_info=err)
            continue
        logger.info(f"Page {page_num}/{PAGES2SCRAPE}: {len(books)} books")
        all_books.extend(books)
        time.sleep(DELAY)

    logger.info(f"Total collected: {len(all_books)}")

    return all_books

if __name__ == "__main__":
    print(scrape_all())