import logging
import traceback
from bs4 import BeautifulSoup

from bot.base.base_scraper import BaseScraper
from bot.base.get_manufacturer import get_manufacturer

logger = logging.getLogger(__name__)


class LuckygunnerScraper(BaseScraper):
    """
    A scraper for the Lucky Gunner website.

    Inherits from BaseScraper.
    """

    def __init__(self, url):
        """
        Initializes the LuckygunnerScraper with a URL.

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
        page.wait_for_selector("div.full-width-wrapper")
        soup = BeautifulSoup(page.content(), "html.parser")
        self.process_page(soup)

    def process_page(self, soup):
        """
        Processes the page content to extract product listings.

        Args:
            soup (BeautifulSoup object): The parsed HTML of the page.
        """
        try:
            inner = soup.find("ol", {"class": "products-list"}).find_all(
                "li", {"class": "item"}
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
            row.find("h3", {"class": "product-name"}).find("a").text.strip()
        )
        result["steel_casing"] = "steel" in result["title"].lower()
        result["remanufactured"] = "reman" in result["title"].lower()
        result["manufacturer"] = get_manufacturer(result["title"])
        if not result["manufacturer"]:
            return
        result["link"] = row.find("a", {"class": "product-image"}).get("href")
        result["image"] = row.find("a", {"class": "product-image"}).find("img")["src"]
        result["website"] = "Lucky Gunner"

        price_box_count = len(row.find("div", {"class": "price-box"}).find_all("span"))
        if price_box_count == 1:
            original_price_text = (
                row.find("div", {"class": "price-box"})
                .find("span", {"class": "regular-price"})
                .text.strip()
            )
        elif price_box_count == 4:
            original_price_text = (
                row.find("p", {"class": "special-price"})
                .find("span", {"class": "price"})
                .text.strip()
            )
        else:
            return
        original_price = float(original_price_text.replace("$", ""))
        result["original_price"] = f"{original_price:.2f}"

        cpr = row.find("p", {"class": "cprc"}).text.split(" ")[0]
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
