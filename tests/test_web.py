"""
网络下载模块测试
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import re


class TestWpComReferer:
    """wp.com CDN referer 处理测试"""

    def test_extract_domain_from_wp_url(self):
        # 测试从 wp.com URL 提取原站域名
        url = "https://i0.wp.com/example.com/wp-content/uploads/image.jpg"
        match = re.search(r"wp\.com/(.+?)/wp-content", url)
        if match:
            domain = match.group(1)
            assert domain == "example.com"

    def test_wp_url_patterns(self):
        # 测试各种 wp.com URL 格式
        urls = [
            "https://i0.wp.com/site1.com/wp-content/uploads/test.jpg",
            "https://i1.wp.com/site2.org/wp-content/uploads/test.jpg",
            "https://i2.wp.com/site3.net/wp-content/uploads/test.jpg",
        ]
        for url in urls:
            match = re.search(r"wp\.com/(.+?)/wp-content", url)
            assert match is not None, f"Failed to match: {url}"


class TestNumberRecognition:
    """番号识别集成测试"""

    def test_common_formats(self):
        from mdcx.number import get_file_number

        test_cases = [
            # (filename, expected_number)
            ("[ABC-123] Title.mp4", "ABC-123"),
            ("ABC-123 Title.mp4", "ABC-123"),
        ]

        for filename, expected in test_cases:
            result = get_file_number(filename, [])
            assert result == expected, f"Failed for {filename}: got {result}"

    def test_cd_part_recognition(self):
        # 测试分集识别
        from mdcx.number import get_file_number

        # 这些文件名应该正确提取番号（不包含分集信息）
        assert get_file_number("SSIS-001-cd1.mp4", []) == "SSIS-001"
        assert get_file_number("SSIS-001_part1.mp4", []) == "SSIS-001"


class TestConfigModels:
    """配置模型测试"""

    def test_website_enum(self):
        from mdcx.config.models import Website

        # 测试网站枚举值
        assert Website.JAVBUS.value == "javbus"
        assert Website.JAVDB.value == "javdb"
        assert Website.MGSTAGE.value == "mgstage"
        assert Website.FC2.value == "fc2"

    def test_language_enum(self):
        from mdcx.config.enums import Language

        # 测试语言枚举值
        assert Language.JP.value == "jp"
        assert Language.ZH_CN.value == "zh_cn"
        assert Language.UNDEFINED.value == "undefined"
