import pytest

try:
    import parsel
    import lxml
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

pytestmark = pytest.mark.skipif(not HAS_DEPS, reason="需要 parsel 和 lxml 依赖")


def test_crawler_classes():
    """测试所有注册的爬虫类可正常初始化."""
    from mdcx.crawlers.base import crawler_registry, get_crawler
    from mdcx.web_async import AsyncWebClient

    async_client = AsyncWebClient(timeout=1)
    for site in crawler_registry:
        crawler_class = get_crawler(site)
        assert crawler_class is not None, f"未找到 {site} 的爬虫"
        crawler_class(client=async_client)
