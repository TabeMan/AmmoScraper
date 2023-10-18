import re
import traceback
import logging
from bs4 import BeautifulSoup

from bot.base.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class GunbuyerScraper(BaseScraper):
    """
    A scraper for the Gun Buyer website.

    Inherits from BaseScraper.
    """

    def __init__(self, url):
        """
        Initializes the GunbuyerScraper with a URL.

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
        page.wait_for_selector("div.page-wrapper")
        soup = BeautifulSoup(page.content(), "html.parser")
        self.process_page(soup)

    def process_page(self, soup):
        """
        Processes the page content to extract product listings.

        Args:
            soup (BeautifulSoup object): The parsed HTML of the page.
        """
        try:
            inner = (
                soup.find(
                    "div",
                    {"class": "products wrapper grid products-grid"},
                )
                .find("ol", {"class": "products list items product-items"})
                .find_all(
                    "li",
                    {"class": "item product product-item"},
                )
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
        if row.find("div", {"class": "fancy-title title-dotted-border title-center"}):
            return
        result["title"] = row.find("a", {"class": "product-item-link"}).text.strip()
        result["steel_casing"] = "steel" in result["title"].lower()
        result["remanufactured"] = "reman" in result["title"].lower()
        result["link"] = row.find("a", {"class": "product-item-link"}).get("href")
        result["image"] = row.find("img").get("data-original")
        result["website"] = "Gun Buyer"

        original_price = float(
            row.find("div", {"class": "price-box price-final_price"})
            .find("span", {"class": "price"})
            .text.strip("$")
        )
        result["original_price"] = f"{original_price:.2f}"

        match = re.search(r"(\d+)\s*(round|rd)", result["title"].lower())
        if match:
            rounds_per_case = int(match.group(1))
            cpr = original_price / rounds_per_case
            result["cpr"] = f"{cpr:.2f}"
            self.results.append(result)
        else:
            return
