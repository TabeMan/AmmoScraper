import logging
import traceback
from bs4 import BeautifulSoup

from bot.base.base_scraper import BaseScraper
from bot.base.get_manufacturer import get_manufacturer

logger = logging.getLogger(__name__)


class CheapammoScraper(BaseScraper):
    """
    A scraper for the Cheap Ammo website.

    Inherits from BaseScraper.
    """

    def __init__(self, url):
        """
        Initializes the CheapammoScraper with a URL.

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
        page.wait_for_selector("div.grid-container")
        soup = BeautifulSoup(page.content(), "html.parser")
        self.process_page(soup)

    def process_page(self, soup):
        """
        Processes the page content to extract product listings.

        Args:
            soup (BeautifulSoup object): The parsed HTML of the page.
        """
        try:
            inner = soup.find("ol", {"class": "b-category-product-list"}).find_all(
                "li",
                {"class": "b-category-product-list-item"},
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
        result["title"] = row.find("h2").text.strip()
        result["steel_casing"] = "steel" in result["title"].lower()
        result["remanufactured"] = "reman" in result["title"].lower()
        result["manufacturer"] = get_manufacturer(result["title"])
        if not result["manufacturer"]:
            return
        result["link"] = row.find(
            "a", {"class": "b-category-product-list-item__image"}
        ).get("href")
        result["image"] = row.find("img").get("src")
        result["website"] = "Cheap Ammo"

        price_cell = row.find(
            "div", {"class": "b-category-product-list-item__price"}
        ).find_all("span", {"class": "price"})
        if len(price_cell) == 1:
            original_price = float(price_cell[0].text.strip("$"))
        elif len(price_cell) == 2:
            original_price = float(price_cell[1].text.strip().replace("$", ""))
        else:
            return
        result["original_price"] = f"{original_price:.2f}"
        cpr = float(
            row.find("div", {"class": "b-price-ppr"}).text.strip("$").split(" ")[0]
        )
        result["cpr"] = f"{cpr:.2f}"
        self.results.append(result)
