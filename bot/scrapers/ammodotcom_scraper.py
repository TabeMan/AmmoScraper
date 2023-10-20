import traceback
import logging
from bs4 import BeautifulSoup

from bot.base.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class AmmodotcomScraper(BaseScraper):
    """
    A scraper for the Ammo.com website.

    Inherits from BaseScraper.
    """

    def __init__(self, url):
        """
        Initializes the AmmodotcomScraper with a URL.

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
        page.wait_for_selector("div.l-page")
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
                soup.find("div", {"id": "catalog-listing"})
                .find(
                    "ol",
                    {"class": "b-category-product-list"},
                )
                .find_all("li", {"class": "b-product-list-item"})
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
            "h2", {"class": "b-product-list-item__product-name"}
        ).text.strip()
        result["steel_casing"] = "steel" in result["title"].lower()
        result["remanufactured"] = "reman" in result["title"].lower()
        result["link"] = (
            row.find("div", {"class": "b-product-list-item__bar-buttons"})
            .find("a")
            .get("href")
        )
        result["image"] = row.find("img").get("src")
        result["website"] = "Ammo.com"

        if row.find("p", {"class": "b-price-sale__special special-price"}):
            original_price = float(
                row.find("p", {"class": "b-price-sale__special special-price"})
                .find("span", {"class": "price"})
                .text.strip()
                .strip("$")
            )
        else:
            original_price = float(
                row.find("div", {"class": "b-price-regular"})
                .find("span", {"class": "price"})
                .text.lstrip()
                .strip("$")
            )
        result["original_price"] = f"{original_price:.2f}"

        cpr_box = (
            row.find("div", {"class": "b-product-list-item__bottom-bar"})
            .find("ul", {"class": "b-product-list-item__attributes-short"})
            .find_all("li")
        )
        cpr = cpr_box[1].text.strip().split(" ")[0]
        if "\u00A2" in cpr:
            cpr = int(cpr.split(".")[0])
            if cpr < 10:
                result["cpr"] = f"0.0{cpr}"
            else:
                result["cpr"] = f"0.{cpr}"
        elif "$" in cpr:
            cpr = float(cpr.strip("$"))
            result["cpr"] = f"{cpr:.2f}"
        else:
            return
        self.results.append(result)
