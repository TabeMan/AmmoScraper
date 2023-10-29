import logging
import traceback
from bs4 import BeautifulSoup

from bot.base.base_scraper import BaseScraper
from bot.base.get_manufacturer import get_manufacturer

logger = logging.getLogger(__name__)


class MiwallcorporationScraper(BaseScraper):
    """
    A scraper for the Miwall Corporation website.

    Inherits from BaseScraper.
    """

    def __init__(self, url):
        """
        Initializes the MiwallcorporationScraper with a URL.

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
        page.wait_for_selector("ul.productGrid")
        # Click "Next" button until it's no longer visible
        while True:
            soup = BeautifulSoup(page.content(), "html.parser")
            self.process_page(soup)
            next_button_locator = page.locator("li.pagination-item--next").nth(0)
            if next_button_locator.is_visible():
                next_button_locator.click()
                page.wait_for_load_state("load")
            else:
                break

    def process_page(self, soup):
        """
        Processes the page content to extract product listings.

        Args:
            soup (BeautifulSoup object): The parsed HTML of the page.
        """
        try:
            inner = soup.find("ul", {"class": "productGrid"}).find_all(
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
        result["title"] = (
            row.find("a", {"class": "pcs__title"}).get("aria-label", "").strip()
        )
        result["steel_casing"] = "steel" in result["title"].lower()
        result["remanufactured"] = "reman" in result["title"].lower()
        result["manufacturer"] = get_manufacturer(result["title"])
        if not result["manufacturer"]:
            return
        result["link"] = row.find("a").get("href")
        result["image"] = row.find("img", {"class": "card-image"}).get("src")
        result["website"] = "Miwall Corporation"
        price = row.find("span", {"class": "price price--withoutTax"}).text.strip("$")
        try:
            original_price = float(price)
            result["original_price"] = f"{original_price:.2f}"
            rounds_per_case = int(
                row.find(
                    "label", {"class": "form-label form-label--rounds-per-case"}
                ).text.split(": ")[1]
            )
            cpr = original_price / rounds_per_case
            result["cpr"] = f"{cpr:.2f}"
            self.results.append(result)
        except Exception as e:
            print(f"Error: {e} - {self.url}")
