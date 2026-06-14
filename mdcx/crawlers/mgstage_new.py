import re
from typing import override

from parsel import Selector

from ..config.manager import manager
from ..config.models import Website
from ..models.types import CrawlerResult
from .base import BaseCrawler, CralwerException, CrawlerData, DetailPageParser, extract_all_texts, extract_text


class Parser(DetailPageParser):
    async def number(self, ctx, html: Selector) -> str:
        result = extract_text(
            html,
            '//th[contains(text(),"品番：")]/../td/a/text()',
            '//th[contains(text(),"品番：")]/../td/text()',
        )
        return result or ctx.input.number

    async def title(self, ctx, html: Selector) -> str:
        result = extract_text(html, '//*[@id="center_column"]/div[1]/h1/text()')
        return result.replace("/", ",") if result else ""

    async def originaltitle(self, ctx, html: Selector) -> str:
        return await self.title(ctx, html)

    async def actors(self, ctx, html: Selector) -> list[str]:
        actors = extract_all_texts(
            html,
            '//th[contains(text(),"出演")]/../td/a/text()',
            '//th[contains(text(),"出演")]/../td/text()',
        )
        # 过滤掉包含逗号的条目（可能是多个演员合并在一个条目中）
        return [a for a in actors if "," not in a or ")" in a]

    async def all_actors(self, ctx, html: Selector) -> list[str]:
        return await self.actors(ctx, html)

    async def studio(self, ctx, html: Selector) -> str:
        return extract_text(
            html,
            '//th[contains(text(),"メーカー：")]/../td/a/text()',
            '//th[contains(text(),"メーカー：")]/../td/text()',
        )

    async def publisher(self, ctx, html: Selector) -> str:
        return extract_text(
            html,
            '//th[contains(text(),"レーベル：")]/../td/a/text()',
            '//th[contains(text(),"レーベル：")]/../td/text()',
        )

    async def runtime(self, ctx, html: Selector) -> str:
        result = extract_text(
            html,
            '//th[contains(text(),"収録時間：")]/../td/a/text()',
            '//th[contains(text(),"収録時間：")]/../td/text()',
        )
        return result.rstrip("min") if result else ""

    async def series(self, ctx, html: Selector) -> str:
        return extract_text(
            html,
            '//th[contains(text(),"シリーズ：")]/../td/a/text()',
            '//th[contains(text(),"シリーズ：")]/../td/text()',
        )

    async def release(self, ctx, html: Selector) -> str:
        result = extract_text(
            html,
            '//th[contains(text(),"配信開始日：")]/../td/a/text()',
            '//th[contains(text(),"配信開始日：")]/../td/text()',
        )
        return result.replace("/", "-") if result else ""

    async def year(self, ctx, html: Selector) -> str:
        release_date = await self.release(ctx, html)
        try:
            result = re.search(r"\d{4}", release_date)
            return result.group() if result else release_date
        except Exception:
            return release_date

    async def tags(self, ctx, html: Selector) -> list[str]:
        return extract_all_texts(
            html,
            '//th[contains(text(),"ジャンル：")]/../td/a/text()',
            '//th[contains(text(),"ジャンル：")]/../td/text()',
        )

    async def thumb(self, ctx, html: Selector) -> str:
        return extract_text(html, '//a[@id="EnlargeImage"]/@href')

    async def poster(self, ctx, html: Selector) -> str:
        cover_url = await self.thumb(ctx, html)
        if cover_url:
            return cover_url.replace("/pb_", "/pf_")
        return ""

    async def extrafanart(self, ctx, html: Selector) -> list[str]:
        return extract_all_texts(html, "//dl[@id='sample-photo']/dd/ul/li/a[@class='sample_image']/@href")

    async def outline(self, ctx, html: Selector) -> str:
        result = extract_text(html, '//*[@id="introduction"]/dd/p[1]/text()')
        if not result:
            # 尝试获取整个简介区域
            temp = html.xpath('//*[@id="introduction"]/dd')
            if temp:
                result = temp[0].xpath("string(.)").replace(" ", "").strip()
        return result

    async def score(self, ctx, html: Selector) -> str:
        result = html.xpath('//td[@class="review"]/span/@class')
        if result:
            try:
                return f"{int(result[0].replace('star_', '')[:2]) / 10:.1f}"
            except (ValueError, IndexError):
                pass
        return ""

    async def mosaic(self, ctx, html: Selector) -> str:
        return "有码"  # MGStage 主要是素人有码

    async def image_cut(self, ctx, html: Selector) -> str:
        return "right"

    async def image_download(self, ctx, html: Selector) -> bool:
        return True  # MGStage 默认下载图片


class MgstageCrawler(BaseCrawler):
    parser = Parser()

    @classmethod
    @override
    def site(cls) -> Website:
        return Website.MGSTAGE

    @classmethod
    @override
    def base_url_(cls) -> str:
        return "https://www.mgstage.com"

    @override
    def _get_cookies(self, ctx) -> dict[str, str] | None:
        return {"adc": "1"}

    @override
    async def _generate_search_url(self, ctx) -> list[str] | str | None:
        number = ctx.input.number.strip().upper()
        short_number = ctx.input.short_number.strip().upper() if ctx.input.short_number else ""

        # MGStage 支持完整番号和短番号
        urls = [f"{self.base_url}/product/product_detail/{number}/"]
        if short_number and short_number != number:
            urls.append(f"{self.base_url}/product/product_detail/{short_number}/")

        return urls

    @override
    async def _parse_search_page(self, ctx, html: Selector, search_url: str) -> list[str] | None:
        # MGStage 直接访问详情页，不需要搜索
        # 如果页面有标题，说明是详情页
        title = await self.parser.title(ctx, html)
        if title:
            return [search_url]
        return None

    @override
    async def _parse_detail_page(self, ctx, html: Selector, detail_url: str) -> CrawlerData | None:
        # 检查页面是否有效
        title = await self.parser.title(ctx, html)
        if not title:
            raise CralwerException("数据获取失败: 未获取到title")

        return await self.parser.parse(ctx, html, external_id=detail_url)

    @override
    async def post_process(self, ctx, res: CrawlerResult) -> CrawlerResult:
        # MGStage 的海报是从封面URL转换而来
        if res.thumb:
            res.poster = res.thumb.replace("/pb_", "/pf_")

        # 获取预告片
        res.trailer = await self._get_trailer(ctx)

        return res

    async def _get_trailer(self, ctx) -> str:
        """获取预告片URL"""
        try:
            # 查找预告片播放按钮
            html, error = await self.async_client.get_text(
                f"{self.base_url}/product/product_detail/{ctx.input.number}/",
                cookies={"adc": "1"},
            )
            if html is None:
                return ""

            # 提取预告片URL
            match = re.search(r"review-btn.*?href=['\"]([^'\"]+)['\"]", html, re.DOTALL)
            if not match:
                return ""

            review_url = match.group(1).replace("/mypage/review.php", "/sampleplayer/sampleRespons.php")
            json_data, _ = await self.async_client.get_json(review_url, cookies={"adc": "1"})

            if json_data and "url" in json_data:
                url_match = re.search(r"(https.+)ism/request", str(json_data["url"]))
                if url_match:
                    return url_match.group(1) + "mp4"
        except Exception:
            pass
        return ""
