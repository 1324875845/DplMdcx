"""
爬虫模块
新架构爬虫使用 BaseCrawler 模式
旧架构爬虫使用延迟导入以减少依赖
"""

from collections.abc import Callable
from typing import TYPE_CHECKING

from ..config.models import Website
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

if TYPE_CHECKING:
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


def _register_legacy_crawlers():
    """延迟注册旧架构爬虫"""
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

    CRAWLER_FUNCS: list[tuple[Website, Callable]] = [
        (Website.MMTV, mmtv.main),
        (Website.AIRAV_CC, airav_cc.main),
        (Website.AIRAV, airav.main),
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
        (Website.IQQTV, iqqtv_new.main),
        (Website.JAV321, jav321.main),
        (Website.JAVDAY, javday.main),
        (Website.JAVLIBRARY, javlibrary_new.main),
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

    for site, func in CRAWLER_FUNCS:
        register_v1_crawler(site, func)


# 注册新架构爬虫
register_crawler(DmmCrawler)
register_crawler(JavdbCrawler)
register_crawler(JavbusCrawler)
register_crawler(MgstageCrawler)
register_crawler(Fc2Crawler)
register_crawler(Fc2ClubCrawler)
register_crawler(Fc2HubCrawler)
register_crawler(Fc2PpvdbCrawler)

# 延迟注册旧架构爬虫（首次访问时才导入）
_legacy_registered = False


def _ensure_legacy_registered():
    global _legacy_registered
    if not _legacy_registered:
        _register_legacy_crawlers()
        _legacy_registered = True


def get_crawler_compat(site: Website):
    """获取爬虫（兼容新旧架构）"""
    c = get_crawler(site)
    if c is not None:
        return c
    _ensure_legacy_registered()
    return get_v1_crawler(site)


def get_all_crawlers() -> dict[Website, type]:
    """获取所有已注册的爬虫"""
    _ensure_legacy_registered()
    from .base import crawler_registry
    from .base.compat import v1_cralwers

    result = {}
    result.update(crawler_registry)
    for site, crawler in v1_cralwers.items():
        if site not in result:
            result[site] = type(crawler)
    return result
