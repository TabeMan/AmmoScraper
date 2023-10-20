import logging
import traceback
from bs4 import BeautifulSoup

from bot.base.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class AmmunitiondepotScraper(BaseScraper):
    """
    A scraper for the Ammunition Depot website.

    Inherits from BaseScraper.
    """

    def __init__(self, url):
        """
        Initializes the AmmunitiondepotScraper with a URL.

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
        page.wait_for_selector("div.ss-targeted")
        soup = BeautifulSoup(page.content(), "html.parser")
        self.process_page(soup)

    def process_page(self, soup):
        """
        Processes the page content to extract product listings.

        Args:
            soup (BeautifulSoup object): The parsed HTML of the page.
        """
        try:
            inner = soup.find("div", {"class": "ss-targeted"}).find("ol").find_all("li")
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
            "a", {"class": "product-item-link ng-binding"}
        ).text.strip()
        result["casing"] = "steel" in result["title"].lower()
        result["remanufactured"] = "reman" in result["title"].lower()
        link = row.find("a", {"class": "product-item-link ng-binding"}).get("href")
        result["link"] = f"https:{link}"
        image = row.find("img", {"class": "product-image-photo"})["src"]
        result["image"] = f"https:{image}"
        result["website"] = "Ammunition Depot"
        price_tag = row.find("span", {"class": "ng-binding ss-sale-price"})
        if price_tag is None:
            price_tag = row.find("span", {"class": "price ng-scope"}).find(
                "span", {"class": "ng-binding"}
            )

        if price_tag is not None:
            original_price = float(price_tag.text.strip("$"))
        else:
            print("Price not found")
            return

        result["original_price"] = f"{original_price:.2f}"
        cpr = float(
            row.find("span", {"class": "rounds-price ng-scope"})
            .find("span", {"class": "ng-binding"})
            .text.strip("$")
        )
        result["cpr"] = f"{cpr:.2f}"
        self.results.append(result)
