from typing import override
from urllib.parse import urljoin

from parsel import Selector

from ..config.manager import manager
from ..config.models import Website
from ..models.types import CrawlerResult
from .base import BaseCrawler, CralwerException, CrawlerData, DetailPageParser, extract_all_texts, extract_text


class Fc2HubParser(DetailPageParser):
    """FC2 Hub 网站解析器"""

    async def number(self, ctx, html: Selector) -> str:
        result = extract_text(html, "//h1/text()")
        return result or ctx.input.number

    async def title(self, ctx, html: Selector) -> str:
        results = extract_all_texts(html, "//h1/text()")
        return results[1] if len(results) > 1 else ""

    async def originaltitle(self, ctx, html: Selector) -> str:
        return await self.title(ctx, html)

    async def actors(self, ctx, html: Selector) -> list[str]:
        return []  # FC2 Hub 没有演员信息

    async def all_actors(self, ctx, html: Selector) -> list[str]:
        return []

    async def studio(self, ctx, html: Selector) -> str:
        return extract_text(html, '//div[@class="col-8"]/text()')

    async def publisher(self, ctx, html: Selector) -> str:
        return await self.studio(ctx, html)

    async def tags(self, ctx, html: Selector) -> list[str]:
        return extract_all_texts(html, '//p[@class="card-text"]/a[contains(@href, "/tag/")]/text()')

    async def thumb(self, ctx, html: Selector) -> str:
        result = extract_text(html, '//a[@data-fancybox="gallery"]/@href')
        if result:
            return result if result.startswith("http") else f"https:{result}"
        return ""

    async def extrafanart(self, ctx, html: Selector) -> list[str]:
        urls = extract_all_texts(html, '//div[@style="padding: 0"]/a/@href')
        return [u if u.startswith("http") else f"https:{u}" for u in urls]

    async def outline(self, ctx, html: Selector) -> str:
        result = extract_text(html, '//div[@class="col des"]//text()')
        return result.replace("\\n", "").replace("・", "") if result else ""

    async def mosaic(self, ctx, html: Selector) -> str:
        tags = ",".join(await self.tags(ctx, html))
        title = await self.title(ctx, html)
        if "無修正" in tags or "無修正" in title:
            return "无码"
        return "有码"

    async def image_cut(self, ctx, html: Selector) -> str:
        return "center"

    async def image_download(self, ctx, html: Selector) -> bool:
        return False


class Fc2HubCrawler(BaseCrawler):
    """FC2 Hub 网站爬虫"""
    parser = Fc2HubParser()

    @classmethod
    @override
    def site(cls) -> Website:
        return Website.FC2HUB

    @classmethod
    @override
    def base_url_(cls) -> str:
        return manager.config.get_site_url(Website.FC2HUB, "https://javten.com")

    @override
    async def _generate_search_url(self, ctx) -> list[str] | str | None:
        number = ctx.input.number.strip()
        # 清理番号格式
        number = number.upper().replace("FC2PPV", "").replace("FC2-PPV-", "").replace("FC2-", "").replace("-", "").strip()
        return f"{self.base_url}/search?kw={number}"

    @override
    async def _parse_search_page(self, ctx, html: Selector, search_url: str) -> list[str] | None:
        number = ctx.input.number.strip()
        number = number.upper().replace("FC2PPV", "").replace("FC2-PPV-", "").replace("FC2-", "").replace("-", "").strip()

        # 搜索结果中查找详情页链接
        urls = html.xpath(f"//link[contains(@href, 'id{number}')]/@href").getall()
        if urls:
            return [urljoin(self.base_url, urls[0])]

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
