from bot.scrapers.sportsmansoutdoorsuperstore_scraper import (
    SportsmansoutdoorsuperstoreScraper,
)
from bot.scrapers.palmetto_scraper import PalmettoScraper
from bot.scrapers.targetsports_scraper import TargetsportsScraper
from bot.scrapers.ammunitiondepot_scraper import AmmunitiondepotScraper
from bot.scrapers.luckygunner_scraper import LuckygunnerScraper
from bot.scrapers.warehouse2a_scraper import Warehouse2aScraper
from bot.scrapers.nytactical_scraper import NytacticalScraper
from bot.scrapers.miwallcorp_scraper import MiwallcorporationScraper
from bot.scrapers.tundramichigan_scraper import TundramichiganScraper
from bot.scrapers.finleyammo_scraper import FinleyammoScraper
from bot.scrapers.cheapestammo_scraper import CheapestammoScraper
from bot.scrapers.southernmunitions_scraper import SouthernmunitionsScraper
from bot.scrapers.laxammo_scraper import LaxammoScraper
from bot.scrapers.mackspw_scraper import MackspwScraper
from bot.scrapers.lohmanarms_scraper import LohmanarmsScraper
from bot.scrapers.sgammo_scraper import SgammoScraper
from bot.scrapers.cheapammo_scraper import CheapammoScraper
from bot.scrapers.aeammo_scraper import AeammoScraper
from bot.scrapers.meadammo_scraper import MeadammoScraper
from bot.scrapers.tacticalshit_scraper import TacticalshitScraper
from bot.scrapers.lastshotaz_scraper import LastshotazScraper
from bot.scrapers.tulammozone_scraper import TulammozoneScraper
from bot.scrapers.outdoorlimited_scraper import OutdoorlimitedScraper
from bot.scrapers.flipammo_scraper import FlipammoScraper
from bot.scrapers.canoeclubusa_scraper import CanoeclubusaScraper
from bot.scrapers.cabelas_scraper import CabelasScraper
from bot.scrapers.ammunitiontogo_scraper import AmmunitiontogoScraper
from bot.scrapers.ammoman_scraper import AmmomanScraper
from bot.scrapers.bulkammo_scraper import BulkammoScraper
from bot.scrapers.cheaperthandirt_scraper import CheaperthandirtScraper
from bot.scrapers.ammodotcom_scraper import AmmodotcomScraper
from bot.scrapers.topgunammo_scraper import TopgunammoScraper
from bot.scrapers.agbammo_scraper import AgbammoScraper
from bot.scrapers.gunprime_scraper import GunprimeScraper
from bot.scrapers.gunbuyer_scraper import GunbuyerScraper
from bot.scrapers.ables_scraper import AblesScraper
from bot.scrapers.bulkmunitions_scraper import BulkmunitionsScraper
from bot.scrapers.freedommunitions_scraper import FreedommunitionsScraper
from bot.scrapers.gunmagwarehouse_scraper import GunmagwarehouseScraper
from bot.scrapers.globalordnance_scraper import GlobalordnanceScraper
from bot.scrapers.huntshootfish_scraper import HuntshootfishScraper
from bot.scrapers.blackoutclub300_scraper import Blackoutclub300Scraper
from bot.scrapers.floridagunexchange_scraper import FloridagunexchangeScraper
from bot.scrapers.americanmarksman_scraper import AmericanmarksmanScraper
from bot.scrapers.ammo2_scraper import Ammo2Scraper
from bot.scrapers.buckinghorseoutpost_scraper import BuckinghorseoutpostScraper
from bot.scrapers.caliberarmory_scraper import CaliberarmoryScraper
from bot.scrapers.venturamunitions_scraper import VenturamunitionsScraper
from bot.scrapers.jgsales_scraper import JgsalesScraper
from bot.scrapers.greentop_scraper import GreentopScraper
from bot.scrapers.natchez_scraper import NatchezScraper
from bot.scrapers.alamoammo_scraper import AlamoammoScraper
from bot.scrapers.grabagun_scraper import GrabagunScraper
from bot.scrapers.opticsplanet_scraper import OpticsplanetScraper
from bot.scrapers.rivertownmunitions_scrapr import RivertownmunitionsScraper
from bot.scrapers.surplusammo_scraper import SurplusammoScraper
from bot.scrapers.kirammo_scraper import KirammoScraper
from bot.scrapers.midsouthshooters_scraper import MidsouthshootersScraper
from bot.scrapers.sportsmanfulfillment_scraper import SportsmanfulfillmentScraper
from bot.scrapers.gunrunusa_scraper import GunrunusaScraper
from bot.scrapers.sportsmansfinest_scraper import SportsmansfinestScraper
from bot.scrapers.stunomma_scraper import StunommasportsScraper
from bot.scrapers.gunnersoutlet_scraper import GunnersoutletScraper
from bot.scrapers.thearmory_scraper import ThearmoryScraper
from bot.scrapers.basspro_scraper import BassproScraper
from bot.scrapers.ammomart_scraper import AmmomartScraper
from bot.scrapers.getloadedpa_scraper import GetloadedpaScraper
from bot.scrapers.botach_scraper import BotachScraper
from bot.scrapers.abguns_scraper import AbgunsScraper
from bot.scrapers.ammo4patriots_scraper import Ammo4patriotsScraper
from bot.scrapers.ammobros_scraper import AmmobrosScraper
from bot.scrapers.ammocitysupply_scraper import AmmocitysupplyScraper
from bot.scrapers.ammofast_scraper import AmmofastScraper
from bot.scrapers.ammojoy_scraper import AmmojoyScraper
from bot.scrapers.astrasports_scraper import AstrasportsScraper
from bot.scrapers.ammunitionplanet_scraper import AmmunitionplanetScraper
from bot.scrapers.bulldogguns_scraper import BulldoggunsScraper
from bot.scrapers.conkeysfirearms_scraper import ConkeysfirearmsScraper
from bot.scrapers.collectorrifleandammo_scraper import CollectorrifleandammoScraper
from bot.scrapers.clarkarmory_scraper import ClarkarmoryScraper
from bot.scrapers.ammosupplywarehouse_scraper import AmmosupplywarehouseScraper

# Won't load items. Gives no results.
# from bot.scrapers.gordyandsons_scraper import GordyandsonsScraper


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
