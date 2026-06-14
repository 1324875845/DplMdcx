"""
网站健康检查模块测试
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from mdcx.core.health import HealthChecker, SiteHealth
from mdcx.config.models import Website


class TestSiteHealth:
    """SiteHealth 数据类测试"""

    def test_default_values(self):
        health = SiteHealth(site=Website.JAVBUS)
        assert health.site == Website.JAVBUS
        assert health.reachable is False
        assert health.response_time == 0.0
        assert health.error == ""

    def test_with_values(self):
        health = SiteHealth(
            site=Website.JAVDB,
            reachable=True,
            response_time=1.5,
            error=""
        )
        assert health.reachable is True
        assert health.response_time == 1.5


class TestHealthChecker:
    """HealthChecker 测试"""

    @pytest.fixture
    def mock_config(self):
        config = MagicMock()
        config.get_site_url.return_value = "https://example.com"
        return config

    @pytest.fixture
    def mock_client(self):
        client = AsyncMock()
        return client

    @pytest.mark.asyncio
    async def test_check_site_success(self, mock_config, mock_client):
        # 模拟成功响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.request = AsyncMock(return_value=(mock_response, ""))

        checker = HealthChecker(mock_config, mock_client)
        health = await checker.check_site(Website.JAVBUS, timeout=5.0)

        assert health.reachable is True
        assert health.error == ""

    @pytest.mark.asyncio
    async def test_check_site_failure(self, mock_config, mock_client):
        # 模拟失败响应
        mock_client.request = AsyncMock(return_value=(None, "Connection refused"))

        checker = HealthChecker(mock_config, mock_client)
        health = await checker.check_site(Website.JAVBUS, timeout=5.0)

        assert health.reachable is False
        assert "Connection refused" in health.error

    @pytest.mark.asyncio
    async def test_check_site_timeout(self, mock_config, mock_client):
        # 模拟超时
        import asyncio
        mock_client.request = AsyncMock(side_effect=asyncio.TimeoutError())

        checker = HealthChecker(mock_config, mock_client)
        health = await checker.check_site(Website.JAVBUS, timeout=1.0)

        assert health.reachable is False
        assert "超时" in health.error

    @pytest.mark.asyncio
    async def test_check_site_no_url(self, mock_config, mock_client):
        mock_config.get_site_url.return_value = ""

        checker = HealthChecker(mock_config, mock_client)
        health = await checker.check_site(Website.JAVBUS)

        assert health.reachable is False
        assert "未配置" in health.error

    def test_get_reachable_sites(self, mock_config, mock_client):
        checker = HealthChecker(mock_config, mock_client)
        health_map = {
            Website.JAVBUS: SiteHealth(site=Website.JAVBUS, reachable=True),
            Website.JAVDB: SiteHealth(site=Website.JAVDB, reachable=False),
            Website.MGSTAGE: SiteHealth(site=Website.MGSTAGE, reachable=True),
        }

        reachable = checker.get_reachable_sites(health_map)
        assert Website.JAVBUS in reachable
        assert Website.MGSTAGE in reachable
        assert Website.JAVDB not in reachable
