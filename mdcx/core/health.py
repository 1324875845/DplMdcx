"""
网站健康检查模块
用于在刮削前检测网站可达性
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..config.enums import Website
from ..models.log_buffer import LogBuffer

if TYPE_CHECKING:
    from ..config.models import Config
    from ..web_async import AsyncWebClient


@dataclass
class SiteHealth:
    """网站健康状态"""
    site: Website
    reachable: bool = False
    response_time: float = 0.0
    error: str = ""
    checked_at: float = field(default_factory=time.time)


class HealthChecker:
    """网站健康检查器"""

    def __init__(self, config: "Config", client: "AsyncWebClient"):
        self.config = config
        self.client = client
        self._cache: dict[Website, SiteHealth] = {}
        self._cache_ttl = 300  # 缓存 5 分钟

    async def check_site(self, site: Website, timeout: float = 10.0) -> SiteHealth:
        """
        检查单个网站的可达性

        Args:
            site: 要检查的网站
            timeout: 超时时间（秒）

        Returns:
            SiteHealth: 网站健康状态
        """
        # 检查缓存
        if site in self._cache:
            cached = self._cache[site]
            if time.time() - cached.checked_at < self._cache_ttl:
                return cached

        url = self.config.get_site_url(site)
        if not url:
            return SiteHealth(site=site, reachable=False, error="未配置 URL")

        start_time = time.time()
        try:
            # 发送 HEAD 请求检测可达性
            response, error = await asyncio.wait_for(
                self.client.request("HEAD", url),
                timeout=timeout
            )
            response_time = time.time() - start_time

            if response is None:
                health = SiteHealth(
                    site=site,
                    reachable=False,
                    response_time=response_time,
                    error=error or "连接失败"
                )
            elif response.status_code < 400:
                health = SiteHealth(
                    site=site,
                    reachable=True,
                    response_time=response_time
                )
            else:
                health = SiteHealth(
                    site=site,
                    reachable=False,
                    response_time=response_time,
                    error=f"HTTP {response.status_code}"
                )
        except asyncio.TimeoutError:
            health = SiteHealth(
                site=site,
                reachable=False,
                response_time=time.time() - start_time,
                error="连接超时"
            )
        except Exception as e:
            health = SiteHealth(
                site=site,
                reachable=False,
                response_time=time.time() - start_time,
                error=str(e)
            )

        # 缓存结果
        self._cache[site] = health
        return health

    async def check_sites(self, sites: list[Website], timeout: float = 10.0) -> dict[Website, SiteHealth]:
        """
        批量检查多个网站的可达性

        Args:
            sites: 要检查的网站列表
            timeout: 每个网站的超时时间（秒）

        Returns:
            dict: 网站健康状态字典
        """
        tasks = [self.check_site(site, timeout) for site in sites]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        health_map = {}
        for site, result in zip(sites, results):
            if isinstance(result, Exception):
                health_map[site] = SiteHealth(
                    site=site,
                    reachable=False,
                    error=str(result)
                )
            else:
                health_map[site] = result

        return health_map

    async def check_configured_sites(self, timeout: float = 10.0) -> dict[Website, SiteHealth]:
        """
        检查配置中所有网站的可达性

        Args:
            timeout: 每个网站的超时时间（秒）

        Returns:
            dict: 网站健康状态字典
        """
        # 收集所有配置的网站
        sites = set()
        for site_group in [
            self.config.website_youma,
            self.config.website_wuma,
            self.config.website_fc2,
            self.config.website_guochan,
            self.config.website_suren,
            self.config.website_oumei,
        ]:
            sites.update(site_group)

        return await self.check_sites(list(sites), timeout)

    def get_reachable_sites(self, health_map: dict[Website, SiteHealth]) -> list[Website]:
        """
        从健康状态字典中筛选可达的网站

        Args:
            health_map: 网站健康状态字典

        Returns:
            list: 可达的网站列表
        """
        return [site for site, health in health_map.items() if health.reachable]

    def log_health_status(self, health_map: dict[Website, SiteHealth]) -> None:
        """
        记录网站健康状态到日志

        Args:
            health_map: 网站健康状态字典
        """
        LogBuffer.log().write("\n 🏥 网站健康检查结果:")
        LogBuffer.log().write("=" * 50)

        reachable = []
        unreachable = []

        for site, health in sorted(health_map.items(), key=lambda x: x[0].value):
            if health.reachable:
                reachable.append(site)
                LogBuffer.log().write(
                    f"  ✅ {site.value:<20} ({health.response_time:.2f}s)"
                )
            else:
                unreachable.append(site)
                LogBuffer.log().write(
                    f"  ❌ {site.value:<20} ({health.error})"
                )

        LogBuffer.log().write("=" * 50)
        LogBuffer.log().write(f"  可达: {len(reachable)}, 不可达: {len(unreachable)}")

        if unreachable:
            LogBuffer.log().write(f"\n  ⚠️ 以下网站不可达，可能影响刮削结果:")
            for site in unreachable:
                LogBuffer.log().write(f"    - {site.value}")
