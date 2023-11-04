import re
import traceback
import logging
from bs4 import BeautifulSoup

from bot.base.base_scraper import BaseScraper
from bot.base.get_manufacturer import get_manufacturer

logger = logging.getLogger(__name__)


class ThearmoryScraper(BaseScraper):
    """
    A scraper for the The Armory website.

    Inherits from BaseScraper.
    """

    def __init__(self, url):
        """
        Initializes the ThearmoryScraper with a URL.

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
        try:
            page.goto(self.url)
        except Exception as e:
            print(f"Unexpected error: {e} - {self.url} during page.goto")
            traceback.print_exc()
            return
        page.wait_for_selector("body#main")
        soup = BeautifulSoup(page.content(), "html.parser")
        self.process_page(soup)

    def process_page(self, soup):
        """
        Processes the page content to extract product listings.

        Args:
            soup (BeautifulSoup object): The parsed HTML of the page.
        """
        try:
            inner = soup.find("ul", {"class": "bb-loopheight"}).find_all(
                "li", {"class": "prod bb-matchheight"}
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
        if row.find("input", {"class": "bb-prodaddtxt"}).get("value") == "Notify Me":
            return
        if row.find("table", {"class": "qp_header"}):
            return
        result["title"] = row.find(
            "a", {"class": "bb-prodnme Bold Normal"}
        ).text.strip()
        if "223" in result["title"]:
            return
        result["steel_casing"] = "steel" in result["title"].lower()
        result["remanufactured"] = "reman" in result["title"].lower()
        result["manufacturer"] = get_manufacturer(result["title"])
        if not result["manufacturer"]:
            return
        result["image"] = row.find("img").get("src")
        result["link"] = row.find("a", {"class": "bb-prodimg"}).get("href")
        result["website"] = "The Armory"

        if row.find("span", {"class": "bb-prodprcsale"}):
            original_price = float(
                row.find("span", {"class": "bb-prodprcsale"}).text.strip("$")
            )
        else:
            original_price = float(
                row.find("span", {"class": "bb-prodprc"}).text.strip("$")
            )
        result["original_price"] = f"{original_price:.2f}"

        match = re.search(r"(\d+[\d,]*)\s*(round|rd)", result["title"], re.IGNORECASE)
        if match:
            rounds_per_case_str = match.group(1)
            rounds_per_case = int(rounds_per_case_str)
            if rounds_per_case == 0:
                return
            cpr = original_price / rounds_per_case
            result["cpr"] = f"{cpr:.2f}"
            self.results.append(result)
        else:
            return
