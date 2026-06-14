from typing import override

from parsel import Selector

from ..config.manager import manager
from ..config.models import Website
from ..models.types import CrawlerResult
from .base import BaseCrawler, CralwerException, CrawlerData, DetailPageParser, extract_all_texts, extract_text


class Fc2PpvdbParser(DetailPageParser):
    """FC2 PPV DB 网站解析器"""

    async def number(self, ctx, html: Selector) -> str:
        return ctx.input.number

    async def title(self, ctx, html: Selector) -> str:
        return extract_text(html, "//h2/a/text()")

    async def originaltitle(self, ctx, html: Selector) -> str:
        return await self.title(ctx, html)

    async def actors(self, ctx, html: Selector) -> list[str]:
        return extract_all_texts(html, "//div[starts-with(text(),'女優：')]/span/a/text()")

    async def all_actors(self, ctx, html: Selector) -> list[str]:
        return await self.actors(ctx, html)

    async def studio(self, ctx, html: Selector) -> str:
        return extract_text(html, "//div[starts-with(text(),'販売者：')]/span/a/text()")

    async def publisher(self, ctx, html: Selector) -> str:
        return await self.studio(ctx, html)

    async def runtime(self, ctx, html: Selector) -> str:
        return extract_text(html, "//div[starts-with(text(),'収録時間：')]/span/text()")

    async def release(self, ctx, html: Selector) -> str:
        return extract_text(html, "//div[starts-with(text(),'販売日：')]/span/text()")

    async def year(self, ctx, html: Selector) -> str:
        release_date = await self.release(ctx, html)
        return release_date[:4] if release_date else ""

    async def tags(self, ctx, html: Selector) -> list[str]:
        return extract_all_texts(html, "//div[starts-with(text(),'タグ：')]/span/a/text()")

    async def thumb(self, ctx, html: Selector) -> str:
        number = ctx.input.number.strip()
        number = number.upper().replace("FC2PPV", "").replace("FC2-PPV-", "").replace("FC2-", "").replace("-", "").strip()
        result = extract_text(html, f"//img[contains(@alt, '{number}')]/@src")
        return result if result and result.startswith("http") else ""

    async def mosaic(self, ctx, html: Selector) -> str:
        result = extract_text(html, "//div[starts-with(text(),'モザイク：')]/span/text()")
        if result == "無":
            return "无码"
        elif result == "有":
            return "有码"
        return "有码"

    async def image_cut(self, ctx, html: Selector) -> str:
        return "center"

    async def image_download(self, ctx, html: Selector) -> bool:
        return False


class Fc2PpvdbCrawler(BaseCrawler):
    """FC2 PPV DB 网站爬虫"""
    parser = Fc2PpvdbParser()

    @classmethod
    @override
    def site(cls) -> Website:
        return Website.FC2PPVDB

    @classmethod
    @override
    def base_url_(cls) -> str:
        return "https://fc2ppvdb.com"

    @override
    async def _generate_search_url(self, ctx) -> list[str] | str | None:
        number = ctx.input.number.strip()
        # 清理番号格式
        number = number.upper().replace("FC2PPV", "").replace("FC2-PPV-", "").replace("FC2-", "").replace("-", "").strip()
        return f"{self.base_url}/articles/{number}"

    @override
    async def _parse_search_page(self, ctx, html: Selector, search_url: str) -> list[str] | None:
        # FC2 PPV DB 直接访问详情页
        title = await self.parser.title(ctx, html)
        if title:
            return [search_url]
        return None

    @override
    async def _parse_detail_page(self, ctx, html: Selector, detail_url: str) -> CrawlerData | None:
        title = await self.parser.title(ctx, html)
        if not title:
            raise CralwerException("数据获取失败: 未获取到title")

        return await self.parser.parse(ctx, html, external_id=detail_url)

    @override
    async def post_process(self, ctx, res: CrawlerResult) -> CrawlerResult:
        # FC2 番号格式化
        number = ctx.input.number.strip()
        number = number.upper().replace("FC2PPV", "").replace("FC2-PPV-", "").replace("FC2-", "").replace("-", "").strip()
        res.number = f"FC2-{number}"

        # 设置默认值
        res.series = "FC2系列"
        res.director = ""

        return res
