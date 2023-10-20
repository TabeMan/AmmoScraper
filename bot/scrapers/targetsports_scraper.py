import logging
import traceback
from bs4 import BeautifulSoup

from bot.base.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class TargetsportsScraper(BaseScraper):
    """
    A scraper for the Target Sports website.

    Inherits from BaseScraper.
    """

    def __init__(self, url):
        """
        Initializes the TargetsportsScraper with a URL.

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
        page.wait_for_selector("div.product-listing-sort")
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
            inner = (
                soup.find("div", {"class": "ResultsArea"})
                .find("ul", {"class": "product-list"})
                .find_all("li")
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
        out_of_stock = row.find("button", {"class": "add-to-cart"}).text.strip()
        if out_of_stock == "Notify":
            return

        result["title"] = row.find("h2").text.strip()
        result["steel_casing"] = "steel" in result["title"].lower()
        result["remanufactured"] = "reman" in result["title"].lower()
        link = row.find("a").get("href")
        result["link"] = f"https://www.targetsportsusa.com{link}"
        result["image"] = row.find("img", {"class": "product-image"}).get("src")
        result["website"] = "Target Sports USA"

        prices = list(
            filter(
                lambda x: x != "",
                row.find("div", {"class": "product-listing-price"})
                .text.strip()
                .rsplit("$", 1),
            )
        )

        if len(prices) == 2:
            original_price = float(prices[0].strip("$"))
            result["original_price"] = f"{original_price:.2f}"
            cpr = prices[1].strip().split(" ")[0]
            cpr = float(cpr[:-1])
            result["cpr"] = f"{cpr:.2f}"
            self.results.append(result)
