import re
import traceback
import logging
from bs4 import BeautifulSoup

from bot.base.base_scraper import BaseScraper
from bot.base.get_manufacturer import get_manufacturer

logger = logging.getLogger(__name__)


class KirammoScraper(BaseScraper):
    """
    A scraper for the Kir Ammo website.

    Inherits from BaseScraper.
    """

    def __init__(self, url):
        """
        Initializes the KirammoScraper with a URL.

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
            try:
                page.goto(self.url)
            except Exception as e:
                print(f"Unexpected error: {e} - {self.url} during page.goto")
                traceback.print_exc()
                return
            page.wait_for_selector("main.container")
            soup = BeautifulSoup(page.content(), "html.parser")
            self.process_page(soup)
            pagination = page.query_selector("a.next.page-numbers")
            if pagination:
                url = (
                    soup.find("ul", {"class": "page-numbers"})
                    .find("a", {"class": "next page-numbers"})
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
                soup.find("div", {"class": "col-xs-12 col-lg-9"})
                .find("div", {"class": "products"})
                .find("div", {"class": "row"})
                .find_all(
                    "div",
                    {"class": "col-6"},
                )
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
        result["title"] = row.find(
            "h2", {"class": "woocommerce-loop-product__title"}
        ).text.strip()
        if ".223" in result["title"]:
            return
        result["steel_casing"] = "steel" in result["title"].lower()
        result["remanufactured"] = "reman" in result["title"].lower()
        result["manufacturer"] = get_manufacturer(result["title"])
        if not result["manufacturer"]:
            return
        result["link"] = row.find("a").get("href")
        result["image"] = row.find("img").get("src")
        result["website"] = "Kir Ammo"

        price_text = row.find("span", {"class": "price"}).find_all("bdi")
        if len(price_text) == 1:
            original_price = float(price_text[0].text.strip("$"))
        elif len(price_text) == 2:
            original_price = float(price_text[1].text.strip("$"))
        result["original_price"] = f"{original_price:.2f}"

        match = re.search(r"(\d+[\d,]*)\s*(round|rd)", result["title"], re.IGNORECASE)
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
