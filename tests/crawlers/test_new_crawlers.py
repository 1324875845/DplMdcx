"""
新架构爬虫单元测试
测试 BaseCrawler 模式的爬虫
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

# 检查依赖是否可用
try:
    import parsel
    import lxml
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

pytestmark = pytest.mark.skipif(not HAS_DEPS, reason="需要 parsel 和 lxml 依赖")


# ====== Helper Function Tests ======

class TestHelperFunctions:
    """辅助函数测试"""

    def test_extract_text(self):
        from mdcx.crawlers.base import extract_text
        from parsel import Selector

        html = Selector(text="<html><body><p>Hello World</p></body></html>")
        result = extract_text(html, "//p/text()")
        assert result == "Hello World"

    def test_extract_all_texts(self):
        from mdcx.crawlers.base import extract_all_texts
        from parsel import Selector

        html = Selector(text="<html><body><p>A</p><p>B</p><p>C</p></body></html>")
        result = extract_all_texts(html, "//p/text()")
        assert result == ["A", "B", "C"]

    def test_extract_text_not_found(self):
        from mdcx.crawlers.base import extract_text
        from parsel import Selector

        html = Selector(text="<html><body></body></html>")
        result = extract_text(html, "//p/text()")
        assert result == ""

    def test_crawler_data_to_result(self):
        from mdcx.crawlers.base import CrawlerData

        data = CrawlerData(
            title="テスト",
            actors=["女優A"],
            all_actors=["女優A", "女優B"],
            directors=[],
            extrafanart=[],
            originalplot="",
            originaltitle="テスト原标题",
            outline="",
            poster="",
            publisher="",
            release="2021-01-01",
            runtime="120",
            score="8.0",
            series="",
            studio="メーカーA",
            tags=["タグ1"],
            thumb="https://example.com/thumb.jpg",
            trailer="",
            wanted="",
            year="2021",
            image_cut="right",
            image_download=False,
            number="SSIS-001",
            mosaic="有码",
        )
        result = data.to_result()
        assert result.title == "テスト"
        assert result.number == "SSIS-001"


# ====== Parser Tests ======

class TestJavbusParser:
    """Javbus 解析器测试"""

    @pytest.fixture
    def sample_html(self):
        return """
        <html>
        <body>
            <h3>SSIS-001 テストタイトル</h3>
            <span class="header">識別碼:</span>
            <span>SSIS-001</span>
            <div class="star-name"><a href="/star/1">女優A</a></div>
            <div class="star-name"><a href="/star/2">女優B</a></div>
            <a class="bigImage" href="/pics/cover/b.jpg"><img src="/pics/thumb/s.jpg"></a>
            <span class="header">發行日期:</span>
            2021/01/01
            <span class="header">長度:</span>
            120分鐘
            <a href="/studio/1">スタジオA</a>
            <a href="/label/1">レーベルB</a>
            <a href="/director/1">監督C</a>
            <a href="/series/1">シリーズD</a>
            <div id="sample-waterfall">
                <a href="/pics/extra/1.jpg"><img src="/pics/thumb/1.jpg"></a>
            </div>
            <span class="genre"><label><a href="/genre/1">タグ1</a></label></span>
            <li class="active"><a>有碼</a></li>
        </body>
        </html>
        """

    @pytest.mark.asyncio
    async def test_parse_title(self, sample_html):
        from mdcx.crawlers.javbus_new import Parser
        from parsel import Selector
        from mdcx.crawlers.base import Context
        from mdcx.models.types import CrawlerInput, Language

        parser = Parser()
        ctx = Context(input=CrawlerInput(
            number="SSIS-001",
            appoint_number="",
            appoint_url="",
            mosaic="",
            short_number="",
            language=Language.UNDEFINED,
            org_language=Language.UNDEFINED,
            file_path=None,
        ))
        html = Selector(text=sample_html)
        title = await parser.title(ctx, html)
        assert title == "テストタイトル"

    @pytest.mark.asyncio
    async def test_parse_actors(self, sample_html):
        from mdcx.crawlers.javbus_new import Parser
        from parsel import Selector
        from mdcx.crawlers.base import Context
        from mdcx.models.types import CrawlerInput, Language

        parser = Parser()
        ctx = Context(input=CrawlerInput(
            number="SSIS-001",
            appoint_number="",
            appoint_url="",
            mosaic="",
            short_number="",
            language=Language.UNDEFINED,
            org_language=Language.UNDEFINED,
            file_path=None,
        ))
        html = Selector(text=sample_html)
        actors = await parser.actors(ctx, html)
        assert actors == ["女優A", "女優B"]

    @pytest.mark.asyncio
    async def test_parse_tags(self, sample_html):
        from mdcx.crawlers.javbus_new import Parser
        from parsel import Selector
        from mdcx.crawlers.base import Context
        from mdcx.models.types import CrawlerInput, Language

        parser = Parser()
        ctx = Context(input=CrawlerInput(
            number="SSIS-001",
            appoint_number="",
            appoint_url="",
            mosaic="",
            short_number="",
            language=Language.UNDEFINED,
            org_language=Language.UNDEFINED,
            file_path=None,
        ))
        html = Selector(text=sample_html)
        tags = await parser.tags(ctx, html)
        assert "タグ1" in tags

    @pytest.mark.asyncio
    async def test_parse_mosaic(self, sample_html):
        from mdcx.crawlers.javbus_new import Parser
        from parsel import Selector
        from mdcx.crawlers.base import Context
        from mdcx.models.types import CrawlerInput, Language

        parser = Parser()
        ctx = Context(input=CrawlerInput(
            number="SSIS-001",
            appoint_number="",
            appoint_url="",
            mosaic="",
            short_number="",
            language=Language.UNDEFINED,
            org_language=Language.UNDEFINED,
            file_path=None,
        ))
        html = Selector(text=sample_html)
        mosaic = await parser.mosaic(ctx, html)
        assert mosaic == "有码"


class TestMgstageParser:
    """MGStage 解析器测试"""

    @pytest.fixture
    def sample_html(self):
        return """
        <html>
        <body>
            <div id="center_column">
                <div><h1>300MIUM-382 テストタイトル</h1></div>
            </div>
            <table>
                <tr><th>品番：</th><td><a>300MIUM-382</a></td></tr>
                <tr><th>出演：</th><td><a>女優X</a></td></tr>
                <tr><th>メーカー：</th><td><a>メーカーA</a></td></tr>
                <tr><th>レーベル：</th><td><a>レーベルB</a></td></tr>
                <tr><th>収録時間：</th><td>90min</td></tr>
                <tr><th>シリーズ：</th><td><a>シリーズC</a></td></tr>
                <tr><th>配信開始日：</th><td>2021/06/15</td></tr>
                <tr><th>ジャンル：</th><td><a>ジャンル1</a></td></tr>
                <tr><th>ジャンル：</th><td><a>ジャンル2</a></td></tr>
            </table>
            <a id="EnlargeImage" href="/pics/pb_test.jpg"></a>
            <dl id="sample-photo"><dd><ul>
                <li><a class="sample_image" href="/pics/pf_test.jpg"></a></li>
            </ul></dd></dl>
            <div id="introduction"><dd><p>テスト概要</p></dd></div>
            <td class="review"><span class="star_80"></span></td>
        </body>
        </html>
        """

    @pytest.mark.asyncio
    async def test_parse_title(self, sample_html):
        from mdcx.crawlers.mgstage_new import Parser
        from parsel import Selector
        from mdcx.crawlers.base import Context
        from mdcx.models.types import CrawlerInput, Language

        parser = Parser()
        ctx = Context(input=CrawlerInput(
            number="300MIUM-382",
            appoint_number="",
            appoint_url="",
            mosaic="",
            short_number="",
            language=Language.UNDEFINED,
            org_language=Language.UNDEFINED,
            file_path=None,
        ))
        html = Selector(text=sample_html)
        title = await parser.title(ctx, html)
        assert "テストタイトル" in title

    @pytest.mark.asyncio
    async def test_parse_studio(self, sample_html):
        from mdcx.crawlers.mgstage_new import Parser
        from parsel import Selector
        from mdcx.crawlers.base import Context
        from mdcx.models.types import CrawlerInput, Language

        parser = Parser()
        ctx = Context(input=CrawlerInput(
            number="300MIUM-382",
            appoint_number="",
            appoint_url="",
            mosaic="",
            short_number="",
            language=Language.UNDEFINED,
            org_language=Language.UNDEFINED,
            file_path=None,
        ))
        html = Selector(text=sample_html)
        studio = await parser.studio(ctx, html)
        assert studio == "メーカーA"

    @pytest.mark.asyncio
    async def test_parse_score(self, sample_html):
        from mdcx.crawlers.mgstage_new import Parser
        from parsel import Selector
        from mdcx.crawlers.base import Context
        from mdcx.models.types import CrawlerInput, Language

        parser = Parser()
        ctx = Context(input=CrawlerInput(
            number="300MIUM-382",
            appoint_number="",
            appoint_url="",
            mosaic="",
            short_number="",
            language=Language.UNDEFINED,
            org_language=Language.UNDEFINED,
            file_path=None,
        ))
        html = Selector(text=sample_html)
        score = await parser.score(ctx, html)
        assert score == "8.0"


class TestFc2Parser:
    """FC2 解析器测试"""

    @pytest.fixture
    def sample_html(self):
        return """
        <html>
        <body>
            <div data-section="userInfo">
                <h3><span>FC2-1234567 テスト商品</span></h3>
            </div>
            <ul class="items_article_SampleImagesArea">
                <li><a href="//example.com/img1.jpg"></a></li>
                <li><a href="//example.com/img2.jpg"></a></li>
            </ul>
            <div class="items_article_MainitemThumb">
                <span><img src="//example.com/thumb.jpg"></span>
            </div>
            <div class="items_article_Releasedate">
                <p>販売日：2021/03/15</p>
            </div>
            <div class="items_article_headerInfo">
                <ul>
                    <li><a>出品者A</a></li>
                    <li><a>ストアB</a></li>
                </ul>
            </div>
            <a class="tag tagTag">無修正</a>
            <a class="tag tagTag">タグ1</a>
            <meta name="description" content="テスト説明文">
        </body>
        </html>
        """

    @pytest.mark.asyncio
    async def test_parse_title(self, sample_html):
        from mdcx.crawlers.fc2_new import Fc2Parser
        from parsel import Selector
        from mdcx.crawlers.base import Context
        from mdcx.models.types import CrawlerInput, Language

        parser = Fc2Parser()
        ctx = Context(input=CrawlerInput(
            number="FC2-1234567",
            appoint_number="",
            appoint_url="",
            mosaic="",
            short_number="",
            language=Language.UNDEFINED,
            org_language=Language.UNDEFINED,
            file_path=None,
        ))
        html = Selector(text=sample_html)
        title = await parser.title(ctx, html)
        assert "テスト商品" in title

    @pytest.mark.asyncio
    async def test_parse_studio(self, sample_html):
        from mdcx.crawlers.fc2_new import Fc2Parser
        from parsel import Selector
        from mdcx.crawlers.base import Context
        from mdcx.models.types import CrawlerInput, Language

        parser = Fc2Parser()
        ctx = Context(input=CrawlerInput(
            number="FC2-1234567",
            appoint_number="",
            appoint_url="",
            mosaic="",
            short_number="",
            language=Language.UNDEFINED,
            org_language=Language.UNDEFINED,
            file_path=None,
        ))
        html = Selector(text=sample_html)
        studio = await parser.studio(ctx, html)
        assert studio == "ストアB"

    @pytest.mark.asyncio
    async def test_parse_mosaic_uncensored(self, sample_html):
        from mdcx.crawlers.fc2_new import Fc2Parser
        from parsel import Selector
        from mdcx.crawlers.base import Context
        from mdcx.models.types import CrawlerInput, Language

        parser = Fc2Parser()
        ctx = Context(input=CrawlerInput(
            number="FC2-1234567",
            appoint_number="",
            appoint_url="",
            mosaic="",
            short_number="",
            language=Language.UNDEFINED,
            org_language=Language.UNDEFINED,
            file_path=None,
        ))
        html = Selector(text=sample_html)
        mosaic = await parser.mosaic(ctx, html)
        assert mosaic == "无码"


# ====== Crawler Registry Tests ======

class TestCrawlerRegistry:
    """爬虫注册表测试"""

    def test_new_crawlers_registered(self):
        """测试新架构爬虫已注册"""
        from mdcx.crawlers.base import crawler_registry
        from mdcx.config.models import Website

        expected_crawlers = [
            Website.JAVBUS,
            Website.JAVDB,
            Website.MGSTAGE,
            Website.FC2,
            Website.FC2CLUB,
            Website.FC2HUB,
            Website.FC2PPVDB,
        ]

        for site in expected_crawlers:
            assert site in crawler_registry, f"{site.value} 未注册"

    def test_crawler_classes_can_instantiate(self):
        """测试所有爬虫类可以实例化"""
        from mdcx.crawlers.base import crawler_registry, get_crawler
        from mdcx.web_async import AsyncWebClient

        async_client = AsyncWebClient(timeout=1)

        for site in crawler_registry:
            crawler_class = get_crawler(site)
            assert crawler_class is not None, f"{site.value} 的爬虫类未找到"
            crawler = crawler_class(client=async_client)
            assert crawler.site() == site
