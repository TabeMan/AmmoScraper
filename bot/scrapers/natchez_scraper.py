import logging
import traceback
from bs4 import BeautifulSoup

from bot.base.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class NatchezScraper(BaseScraper):
    """
    A scraper for the Natchez website.

    Inherits from BaseScraper.
    """

    def __init__(self, url):
        """
        Initializes the NatchezScraper with a URL.

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
        page.goto(self.url)
        page.wait_for_selector("div#root")
        soup = BeautifulSoup(page.content(), "html.parser")
        self.process_page(soup)

    def process_page(self, soup):
        """
        Processes the page content to extract product listings.

        Args:
            soup (BeautifulSoup object): The parsed HTML of the page.
        """
        try:
            inner = soup.find("div", {"class": "sc-dlnjwi bAXiqn"}).find(
                "section", {"class": "sc-kSCemg fAJJHa"}
            )
            print(inner)
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
        result["title"] = row.find(
            "p", {"class": "sc-dWBRfb sc-jHcXXw iWqacH jXsVSz"}
        ).text.strip()
        print(result["title"])
        result["steel_casing"] = "steel" in result["title"].lower()
        result["remanufactured"] = "reman" in result["title"].lower()
        result["link"] = row.find("a").get("href")
        print(result["link"])
        result["image"] = row.find("img").get("src")
        print(result["image"])
        result["website"] = "Natchez"

        original_price = float(
            row.find("div", {"class": "sc-gIvpjk gZQWys"}).text.strip("$")
        )
        result["original_price"] = f"{original_price:.2f}"
        print(result["original_price"])
        cpr = float(
            row.find("div", {"class": "sc-eEVmNe lmmOGX"})
            .text.split("/")[0]
            .strip("($")
        )
        result["cpr"] = f"{cpr:.2f}"
        print(result["cpr"])
        self.results.append(result)
