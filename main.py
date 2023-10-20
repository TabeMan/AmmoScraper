import pprint
from decouple import config

from bot.base.get_scraper import get_scraper
from bot.base.base_scraper import ScraperBot


CALIBERS = [
    "9mm Luger",
    # "5.56x45 NATO",
    # "22 LR",
    # "380 Auto",
    # "45 ACP",
    # "38 Special",
    # "7.62x39mm",
]


def run_scraper_for_caliber(caliber):
    """
    Runs the scraper for a specific caliber.

    This function fetches the URL configurations for the given caliber,
    initializes the scraper objects, and scrapes the data for ammo deals.

    :param caliber: The caliber for which to scrape ammo deals.
    """
    # scraper = JgsalesScraper(
    #     "https://www.jgsales.com/product-category/ammunition/ammo-for-rifles/?count=150&paged=&filter_caliber=223"
    # )
    # bot = ScraperBot(scrapers=[scraper])
    # Converting the caliber name to the format used in the environment variable keys
    config_caliber_name = caliber.upper().replace(" ", "_").replace(".", "")
    url_key = f"MM_{config_caliber_name}_URLS"

    # Parsing the URLs from the environment variable
    urls_list = config(url_key, "").split(",")
    urls_dict = dict(item.split(";") for item in urls_list)

    # Initializing the scraper objects
    scrapers = []
    for website, url in urls_dict.items():
        scrapers.append(get_scraper(website, url))

    # Initializing the ScraperBot with the scraper objects
    bot = ScraperBot(scrapers=scrapers)
    # Running the scrapers and printing the scraped data
    data = bot.run()
    pprint.pprint(data)
    print(f"Found {len(data)} deals for {caliber}")


def main():
    """
    Main function to run the scraper for each caliber in the CALIBERS list.
    """
    for caliber in CALIBERS:
        run_scraper_for_caliber(caliber)


if __name__ == "__main__":
    main()
