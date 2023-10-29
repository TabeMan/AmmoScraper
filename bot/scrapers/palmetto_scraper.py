import re
import time
import logging
import traceback
from bs4 import BeautifulSoup

from bot.base.base_scraper import BaseScraper
from bot.base.get_manufacturer import get_manufacturer

logger = logging.getLogger(__name__)


class PalmettoScraper(BaseScraper):
    """
    A scraper for the Palmetto State Armory website.

    Inherits from BaseScraper.
    """

    def __init__(self, url):
        """
        Initializes the PalmettoScraper with a URL.

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
        # Click "Next" button until it's no longer visible
        while True:
            page.wait_for_selector("ol.products")
            soup = BeautifulSoup(page.content(), "html.parser")
            self.process_page(soup)
            try:
                next_button_locator = page.locator("a.next").nth(2)
                if next_button_locator.is_visible():
                    next_button_locator.click()
                else:
                    break
            except Exception as e:
                print(f"An error occurred: {e}")
                break

    def process_page(self, soup):
        """
        Processes the page content to extract product listings.

        Args:
            soup (BeautifulSoup object): The parsed HTML of the page.
        """
        try:
            inner = soup.find(
                "ol", {"class": "products list items product-items"}
            ).find_all("li")
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
        if row.find("span", {"class": "items-count"}):
            return
        result["title"] = row.find("a", {"class": "product-item-link"}).text.strip()
        result["steel_casing"] = "steel" in result["title"].lower()
        result["remanufactured"] = "reman" in result["title"].lower()
        result["manufacturer"] = get_manufacturer(result["title"])
        if not result["manufacturer"]:
            return
        result["link"] = row.find("a", {"class": "product-item-link"}).get("href")
        result["image"] = row.find("img", {"class": "product-image-photo"})["src"]
        result["website"] = "Palmetto State Armory"

        original_price = float(
            row.find("span", {"class": "price-wrapper final-price"})
            .find("span", {"class": "price"})
            .text.strip()
            .strip("$")
        )
        result["original_price"] = f"{original_price:.2f}"
        match = re.search(r"(\d+[\d,]*)\s*(rds|rd b)", result["title"], re.IGNORECASE)
        if match:
            rounds_per_case_str = match.group(1).replace(",", "")
            rounds_per_case = int(rounds_per_case_str)
            if rounds_per_case == 0:
                return
            cpr = original_price / rounds_per_case
            result["cpr"] = f"{cpr:.2f}"
            self.results.append(result)
        else:
            return
