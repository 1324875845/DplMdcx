import re
from typing import override

from parsel import Selector

from ..config.enums import FieldRule
from ..config.manager import manager
from ..config.models import Website
from ..models.types import CrawlerResult
from .base import BaseCrawler, CralwerException, CrawlerData, DetailPageParser, extract_all_texts, extract_text


class Fc2ClubParser(DetailPageParser):
    """FC2 Club 网站解析器"""

    async def number(self, ctx, html: Selector) -> str:
        result = extract_text(html, "//h1/text()")
        return result or ctx.input.number

    async def title(self, ctx, html: Selector) -> str:
        result = extract_text(html, "//h3/text()")
        if result:
            # 移除番号前缀
            number = ctx.input.number
            result = result.replace(f"FC2-{number} ", "").replace(f"FC2{number} ", "")
        return result

    async def originaltitle(self, ctx, html: Selector) -> str:
        return await self.title(ctx, html)

    async def actors(self, ctx, html: Selector) -> list[str]:
        actors = extract_all_texts(html, '//strong[contains(text(), "女优名字")]/../a/text()')
        if actors:
            return actors
        # 如果没有演员信息，使用卖家（如果配置允许）
        if "fc2_seller" in manager.config.fields_rule:
            studio = await self.studio(ctx, html)
            return [studio] if studio else []
        return []

    async def all_actors(self, ctx, html: Selector) -> list[str]:
        return await self.actors(ctx, html)

    async def studio(self, ctx, html: Selector) -> str:
        result = extract_text(html, '//strong[contains(text(), "卖家信息")]/../a/text()')
        return result.replace("本资源官网地址", "") if result else ""

    async def publisher(self, ctx, html: Selector) -> str:
        return await self.studio(ctx, html)

    async def score(self, ctx, html: Selector) -> str:
        result = extract_text(html, '//strong[contains(text(), "影片评分")]/../text()')
        if result:
            match = re.search(r"\d+", result)
            return match.group() if match else ""
        return ""

    async def tags(self, ctx, html: Selector) -> list[str]:
        return extract_all_texts(html, '//strong[contains(text(), "影片标签")]/../a/text()')

    async def thumb(self, ctx, html: Selector) -> str:
        result = extract_text(html, '//img[@class="responsive"]/@src')
        if result:
            return result.replace("../uploadfile", "https://fc2club.top/uploadfile")
        return ""

    async def extrafanart(self, ctx, html: Selector) -> list[str]:
        urls = extract_all_texts(html, '//img[@class="responsive"]/@src')
        return [u.replace("../uploadfile", "https://fc2club.top/uploadfile") for u in urls]

    async def outline(self, ctx, html: Selector) -> str:
        result = extract_text(html, '//div[@class="col des"]/text()')
        return result.replace("\\n", "").replace("・", "") if result else ""

    async def mosaic(self, ctx, html: Selector) -> str:
        result = extract_text(html, '//h5/strong[contains(text(), "资源参数")]/../text()')
        return "无码" if "无码" in result else "有码"

    async def image_cut(self, ctx, html: Selector) -> str:
        return "center"

    async def image_download(self, ctx, html: Selector) -> bool:
        return False


class Fc2ClubCrawler(BaseCrawler):
    """FC2 Club 网站爬虫"""
    parser = Fc2ClubParser()

    @classmethod
    @override
    def site(cls) -> Website:
        return Website.FC2CLUB

    @classmethod
    @override
    def base_url_(cls) -> str:
        return "https://fc2club.top"

    @override
    async def _generate_search_url(self, ctx) -> list[str] | str | None:
        number = ctx.input.number.strip()
        # 清理番号格式
        number = number.upper().replace("FC2PPV", "").replace("FC2-PPV-", "").replace("FC2-", "").replace("-", "").strip()
        return f"{self.base_url}/articles/{number}"

    @override
    async def _parse_search_page(self, ctx, html: Selector, search_url: str) -> list[str] | None:
        # FC2 Club 直接访问详情页
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
