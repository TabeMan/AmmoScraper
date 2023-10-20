import re
import traceback
import logging
from bs4 import BeautifulSoup

from bot.base.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class TundramichiganScraper(BaseScraper):
    """
    A scraper for the Tundra Michigan website.

    Inherits from BaseScraper.
    """

    def __init__(self, url):
        """
        Initializes the TundramichiganScraper with a URL.

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
        page.wait_for_selector("div.grid.grid--uniform")
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
            inner = soup.find("div", {"class": "grid grid--uniform"}).find_all(
                "div",
                {
                    "class": "product grid__item medium-up--one-third small--one-half slide-up-animation animated"
                },
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
            "div", {"class": "product__title product__title--card text-center"}
        ).text.strip()
        result["steel_casing"] = "steel" in result["title"].lower()
        result["remanufactured"] = "reman" in result["title"].lower()
        link = row.find("a", {"class": "product__image-wrapper"}).get("href")
        result["link"] = f"https://tundramichigan.com{link}"
        images = row.find("img", {"class": "product__image"}).get("srcset")
        result["image"] = f"https:{images.split(',')[3].lstrip().split(' ')[0]}"
        result["website"] = "Tundra Michigan"

        prices = row.find("div", {"class": "product__prices text-center"}).find_all(
            "span"
        )

        if len(prices) in [2, 4]:
            price_class = (
                "product__price" if len(prices) == 2 else "product__price--on-sale"
            )
            price = (
                row.find("div", {"class": "product__prices text-center"})
                .find("span", {"class": price_class})
                .text.split(" $")[1]
                .strip()
            )
            original_price = float(price)
            result["original_price"] = f"{original_price:.2f}"

            match = re.search(r"(\d+)\s*(rounds|rds|rd)", result["title"].lower())
            if match:
                rounds_per_case = int(match.group(1))
                cpr = original_price / rounds_per_case
                result["cpr"] = f"{cpr:.2f}"
                self.results.append(result)

        else:
            return
