import traceback
import logging
from bs4 import BeautifulSoup

from bot.base.base_scraper import BaseScraper
from bot.base.get_manufacturer import get_manufacturer

logger = logging.getLogger(__name__)


class GunmagwarehouseScraper(BaseScraper):
    """
    A scraper for the Gun Mag Warehouse website.

    Inherits from BaseScraper.
    """

    def __init__(self, url):
        """
        Initializes the GunmagwarehouseScraper with a URL.

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
        page.wait_for_selector("div.page")
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
                soup.find("div", {"class": "category-products"})
                .find(
                    "ul",
                    {"class": "products-grid row"},
                )
                .find_all("li", {"class": "item col-xs-6 col-sm-4 col-lg-3"})
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
            row.find("h2", {"class": "product-name"}).find("a").text.strip()
        )
        result["steel_casing"] = "steel" in result["title"].lower()
        result["remanufactured"] = "reman" in result["title"].lower()
        result["manufacturer"] = get_manufacturer(result["title"])
        if not result["manufacturer"]:
            return
        result["link"] = row.find("a").get("href")
        result["image"] = row.find("img").get("src")
        result["website"] = "Gun Mag Warehouse"

        price_box = row.find("div", {"class": "details-area"}).find(
            "div", {"class": "price-box"}
        )
        if price_box.find("p", {"class": "special-price"}):
            original_price = float(
                price_box.find("p", {"class": "special-price"})
                .find("span", {"class": "price"})
                .text.strip()
                .strip("$")
            )
        else:
            original_price = float(
                price_box.find("span", {"class": "regular-price"})
                .find("span", {"class": "price"})
                .text.strip()
                .strip("$")
            )
        result["original_price"] = f"{original_price:.2f}"
        cpr = float(
            row.find("div", {"class": "price-per-round"})
            .text.strip()
            .split(" ")[0]
            .strip("($")
        )
        result["cpr"] = f"{cpr:.2f}"
        self.results.append(result)
