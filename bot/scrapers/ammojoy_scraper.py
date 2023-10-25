import traceback
import logging
from bs4 import BeautifulSoup

from bot.base.base_scraper import BaseScraper
from bot.base.get_manufacturer import get_manufacturer

logger = logging.getLogger(__name__)


class AmmojoyScraper(BaseScraper):
    """
    A scraper for the Ammo Joy website.

    Inherits from BaseScraper.
    """

    def __init__(self, url):
        """
        Initializes the AmmojoyScraper with a URL.

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
        page.wait_for_selector("main#site-main")
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
            inner = soup.find("div", {"class": "mz-grid"}).find_all(
                "div", {"class": "mz-grid-item"}
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
        # Skip if the product has no image
        if row.find("figure", {"class": "productitem--image"}).find(
            "svg", {"class": "placeholder--image"}
        ):
            return
        result["title"] = row.find("h2", {"class": "productitem--title"}).text.strip()
        result["steel_casing"] = "steel" in result["title"].lower()
        result["remanufactured"] = "reman" in result["title"].lower()
        manufacturer = row.find("span", {"class": "productitem--vendor"}).text.strip()
        result["manufacturer"] = get_manufacturer(manufacturer)
        if not result["manufacturer"]:
            return
        link = row.find("a").get("href")
        result["link"] = f"https://www.ammojoy.com{link}"
        image = row.find("img").get("src")
        result["image"] = f"https:{image}"
        result["website"] = "Ammo Joy"

        original_price = float(
            row.find("div", {"class": "price__current"})
            .find("span", {"class": "money"})
            .text.strip()
            .strip("$")
        )
        result["original_price"] = f"{original_price:.2f}"

        cpr = float(
            row.find("div", {"class": "productitem--info"})
            .find("p")
            .text.strip()
            .split("$")[1]
        )
        result["cpr"] = f"{cpr:.2f}"
        self.results.append(result)
