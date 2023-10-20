import re
import traceback
import logging
from bs4 import BeautifulSoup

from bot.base.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class Warehouse2aScraper(BaseScraper):
    """
    A scraper for the 2A Warehouse website.

    Inherits from BaseScraper.
    """

    def __init__(self, url):
        """
        Initializes the Warehouse2aScraper with a URL.

        Args:
            url (str): The URL to be scraped.
        """
        super().__init__(url)

    def scrape(self):
        """
        Navigates to the URL, waits for the page to load, then processes
        the page content to extract data.
        """
        browser = self.browser
        page = browser.new_page()
        page.goto(self.url, wait_until="networkidle")
        page.wait_for_selector("div.body")
        soup = BeautifulSoup(page.content(), "html.parser")
        self.process_page(soup)

    def process_page(self, soup):
        """
        Processes the page content to extract product listings.
        The tr tags are split into odd and even lists, so we need to
        process them separately.

        Args:
            soup (BeautifulSoup object): The parsed HTML of the page.
        """
        try:
            inner = soup.find("ul", {"class": "productGrid--maxCol3"}).find_all(
                "li", {"class": "product"}
            )
        except Exception as e:
            print(f"Unexpected error: {e} - {self.url} during process_page")
            traceback.print_exc()
            return

        for row in inner:
            self.process_row(row)

    def process_row(self, row):
        """
        Processes a single product listing to extract product info.

        Args:
            row (bs4.element.Tag): The HTML element representing a product listing.
        """
        try:
            self.extract_product_info(row)
        except Exception as e:
            print(f"Unexpected error: {e} - {self.url} during process_row")
            traceback.print_exc()
            return

    def extract_product_info(self, row):
        """
        Extracts product info from a product listing.

        Args:
            row (bs4.element.Tag): The HTML element representing a product listing.

        Returns:
            dict: A dictionary containing the extracted product info.
        """
        result = {}
        result["title"] = row.find("h4", {"class": "card-title"}).find("a").text.strip()
        result["steel_casing"] = "steel" in result["title"].lower()
        result["remanufactured"] = "reman" in result["title"].lower()
        result["link"] = row.find("h4", {"class": "card-title"}).find("a").get("href")
        result["image"] = row.find("span", {"class": "card-image-wrapper"}).find(
            "img", {"class": "card-image"}
        )["data-src"]
        result["website"] = "2A Warehouse"

        original_price = float(
            row.find(
                "span", {"class": "price price--withoutTax price--main"}
            ).text.strip("$")
        )
        result["original_price"] = f"{original_price:.2f}"

        match = re.search(
            r"(\d+)\s*(rounds|rds|rd|round)", result["title"].lower().replace(",", "")
        )
        if match:
            rounds_per_case = int(match.group(1))
            cpr = float(original_price / rounds_per_case)
            result["cpr"] = f"{cpr:.2f}"
            self.results.append(result)
        else:
            return
