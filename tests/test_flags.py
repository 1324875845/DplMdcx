"""
Flags 模块测试
"""

import pytest
from pathlib import Path
from mdcx.models.flags import (
    Flags, ScrapeProgress, ScrapeCache, GlobalFlags,
    FileDoneDict, _Flags
)
from mdcx.models.enums import FileMode


class TestScrapeProgress:
    """ScrapeProgress 测试"""

    def test_default_values(self):
        progress = ScrapeProgress()
        assert progress.succ_count == 0
        assert progress.fail_count == 0
        assert progress.file_mode == FileMode.Default
        assert progress.reachable_sites == []

    def test_reset(self):
        progress = ScrapeProgress()
        progress.succ_count = 10
        progress.fail_count = 5
        progress.reachable_sites = ["site1"]
        progress.reset()
        assert progress.succ_count == 0
        assert progress.fail_count == 0
        assert progress.reachable_sites == []


class TestScrapeCache:
    """ScrapeCache 测试"""

    def test_default_values(self):
        cache = ScrapeCache()
        assert cache.file_new_path_dic == {}
        assert cache.json_data_dic == {}
        assert cache.failed_list == []

    def test_reset(self):
        cache = ScrapeCache()
        cache.json_data_dic["test"] = "value"
        cache.failed_list.append(("path", "error"))
        cache.reset()
        assert cache.json_data_dic == {}
        assert cache.failed_list == []


class TestGlobalFlags:
    """GlobalFlags 测试"""

    def test_default_values(self):
        global_flags = GlobalFlags()
        assert global_flags.appoint_url == ""
        assert global_flags.website_name == ""
        assert global_flags.local_number_set == set()


class TestFlags:
    """Flags 组合类测试"""

    def test_proxy_attribute_access(self):
        # 测试通过 Flags 访问 progress 属性
        Flags.progress.succ_count = 5
        assert Flags.succ_count == 5

    def test_proxy_cache_access(self):
        # 测试通过 Flags 访问 cache 属性
        Flags.cache.json_data_dic["test"] = "value"
        assert Flags.json_data_dic["test"] == "value"

    def test_proxy_global_access(self):
        # 测试通过 Flags 访问 global_flags 属性
        Flags.global_flags.appoint_url = "http://test.com"
        assert Flags.appoint_url == "http://test.com"

    def test_reset(self):
        # 测试 reset 方法
        Flags.progress.succ_count = 10
        Flags.cache.json_data_dic["test"] = "value"
        Flags.reset()
        assert Flags.progress.succ_count == 0
        assert Flags.cache.json_data_dic == {}

    def test_backward_compatibility(self):
        # 测试向后兼容性
        Flags.succ_count = 0
        Flags.fail_count = 0
        assert Flags.succ_count == 0
        assert Flags.fail_count == 0


class TestFileDoneDict:
    """FileDoneDict 测试"""

    def test_create(self):
        from mdcx.models.flags import FileDoneDict
        d = FileDoneDict(
            poster=None,
            thumb=None,
            fanart=None,
            trailer=None,
            local_poster=None,
            local_thumb=None,
            local_fanart=None,
            local_trailer=None,
        )
        assert d["poster"] is None
        assert d["thumb"] is None
