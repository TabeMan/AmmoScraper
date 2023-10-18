import pprint
from decouple import config

from bot.base.scrapers import get_scraper
from bot.base.base_scraper import ScraperBot


CALIBERS = [
    "9mm Luger",
    "5.56x45 NATO",
    "22 LR",
    "380 Auto",
    "45 ACP",
    "38 Special",
    "7.62x39mm",
]


def run_scraper_for_caliber(caliber):
    config_caliber_name = caliber.upper().replace(" ", "_").replace(".", "")
    url_key = f"MM_{config_caliber_name}_URLS"
    urls_list = config(url_key, "").split(",")
    urls_dict = dict(item.split(";") for item in urls_list)

    scrapers = []
    for website, url in urls_dict.items():
        scrapers.append(get_scraper(website, url))
    bot = ScraperBot(scrapers=scrapers)
    # scraper = Blackoutclub300Scraper(
    #     "https://www.300blackoutclub.com/556x45mm-NATO_c_15.html"
    # )
    # bot = ScraperBot(scrapers=[scraper])
    data = bot.run()
    pprint.pprint(data)
    print(f"Found {len(data)} deals for {caliber}")


def main():
    for caliber in CALIBERS:
        run_scraper_for_caliber(caliber)


if __name__ == "__main__":
    main()
