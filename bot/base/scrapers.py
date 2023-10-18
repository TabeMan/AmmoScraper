from bot.palmetto_scraper import PalmettoScraper
from bot.targetsports_scraper import TargetsportsScraper
from bot.ammunitiondepot_scraper import AmmunitiondepotScraper
from bot.luckygunner_scraper import LuckygunnerScraper
from bot.warehouse2a_scraper import Warehouse2aScraper
from bot.nytactical_scraper import NytacticalScraper
from bot.miwallcorp_scraper import MiwallcorporationScraper
from bot.tundramichigan_scraper import TundramichiganScraper
from bot.finleyammo_scraper import FinleyammoScraper
from bot.cheapestammo_scraper import CheapestammoScraper
from bot.southernmunitions_scraper import SouthernmunitionsScraper
from bot.laxammo_scraper import LaxammoScraper
from bot.mackspw_scraper import MackspwScraper
from bot.lohmanarms_scraper import LohmanarmsScraper
from bot.sgammo_scraper import SgammoScraper
from bot.cheapammo_scraper import CheapammoScraper
from bot.aeammo_scraper import AeammoScraper
from bot.meadammo_scraper import MeadammoScraper
from bot.tacticalshit_scraper import TacticalshitScraper
from bot.lastshotaz_scraper import LastshotazScraper
from bot.tulammozone_scraper import TulammozoneScraper
from bot.outdoorlimited_scraper import OutdoorlimitedScraper
from bot.flipammo_scraper import FlipammoScraper
from bot.canoeclubusa_scraper import CanoeclubusaScraper
from bot.cabelas_scraper import CabelasScraper
from bot.ammunitiontogo_scraper import AmmunitiontogoScraper
from bot.ammoman_scraper import AmmomanScraper
from bot.bulkammo_scraper import BulkammoScraper
from bot.cheaperthandirt_scraper import CheaperthandirtScraper
from bot.ammodotcom_scraper import AmmodotcomScraper
from bot.topgunammo_scraper import TopgunammoScraper
from bot.agbammo_scraper import AgbammoScraper
from bot.gunprime_scraper import GunprimeScraper
from bot.gunbuyer_scraper import GunbuyerScraper
from bot.ables_scraper import AblesScraper
from bot.bulkmunitions_scraper import BulkmunitionsScraper
from bot.freedommunitions_scraper import FreedommunitionsScraper
from bot.gunmagwarehouse_scraper import GunmagwarehouseScraper
from bot.sportsmansoutdoorsuperstore_scraper import SportsmansoutdoorsuperstoreScraper
from bot.globalordnance_scraper import GlobalordnanceScraper
from bot.huntshootfish_scraper import HuntshootfishScraper
from bot.blackoutclub300_scraper import Blackoutclub300Scraper


def get_scraper(website_name, url):
    """
    Returns an instance of the scraper class corresponding to the given website name.

    :param website_name: The name of the website for which to create a scraper.
    :param url: The URL at which to scrape data.
    :return: An instance of the appropriate scraper class.
    :raises ValueError: If no scraper class is found for the given website name.
    """
    scraper_class = globals().get(f"{website_name.capitalize()}Scraper")
    if scraper_class is None:
        raise ValueError(f"No scraper found for website: {website_name}")
    return scraper_class(url)
