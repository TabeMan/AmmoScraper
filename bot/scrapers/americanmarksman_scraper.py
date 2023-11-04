import re
import traceback
import logging
from bs4 import BeautifulSoup

from bot.base.base_scraper import BaseScraper
from bot.base.get_manufacturer import get_manufacturer

logger = logging.getLogger(__name__)


class AmericanmarksmanScraper(BaseScraper):
    """
    A scraper for the American Marksman USA website.

    Inherits from BaseScraper.
    """

    def __init__(self, url):
        """
        Initializes the AmericanmarksmanScraper with a URL.

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
        try:
            page.goto(self.url)
        except Exception as e:
            print(f"Unexpected error: {e} - {self.url} during page.goto")
            traceback.print_exc()
            return
        page.wait_for_selector("div.container")
        soup = BeautifulSoup(page.content(), "html.parser")
        self.process_page(soup)

    def process_page(self, soup):
        """
        Processes the page content to extract product listings.

        Args:
            soup (BeautifulSoup object): The parsed HTML of the page.
        """
        try:
            inner = soup.find(
                "div", {"class": "product-items product-items-1"}
            ).find_all("div", {"class": "product-item product-item-thumbstyle"})
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
        if (
            row.find("div", {"id": "availability"}).find("span").text.strip().lower()
            == "out of stock"
        ):
            return
        result["title"] = row.find("div", {"class": "name"}).find("a").text.strip()
        result["steel_casing"] = "steel" in result["title"].lower()
        result["remanufactured"] = "reman" in result["title"].lower()
        result["manufacturer"] = get_manufacturer(result["title"])
        if not result["manufacturer"]:
            return
        link = row.find("a").get("href")
        result["link"] = f"https://www.theamericanmarksman.com/{link}"
        result["image"] = row.find("img", {"class": "img-responsive"}).get("src")
        result["website"] = "American Marksman"

        if row.find("span", {"class": "sale-price"}):
            original_price = float(
                row.find("span", {"class": "sale-price"}).text.strip("$")
            )
        else:
            original_price = float(
                row.find("span", {"class": "regular-price"}).text.strip("$")
            )
        result["original_price"] = f"{original_price:.2f}"

        cpr = float(
            row.find("div", {"class": "extrafieldsBlock"})
            .find("div", {"class": "extra_field"})
            .find("span", {"class": "info"})
            .text.strip("$")
        )
        result["cpr"] = f"{cpr:.2f}"
        self.results.append(result)
