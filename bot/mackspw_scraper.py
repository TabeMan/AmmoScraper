import logging
import traceback
from bs4 import BeautifulSoup

from bot.base.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class MackspwScraper(BaseScraper):
    """
    A scraper for the Mack's Prairie Wings website.

    Inherits from BaseScraper.
    """

    def __init__(self, url):
        """
        Initializes the MackspwScraper with a URL.

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
        page.wait_for_selector("div#main-container")
        soup = BeautifulSoup(page.content(), "html.parser")
        self.process_page(soup)

    def process_page(self, soup):
        """
        Processes the page content to extract product listings.

        Args:
            soup (BeautifulSoup object): The parsed HTML of the page.
        """
        try:
            inner = soup.find("div", {"class": "facets-facet-browse-items"}).find_all(
                "div", {"class": "facets-items-collection-view-row"}
            )
        except Exception as e:
            print(f"Unexpected error: {e} - {self.url} during process_page")
            traceback.print_exc()
            return

        for div in inner:
            self.process_div(div)

    def process_div(self, div):
        """
        Processes a single div of product listings to extract product info.

        Args:
            div (bs4.element.Tag): The HTML element representing a product listing.
        """
        try:
            all_div = div.find_all(
                "div", {"class": "facets-items-collection-view-cell-span3"}
            )
        except Exception as e:
            print(f"Unexpected error: {e} - {self.url} during process_div")
            traceback.print_exc()
            return

        for row in all_div:
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

    def extract_product_info(self, row):
        """
        Extracts product info from a product listing.

        Args:
            row (bs4.element.Tag): The HTML element representing a product listing.

        Returns:
            dict: A dictionary containing the extracted product info.
        """
        result = {}
        if row.find("span", {"class": "product-line-stock-msg-out-text"}):
            return
        result["title"] = row.find(
            "a", {"class": "facets-item-cell-grid-title"}
        ).text.strip()
        result["steel_casing"] = "steel" in result["title"].lower()
        result["remanufactured"] = "reman" in result["title"].lower()
        link = row.find("a", {"class": "facets-item-cell-grid-title"}).get("href")
        result["link"] = f"https://www.mackspw.com{link}"
        result["image"] = row.find("img", {"class": "facets-item-cell-grid-image"}).get(
            "src"
        )
        result["website"] = "Mack's Prairie Wings"
        original_price = float(
            row.find("span", {"class": "product-views-price-lead"}).text.strip(" $")
        )
        result["original_price"] = f"{original_price:.2f}"
        cpr = float(
            row.find("div", {"class": "price-per-round-amount"})
            .text.strip(" ($")
            .split(" ")[0]
        )
        result["cpr"] = f"{cpr:.2f}"
        self.results.append(result)
