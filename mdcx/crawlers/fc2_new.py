import re
from typing import override
from urllib.parse import urljoin

from parsel import Selector

from ..config.enums import FieldRule
from ..config.manager import manager
from ..config.models import Website
from ..models.types import CrawlerResult
from .base import BaseCrawler, CralwerException, CrawlerData, DetailPageParser, extract_all_texts, extract_text


class Fc2Parser(DetailPageParser):
    """FC2 官方网站解析器"""

    async def number(self, ctx, html: Selector) -> str:
        return ctx.input.number

    async def title(self, ctx, html: Selector) -> str:
        result = extract_text(html, '//div[@data-section="userInfo"]//h3/span/../text()')
        if not result:
            result = extract_text(html, '//div[@data-section="userInfo"]//h3/text()')
        return result

    async def originaltitle(self, ctx, html: Selector) -> str:
        return await self.title(ctx, html)

    async def actors(self, ctx, html: Selector) -> list[str]:
        # FC2 官方网站没有演员信息，使用卖家作为演员（如果配置允许）
        if FieldRule.FC2_SELLER in manager.config.fields_rule:
            studio = await self.studio(ctx, html)
            return [studio] if studio else []
        return []

    async def all_actors(self, ctx, html: Selector) -> list[str]:
        return await self.actors(ctx, html)

    async def studio(self, ctx, html: Selector) -> str:
        return extract_text(html, '//div[@class="items_article_headerInfo"]/ul/li[last()]/a/text()')

    async def publisher(self, ctx, html: Selector) -> str:
        return await self.studio(ctx, html)

    async def release(self, ctx, html: Selector) -> str:
        result = extract_text(html, '//div[@class="items_article_Releasedate"]/p/text()')
        if result:
            match = re.search(r"\d+/\d+/\d+", result)
            if match:
                return match.group().replace("/", "-")
        return ""

    async def year(self, ctx, html: Selector) -> str:
        release_date = await self.release(ctx, html)
        return release_date[:4] if release_date else ""

    async def tags(self, ctx, html: Selector) -> list[str]:
        tags = extract_all_texts(html, '//a[@class="tag tagTag"]/text()')
        # 移除 "無修正" 标签
        return [t for t in tags if t != "無修正"]

    async def thumb(self, ctx, html: Selector) -> str:
        # 获取封面图片列表
        extrafanart = extract_all_texts(html, '//ul[@class="items_article_SampleImagesArea"]/li/a/@href')
        if extrafanart:
            return extrafanart[0] if extrafanart[0].startswith("http") else f"https:{extrafanart[0]}"
        return ""

    async def poster(self, ctx, html: Selector) -> str:
        result = extract_text(html, '//div[@class="items_article_MainitemThumb"]/span/img/@src')
        if result:
            return result if result.startswith("http") else f"https:{result}"
        return ""

    async def extrafanart(self, ctx, html: Selector) -> list[str]:
        urls = extract_all_texts(html, '//ul[@class="items_article_SampleImagesArea"]/li/a/@href')
        return [u if u.startswith("http") else f"https:{u}" for u in urls]

    async def outline(self, ctx, html: Selector) -> str:
        return extract_text(html, '//meta[@name="description"]/@content')

    async def mosaic(self, ctx, html: Selector) -> str:
        tags = await self.tags(ctx, html)
        title = await self.title(ctx, html)
        if "無修正" in ",".join(tags) or "無修正" in title:
            return "无码"
        return "有码"

    async def image_cut(self, ctx, html: Selector) -> str:
        return "center"

    async def image_download(self, ctx, html: Selector) -> bool:
        return False


class Fc2Crawler(BaseCrawler):
    """FC2 官方网站爬虫"""
    parser = Fc2Parser()

    @classmethod
    @override
    def site(cls) -> Website:
        return Website.FC2

    @classmethod
    @override
    def base_url_(cls) -> str:
        return "https://adult.contents.fc2.com"

    @override
    async def _generate_search_url(self, ctx) -> list[str] | str | None:
        number = ctx.input.number.strip()
        # 清理番号格式
        number = number.upper().replace("FC2PPV", "").replace("FC2-PPV-", "").replace("FC2-", "").replace("-", "").strip()
        return f"{self.base_url}/article/{number}/"

    @override
    async def _parse_search_page(self, ctx, html: Selector, search_url: str) -> list[str] | None:
        # FC2 直接访问详情页
        title = await self.parser.title(ctx, html)
        if title and "お探しの商品が見つかりません" not in title:
            return [search_url]
        return None

    @override
    async def _parse_detail_page(self, ctx, html: Selector, detail_url: str) -> CrawlerData | None:
        title = await self.parser.title(ctx, html)
        if not title or "お探しの商品が見つかりません" in title:
            raise CralwerException("搜索结果: 未匹配到番号！")

        # 检查封面是否有效
        thumb = await self.parser.thumb(ctx, html)
        if not thumb:
            raise CralwerException("数据获取失败: 未获取到cover！")

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

        # 处理 relative URL
        if res.thumb and not res.thumb.startswith("http"):
            res.thumb = urljoin(self.base_url, res.thumb)
        if res.poster and not res.poster.startswith("http"):
            res.poster = urljoin(self.base_url, res.poster)
        res.extrafanart = [
            urljoin(self.base_url, url) if not url.startswith("http") else url
            for url in res.extrafanart
        ]

        return res
