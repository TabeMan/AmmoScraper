import traceback
import logging
from bs4 import BeautifulSoup

from bot.base.base_scraper import BaseScraper
from bot.base.get_manufacturer import get_manufacturer

logger = logging.getLogger(__name__)


class OpticsplanetScraper(BaseScraper):
    """
    A scraper for the Optics Planet website.

    Inherits from BaseScraper.
    """

    def __init__(self, url):
        """
        Initializes the OpticsplanetScraper with a URL.

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
        page.goto(self.url)
        page.wait_for_selector("div#list-page-main")
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
                "div",
                {
                    "class": "grid-c__main products qa-grid-c__main op-plugin op-widget-initialized"
                },
            ).find_all(
                "div",
                {"class": "grid"},
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
        result["title"] = row.find("span", {"class": "grid__text"}).text.strip()
        if "223" in result["title"]:
            return
        result["steel_casing"] = "steel" in result["title"].lower()
        result["remanufactured"] = "reman" in result["title"].lower()
        result["manufacturer"] = get_manufacturer(result["title"])
        if not result["manufacturer"]:
            return
        result["link"] = row.find("a").get("href")
        result["image"] = row.find("img").get("src")
        result["website"] = "Optics Planet"

        original_price = float(
            row.find("span", {"class": "variant-price-dollars"}).text.strip().strip("$")
        )
        result["original_price"] = f"{original_price:.2f}"

        cpr_text = (
            row.find("span", {"class": "grid__save-text"})
            .text.strip()
            .split("/")[0]
            .strip("$")
        )
        if "-" in cpr_text:
            cpr_text = cpr_text.split("-")[0].strip().strip("$")
        cpr = float(cpr_text)
        result["cpr"] = f"{cpr:.2f}"
        self.results.append(result)
