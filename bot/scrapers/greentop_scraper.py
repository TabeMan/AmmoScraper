import re
import traceback
import logging
from bs4 import BeautifulSoup

from bot.base.base_scraper import BaseScraper
from bot.base.get_manufacturer import get_manufacturer

logger = logging.getLogger(__name__)


class GreentopScraper(BaseScraper):
    """
    A scraper for the Green Top website.

    Inherits from BaseScraper.
    """

    def __init__(self, url):
        """
        Initializes the GreentopScraper with a URL.

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
        # Click "Next" button until it's no longer visible
        while True:
            page.goto(self.url)
            page.wait_for_selector("div.page-wrapper")
            soup = BeautifulSoup(page.content(), "html.parser")
            self.process_page(soup)
            if soup.find("ul", {"class": "items pages-items"}).find(
                "li", {"class": "item pages-item-next"}
            ):
                url = (
                    soup.find("ul", {"class": "items pages-items"})
                    .find("li", {"class": "item pages-item-next"})
                    .find("a")
                    .get("href")
                )
                if url:
                    self.url = url
                else:
                    break
            else:
                break

    def process_page(self, soup):
        """
        Processes the page content to extract product listings.

        Args:
            soup (BeautifulSoup object): The parsed HTML of the page.
        """
        try:
            inner = (
                soup.find("div", {"class": "products wrapper grid products-grid"})
                .find("ol", {"class": "products list items product-items"})
                .find_all("li")
            )
        except Exception as e:
            print(f"Unexpected error: {e} - {self.url} during process_page")
            traceback.print_exc()
            return
        # Discard li elements that are not product listings
        number_of_listings = soup.find("p", {"class": "toolbar-amount"}).find_all(
            "span", {"class": "toolbar-number"}
        )
        if len(number_of_listings) == 1:
            products = int(number_of_listings[0].text.strip())
        else:
            products = int(number_of_listings[1].text.strip())
        for row in inner[:products]:
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
            row.find("div", {"class": "product details product-item-details"})
            .find("a", {"class": "product-item-link primary-info"})
            .text.strip()
        )
        result["steel_casing"] = "steel" in result["title"].lower()
        result["remanufactured"] = "reman" in result["title"].lower()
        result["manufacturer"] = get_manufacturer(result["title"])
        if not result["manufacturer"]:
            return
        result["link"] = row.find("a", {"class": "product-item-link primary-info"}).get(
            "href"
        )
        result["image"] = row.find("img", {"class": "product-image-photo"}).get("src")
        result["website"] = "Green Top"

        original_price = float(
            row.find("div", {"class": "secondary-info"})
            .find("span", {"class": "price-wrapper"})
            .find("span", {"class": "price"})
            .text.strip("$")
        )
        result["original_price"] = f"{original_price:.2f}"

        match = re.search(
            r"(\d+)\s*(rd|bx|/box|per|round)", result["title"], re.IGNORECASE
        )
        if match:
            rounds_per_case = int(match.group(1))
            cpr = original_price / rounds_per_case
            result["cpr"] = f"{cpr:.2f}"
            self.results.append(result)
        else:
            return
