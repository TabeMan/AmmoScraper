import re
import traceback
import logging
from bs4 import BeautifulSoup

from bot.base.base_scraper import BaseScraper
from bot.base.get_manufacturer import get_manufacturer

logger = logging.getLogger(__name__)


class BulldoggunsScraper(BaseScraper):
    """
    A scraper for the Bulldog Guns & Ammo website.

    Inherits from BaseScraper.
    """

    def __init__(self, url):
        """
        Initializes the BulldoggunsScraper with a URL.

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
            page.goto(self.url, wait_until="networkidle")
            page.wait_for_selector("div#content-backdrop")
            soup = BeautifulSoup(page.content(), "html.parser")
            self.process_page(soup)
            if soup.find("ul", {"class": "pagination"}).find("a", {"rel": "next"}):
                url = (
                    soup.find("ul", {"class": "pagination"})
                    .find("a", {"rel": "next"})
                    .get("href")
                )
                if url:
                    self.url = f"https://www.bulldogguns.us{url}"
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
                soup.find("div", {"class": "item-container"})
                .find("div", {"class": "col-lg-10 col-md-9"})
                .find_all(
                    "div",
                    {"class": "item no-js-link col-lg-3 col-md-4 col-sm-4 col-xs-12"},
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
        result["title"] = row.find("div", {"class": "description"}).text.strip()
        result["steel_casing"] = "steel" in result["title"].lower()
        result["remanufactured"] = "reman" in result["title"].lower()
        manufacturer = (
            row.find("div", {"class": "description"})
            .find("span", {"class": "small"})
            .text.strip()
        )
        result["manufacturer"] = get_manufacturer(manufacturer)
        if not result["manufacturer"]:
            return
        link = row.find("a").get("href")
        result["link"] = f"https://www.bulldogguns.us{link}"
        result["image"] = row.find("img").get("src")
        result["website"] = "Bulldog Guns & Ammo"

        if row.find("div", {"class": "price"}).find("span", {"class": "text-success"}):
            original_price = float(
                row.find("div", {"class": "price"})
                .find("span", {"class": "text-success"})
                .text.strip("$")
            )
        else:
            original_price = float(row.find("div", {"class": "price"}).text.strip("$"))
        result["original_price"] = f"{original_price:.2f}"

        match = re.search(
            r"(\d+[\d,]*)\s*(round|pack|rd|pk|-pack)", result["title"], re.IGNORECASE
        )
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
