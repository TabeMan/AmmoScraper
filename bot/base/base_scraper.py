import logging
from playwright.sync_api import sync_playwright


logger = logging.getLogger(__name__)


class BaseScraper:
    """
    Base class for a web scraper.

    Attributes:
        url (str): The URL to be scraped.
        results (list): A list to hold the scraped data.
        browser (object): The browser object for web scraping.
    """

    def __init__(self, url):
        """
        Initializes the BaseScraper with a URL.

        Args:
            url (str): The URL to be scraped.
        """
        self.url = url
        self.results = []
        self.browser = None

    def scrape(self):
        """
        Abstract method to be implemented by subclasses to define
        the scraping behavior.

        Raises:
            NotImplementedError: If not overridden by a subclass.
        """
        raise NotImplementedError


class ScraperBot:
    """
    Orchestrates the execution of multiple scrapers.

    Attributes:
        scrapers (list): A list of scraper objects.
    """

    def __init__(self, scrapers=[]):
        """
        Initializes the ScraperBot with a list of scraper objects.

        Args:
            scrapers (list, optional): A list of scraper objects.
        """
        self.scrapers = scrapers

    def run(self):
        """
        Executes all the scrapers and aggregates the results.

        Returns:
            list: A list of dictionaries containing the scraped data.
        """
        all_results = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                extra_http_headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "en-US,en;q=0.5",
                    # "Upgrade-Insecure-Requests": "1",
                    "Connection": "keep-alive",
                },
                viewport={"width": 1920, "height": 1080},
            )

            for scraper in self.scrapers:
                scraper.browser = context
                scraper.scrape()
                all_results.extend(scraper.results)

            browser.close()

        return all_results
