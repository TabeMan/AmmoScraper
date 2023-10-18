import traceback
import logging
from bs4 import BeautifulSoup

from bot.base.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class SportsmansoutdoorsuperstoreScraper(BaseScraper):
    """
    A scraper for the Sportsmans Outdoor Superstore website.

    Inherits from BaseScraper.
    """

    def __init__(self, url):
        """
        Initializes the SportsmansoutdoorsuperstoreScraper with a URL.

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
        page.wait_for_selector("div.container-fluid")
        soup = BeautifulSoup(page.content(), "html.parser")
        self.process_page(soup)

    def process_page(self, soup):
        """
        Processes the page content to extract product listings.

        Args:
            soup (BeautifulSoup object): The parsed HTML of the page.
        """
        try:
            inner = soup.find("div", {"class": "row padding-v-10"}).find_all(
                "div",
                {"class": "prd-ctn"},
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
        # Check if product is in stock
        if row.find("div", {"class": "prd-in-stk-ctn"}):
            result = {}
            if row.find(
                "div", {"class": "fancy-title title-dotted-border title-center"}
            ):
                return
            result["title"] = (
                row.find("div", {"class": "prd-info"}).find("h2").text.strip()
            )
            result["steel_casing"] = "steel" in result["title"].lower()
            result["remanufactured"] = "reman" in result["title"].lower()
            result["link"] = row.find("a").get("href")
            image = row.find("img").get("src")
            result["image"] = f"https://www.sportsmansoutdoorsuperstore.com{image}"
            result["website"] = "Sportsmans Outdoor Superstore"

            original_price = float(
                row.find("ul", {"class": "list-unstyled"})
                .find("span", {"class": "price"})
                .text.strip("$")
            )
            result["original_price"] = f"{original_price:.2f}"

            cpr = float(
                row.find("ul", {"class": "list-unstyled"})
                .find("span", {"class": "price-per"})
                .text.strip()
                .split(" ")[0]
                .strip("($")
            )
            result["cpr"] = f"{cpr:.2f}"
            self.results.append(result)
        else:
            return
