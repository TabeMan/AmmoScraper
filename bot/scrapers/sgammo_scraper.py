import logging
import traceback
from bs4 import BeautifulSoup

from bot.base.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class SgammoScraper(BaseScraper):
    """
    A scraper for the SG Ammo website.

    Inherits from BaseScraper.
    """

    def __init__(self, url):
        """
        Initializes the SgammoScraper with a URL.

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
        page.wait_for_selector("div#main-wrapper")
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
            inner = []
            odd = (
                soup.find(
                    "table", {"class": "category-products sticky-enabled sticky-table"}
                )
                .find("tbody")
                .find_all("tr", {"class": "odd"})
            )
            inner.append(odd)
            even = (
                soup.find(
                    "table", {"class": "category-products sticky-enabled sticky-table"}
                )
                .find("tbody")
                .find_all("tr", {"class": "even"})
            )
            inner.append(even)
        except Exception as e:
            print(f"Unexpected error: {e} - {self.url} during process_page")
            traceback.print_exc()
            return

        for odd_or_even in inner:
            for row in odd_or_even:
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
        if row.find("td", {"class": "cell-qty"}).text.strip() == "0":
            return
        result["title"] = row.find("h2").text.strip()
        if "223" in result["title"].lower():
            return
        result["steel_casing"] = "steel" in result["title"].lower()
        result["remanufactured"] = "reman" in result["title"].lower()
        link = row.find("a").get("href")
        result["link"] = f"https://www.sgammo.com{link}"
        result["image"] = row.find(
            "img", {"class": "imagecache imagecache-product_list"}
        ).get("src")
        result["website"] = "SG Ammo"

        price_cell = row.find("td", {"class": "price-cell"}).find_all("span")
        original_price = float(price_cell[0].text.strip("$"))
        result["original_price"] = f"{original_price:.2f}"
        if len(price_cell) == 2:
            cpr = float(price_cell[1].text.strip("$"))
        elif len(price_cell) == 3:
            cpr = float(price_cell[2].text.strip("$"))
        else:
            return
        result["cpr"] = f"{cpr:.2f}"
        self.results.append(result)
