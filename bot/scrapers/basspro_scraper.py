import traceback
import logging
from bs4 import BeautifulSoup

from bot.base.base_scraper import BaseScraper
from bot.base.get_manufacturer import get_manufacturer

logger = logging.getLogger(__name__)


class BassproScraper(BaseScraper):
    """
    A scraper for the Bass Pro website.

    Inherits from BaseScraper.
    """

    def __init__(self, url):
        """
        Initializes the BassproScraper with a URL.

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
        try:
            page.goto(self.url)
            page.wait_for_selector("img", state="attached")
        except Exception as e:
            print(f"Unexpected error: {e} - {self.url} during page.goto")
            traceback.print_exc()
            return
        soup = BeautifulSoup(page.content(), "html.parser")
        self.process_page(soup)

    def process_page(self, soup):
        """
        Processes the page content to extract product listings.

        Args:
            soup (BeautifulSoup object): The parsed HTML of the page.
        """
        try:
            inner = soup.find("div", {"class": "styles_ResultsList__FA8dO"}).find_all(
                "div",
                {"class": "styles_ResultItem__DHSnb"},
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
        result["title"] = row.find("a").get("title")
        result["steel_casing"] = "steel" in result["title"].lower()
        result["remanufactured"] = "reman" in result["title"].lower()
        result["manufacturer"] = get_manufacturer(result["title"])
        if not result["manufacturer"]:
            return
        link = row.find("a").get("href")
        result["link"] = f"https://www.basspro.com{link}"
        result["image"] = (
            row.find("div", {"class": "styles_ResultItemThumbnail__QKxlc undefined"})
            .find("img")
            .get("src")
        )
        if not result["image"]:
            return
        result["website"] = "Bass Pro"

        original_price_text = row.find(
            "div", {"class": "styles_PriceContainer__TySzg"}
        ).find_all("span")
        if len(original_price_text) == 1:
            original_price = float(
                row.find("div", {"class": "styles_PriceContainer__TySzg"})
                .find("span", {"class": "styles_ProductPrice__KUcFU"})
                .text.strip("$")
            )
        elif len(original_price_text) == 3:
            if original_price_text[1].text.strip() == "-":
                return
            original_price = float(
                row.find("div", {"class": "styles_PriceContainer__TySzg"})
                .find("span", {"class": "styles_ProductPrice__Z1hB9"})
                .text.strip("$")
            )
        else:
            return
        result["original_price"] = f"{original_price:.2f}"

        if row.find("div", {"class": "styles_PricePerRoundContainer__GNmAp"}):
            cpr = (
                row.find("div", {"class": "styles_PricePerRoundContainer__GNmAp"})
                .text.split("/")[0]
                .strip()
            )
            if "\u00A2" in cpr:
                cpr = int(cpr.strip("\u00A2"))
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
        else:
            return
