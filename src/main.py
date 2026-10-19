from fileinput import filename

from logging_settings.logging_setup import setup_logger

setup_logger()

import argparse
import logging
import yaml
from scraper import scrape_all
from exporter import export2csv, export2xlsx
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

with open(BASE_DIR / "config.yaml") as conf_f:
    config = yaml.safe_load(conf_f)

parser = argparse.ArgumentParser(description="Price parser")
parser.add_argument('--url', help="Catalogue to parse")
parser.add_argument('--pages', type=int, help="Amount of pages to parse")
parser.add_argument('--delay', type=float, help='Delay between pages parsing')
parser.add_argument('--csv', action="store_true", help='Export result to .csv')
parser.add_argument('--xlsx', action="store_true", help='Export result to .xlsx')
args = parser.parse_args()

url = args.url if args.url is not None else config["scraping"]["website_to_scrape"]
pages = args.pages if args.pages is not None else config['scraping']["amount_of_pages_to_scrape"]
delay = args.delay if args.delay is not None else config["scraping"]["delay"]

data = scrape_all(url.rstrip('/'), pages, delay)

if data is None:
    logger.error("Failed to retrieve data from website")
    exit()

if args.csv or config["export"]['csv']['save']:
    filename = config["export"]['csv']['filename']
    headers = list(data[0].keys())
    data_to_save = [list(el.values()) for el in data]
    num2store = config['export']['csv']['num_of_files_to_store']
    export2csv(filename, headers, data_to_save, num2store)
if args.xlsx or config["export"]['xlsx']['save']:
    filename = config["export"]['xlsx']['filename']
    headers = list(data[0].keys())
    data_to_save = [list(el.values()) for el in data]
    num2store = config['export']['xlsx']['num_of_files_to_store']
    export2xlsx(filename, headers, data_to_save, num2store)
