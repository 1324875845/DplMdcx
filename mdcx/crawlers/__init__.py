from collections.abc import Callable

from ..config.models import Website
from . import (
    airav,
    airav_cc,
    avsex,
    avsox,
    cableav,
    cnmdb,
    dahlia,
    faleno,
    fantastica,
    freejavbt,
    getchu,
    getchu_dmm,
    giga,
    hdouban,
    hscangku,
    iqqtv_new,
    jav321,
    javday,
    javlibrary_new,
    kin8,
    love6,
    lulubar,
    madouqu,
    mdtv,
    mmtv,
    mywife,
    official,
    prestige,
    theporndb,
    xcity,
)
from .base import get_crawler, register_crawler
from .base.compat import get_v1_crawler, register_v1_crawler
from .dmm_new import DmmCrawler
from .fc2_new import Fc2Crawler
from .fc2club_new import Fc2ClubCrawler
from .fc2hub_new import Fc2HubCrawler
from .fc2ppvdb_new import Fc2PpvdbCrawler
from .javbus_new import JavbusCrawler
from .javdb_new import JavdbCrawler
from .mgstage_new import MgstageCrawler

CRAWLER_FUNCS: list[tuple[Website, Callable]] = [
    (Website.MMTV, mmtv.main),
    (Website.AIRAV_CC, airav_cc.main),  # lang
    (Website.AIRAV, airav.main),  # lang
    (Website.AVSEX, avsex.main),
    (Website.AVSOX, avsox.main),
    (Website.CABLEAV, cableav.main),
    (Website.CNMDB, cnmdb.main),
    (Website.DAHLIA, dahlia.main),
    (Website.FALENO, faleno.main),
    (Website.FANTASTICA, fantastica.main),
    (Website.FREEJAVBT, freejavbt.main),
    (Website.GETCHU_DMM, getchu_dmm.main),
    (Website.GETCHU, getchu.main),
    (Website.GIGA, giga.main),
    (Website.HDOUBAN, hdouban.main),
    (Website.HSCANGKU, hscangku.main),
    (Website.IQQTV, iqqtv_new.main),  # lang
    (Website.JAV321, jav321.main),
    (Website.JAVDAY, javday.main),
    (Website.JAVLIBRARY, javlibrary_new.main),  # lang
    (Website.KIN8, kin8.main),
    (Website.LOVE6, love6.main),
    (Website.LULUBAR, lulubar.main),
    (Website.MADOUQU, madouqu.main),
    (Website.MDTV, mdtv.main),
    (Website.MYWIFE, mywife.main),
    (Website.OFFICIAL, official.main),
    (Website.PRESTIGE, prestige.main),
    (Website.THEPORNDB, theporndb.main),
    (Website.XCITY, xcity.main),
]


register_crawler(DmmCrawler)
register_crawler(JavdbCrawler)
register_crawler(JavbusCrawler)
register_crawler(MgstageCrawler)
register_crawler(Fc2Crawler)
register_crawler(Fc2ClubCrawler)
register_crawler(Fc2HubCrawler)
register_crawler(Fc2PpvdbCrawler)
for site, func in CRAWLER_FUNCS:
    register_v1_crawler(site, func)


def get_crawler_compat(site: Website):
    c = get_crawler(site)
    if c is not None:
        return c
    return get_v1_crawler(site)
