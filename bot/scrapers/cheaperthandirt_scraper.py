import re
import traceback
import logging
from bs4 import BeautifulSoup

from bot.base.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class CheaperthandirtScraper(BaseScraper):
    """
    A scraper for the Cheaper Than Dirt website.

    Inherits from BaseScraper.
    """

    def __init__(self, url):
        """
        Initializes the CheaperthandirtScraper with a URL.

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

        # Define the scrolling function
        def scroll_page():
            return page.eval_on_selector(
                "body",
                """body => {
                window.scrollBy(0, window.innerHeight);
                return window.scrollY;
            }""",
            )

        # Scroll incrementally, waiting for a bit between each scroll.
        last_position = 0
        while True:
            new_position = scroll_page()
            if new_position == last_position:
                # Stop scrolling when we reach the bottom of the page
                break
            last_position = new_position
            page.wait_for_timeout(800)
        soup = BeautifulSoup(page.content(), "html.parser")
        self.process_page(soup)

    def process_page(self, soup):
        """
        Processes the page content to extract product listings.

        Args:
            soup (BeautifulSoup object): The parsed HTML of the page.
        """
        try:
            inner = (
                soup.find(
                    "div",
                    {"class": "page-content"},
                )
                .find("div", {"class": "blm-category__results productGrid"})
                .find_all("li", {"class": "product"})
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
        result["title"] = row.find("h3").text.strip()
        result["steel_casing"] = "steel" in result["title"].lower()
        result["remanufactured"] = "reman" in result["title"].lower()
        result["link"] = row.find("a").get("href")
        result["image"] = row.find("img").get("src")
        result["website"] = "Cheaper Than Dirt"

        original_price = row.find("span", {"class": "price price--withoutTax"}).text
        if "-" in original_price:
            return
        else:
            original_price = float(original_price.strip().strip("$"))
        result["original_price"] = f"{original_price:.2f}"

        match = re.search(r"(\d+)\s*(round)", result["title"].lower())
        if match:
            if int(match.group(1)) == 0:
                return
            rounds_per_case = int(match.group(1))
            cpr = original_price / rounds_per_case
            result["cpr"] = f"{cpr:.2f}"
            self.results.append(result)
        else:
            return