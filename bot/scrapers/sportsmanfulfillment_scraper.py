import re
import traceback
import logging
from bs4 import BeautifulSoup

from bot.base.base_scraper import BaseScraper
from bot.base.get_manufacturer import get_manufacturer

logger = logging.getLogger(__name__)


class SportsmanfulfillmentScraper(BaseScraper):
    """
    A scraper for the Sportsman Fulfillment website.

    Inherits from BaseScraper.
    """

    def __init__(self, url):
        """
        Initializes the SportsmanfulfillmentScraper with a URL.

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
        page.wait_for_selector("div.body")
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
                "div", {"class": "productBlockContainer columns-4"}
            ).find_all("div", {"class": "prod-item"})
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
        result["title"] = row.find("h3", {"class": "prod-name"}).text.strip()
        result["steel_casing"] = "steel" in result["title"].lower()
        result["remanufactured"] = "reman" in result["title"].lower()
        manufacturer = row.find("p", {"class": "prod-brand"}).text.strip()
        result["manufacturer"] = get_manufacturer(manufacturer.capitalize())
        if not result["manufacturer"]:
            return
        link = row.find("a").get("href")
        result["link"] = f"https://www.sportsmanfulfillment.com{link}"
        result["image"] = row.find("img", {"class": "card-image"}).get("src")
        result["website"] = "Sportsman Fulfillment"

        if row.find("span", {"class": "price price--withoutTax price--sale-price"}):
            price_text = row.find(
                "span", {"class": "price price--withoutTax price--sale-price"}
            ).text.strip()
            price_text = price_text.replace("\xa0", "").strip("$")
            original_price = float(price_text)
        else:
            price_text = row.find(
                "span", {"class": "price price--withoutTax"}
            ).text.strip()
            price_text = price_text.replace("\xa0", "").strip("$")
            original_price = float(price_text)
        result["original_price"] = f"{original_price:.2f}"

        match = re.search(r"(\d+[\d,]*)\s*(round)", result["title"], re.IGNORECASE)
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
