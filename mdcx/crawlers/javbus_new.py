import re
from typing import override
from urllib.parse import urljoin

from parsel import Selector

from ..config.manager import manager
from ..config.models import Website
from ..models.types import CrawlerResult
from .base import BaseCrawler, CralwerException, CrawlerData, DetailPageParser, extract_all_texts, extract_text


class Parser(DetailPageParser):
    async def number(self, ctx, html: Selector) -> str:
        result = extract_text(html, '//span[@class="header"][contains(text(), "識別碼:")]/../span[2]/text()')
        return result or ctx.input.number

    async def title(self, ctx, html: Selector) -> str:
        return extract_text(html, "//h3/text()")

    async def originaltitle(self, ctx, html: Selector) -> str:
        return await self.title(ctx, html)

    async def actors(self, ctx, html: Selector) -> list[str]:
        return extract_all_texts(html, '//div[@class="star-name"]/a/text()')

    async def all_actors(self, ctx, html: Selector) -> list[str]:
        return await self.actors(ctx, html)

    async def studio(self, ctx, html: Selector) -> str:
        return extract_text(html, '//a[contains(@href, "/studio/")]/text()')

    async def publisher(self, ctx, html: Selector) -> str:
        return extract_text(html, '//a[contains(@href, "/label/")]/text()') or await self.studio(ctx, html)

    async def runtime(self, ctx, html: Selector) -> str:
        result = extract_text(html, '//span[@class="header"][contains(text(), "長度:")]/../text()')
        if result:
            match = re.search(r"\d+", result)
            return match.group() if match else ""
        return ""

    async def series(self, ctx, html: Selector) -> str:
        return extract_text(html, '//a[contains(@href, "/series/")]/text()')

    async def release(self, ctx, html: Selector) -> str:
        return extract_text(html, '//span[@class="header"][contains(text(), "發行日期:")]/../text()')

    async def year(self, ctx, html: Selector) -> str:
        release_date = await self.release(ctx, html)
        try:
            result = re.search(r"\d{4}", release_date)
            return result.group() if result else release_date[:4]
        except Exception:
            return release_date[:4] if release_date else ""

    async def tags(self, ctx, html: Selector) -> list[str]:
        return extract_all_texts(html, '//span[@class="genre"]/label/a[contains(@href, "/genre/")]/text()')

    async def thumb(self, ctx, html: Selector) -> str:
        return extract_text(html, '//a[@class="bigImage"]/@href')

    async def extrafanart(self, ctx, html: Selector) -> list[str]:
        return extract_all_texts(html, "//div[@id='sample-waterfall']/a/@href")

    async def directors(self, ctx, html: Selector) -> list[str]:
        return extract_all_texts(html, '//a[contains(@href, "/director/")]/text()')

    async def mosaic(self, ctx, html: Selector) -> str:
        select_tab = extract_text(html, '//li[@class="active"]/a/text()')
        return "无码" if "無碼" in select_tab else "有码"

    async def image_cut(self, ctx, html: Selector) -> str:
        mosaic = await self.mosaic(ctx, html)
        return "center" if mosaic == "无码" else "right"

    async def image_download(self, ctx, html: Selector) -> bool:
        mosaic = await self.mosaic(ctx, html)
        number = ctx.input.number
        if mosaic == "无码":
            if "_" in number or "HEYZO" in number:
                return True
        if "KMHRS" in number:
            return True
        return False

    async def poster(self, ctx, html: Selector) -> str:
        cover_url = await self.thumb(ctx, html)
        if not cover_url:
            return ""
        if "/pics/" in cover_url:
            return cover_url.replace("/cover/", "/thumb/").replace("_b.jpg", ".jpg")
        elif "/imgs/" in cover_url:
            return cover_url.replace("/cover/", "/thumbs/").replace("_b.jpg", ".jpg")
        return ""


class JavbusCrawler(BaseCrawler):
    parser = Parser()

    @classmethod
    @override
    def site(cls) -> Website:
        return Website.JAVBUS

    @classmethod
    @override
    def base_url_(cls) -> str:
        return manager.config.get_site_url(Website.JAVBUS, "https://www.javbus.com")

    @override
    def _get_headers(self, ctx) -> dict[str, str] | None:
        headers = {
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
        }
        if manager.config.javbus:
            headers["cookie"] = manager.config.javbus
        return headers

    @override
    async def _generate_search_url(self, ctx) -> list[str] | str | None:
        number = ctx.input.number.strip()
        mosaic = ctx.input.mosaic

        # 欧美番号使用搜索
        if "." in number or re.search(r"[-_]\d{2}[-_]\d{2}[-_]\d{2}", number):
            number = number.replace("-", ".").replace("_", ".")
            return f"https://www.javbus.hair/search/{number}"

        # CWP/LAF 特殊处理
        if number.upper().startswith("CWP") or number.upper().startswith("LAF"):
            temp_number = number.replace("-0", "-")
            if temp_number[-2] == "-":
                temp_number = temp_number.replace("-", "-0")
            return f"{self.base_url}/{temp_number}"

        # 尝试直接拼接地址
        return f"{self.base_url}/{number}"

    @override
    async def _parse_search_page(self, ctx, html: Selector, search_url: str) -> list[str] | None:
        number = ctx.input.number

        # 检查是否需要登录
        html_text = html._text or ""
        if "lostpasswd" in html_text:
            raise CralwerException("Cookie 无效！请重新填写 Cookie 或更新节点！")

        # 获取搜索结果
        url_list = html.xpath("//a[@class='movie-box']/@href").getall()
        for each in url_list:
            each_url = each.upper().replace("-", "")
            number_1 = "/" + number.upper().replace(".", "").replace("-", "")
            number_2 = number_1 + "_"
            if each_url.endswith(number_1) or number_2 in each_url:
                return [each]

        return None

    @override
    async def _parse_detail_page(self, ctx, html: Selector, detail_url: str) -> CrawlerData | None:
        # 检查是否需要登录
        html_text = html._text or ""
        if "lostpasswd" in html_text:
            raise CralwerException("Cookie 无效！请重新填写 Cookie 或更新节点！")

        return await self.parser.parse(ctx, html, external_id=detail_url)

    @override
    async def post_process(self, ctx, res: CrawlerResult) -> CrawlerResult:
        # 处理无码影片的图片
        if res.mosaic == "无码":
            number = ctx.input.number
            if "_" not in number and "HEYZO" not in number:
                res.poster = ""  # 非一本道的无码影片，清空小图地址

        # KMHRS 特殊处理：剧照第一张是高清图
        if "KMHRS" in res.number and res.extrafanart:
            res.poster = res.extrafanart[0]

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
