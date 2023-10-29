import traceback
import logging
from bs4 import BeautifulSoup

from bot.base.base_scraper import BaseScraper
from bot.base.get_manufacturer import get_manufacturer

logger = logging.getLogger(__name__)


class AmmunitiontogoScraper(BaseScraper):
    """
    A scraper for the Ammunition To Go website.

    Inherits from BaseScraper.
    """

    def __init__(self, url):
        """
        Initializes the TacticalshitScraper with a URL.

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
        page.wait_for_selector("div.l-page__nav")
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
            inner = soup.find(
                "ol", {"class": "p-category__products b-product-list products-list"}
            ).find_all(
                "li",
                {"class": "b-product-list__item b-product-item item"},
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
        result["title"] = (
            row.find("a", {"class": "b-product-item__name product-name"})
            .find("span")
            .text.strip()
        )
        if "223" in result["title"].lower():
            return
        result["steel_casing"] = "steel" in result["title"].lower()
        result["remanufactured"] = "reman" in result["title"].lower()
        result["manufacturer"] = get_manufacturer(result["title"])
        if not result["manufacturer"]:
            return
        result["link"] = row.find("a").get("href")
        result["image"] = row.find("img").get("src")
        result["website"] = "Ammunition To Go"

        if row.find("p", {"class": "b-price_sale__special special-price"}):
            original_price = float(
                row.find("p", {"class": "b-price_sale__special special-price"})
                .find("span", {"class": "price"})
                .text.lstrip()
                .strip("$")
            )
        else:
            original_price = float(
                row.find("div", {"class": "b-price b-price_regular"})
                .find("span", {"class": "price"})
                .text.lstrip()
                .strip("$")
            )
        result["original_price"] = f"{original_price:.2f}"

        cpr = float(
            row.find("div", {"class": "b-price b-price_ppr"})
            .text.lstrip()
            .split("/")[0]
            .strip("$")
        )
        result["cpr"] = f"{cpr:.2f}"
        self.results.append(result)
