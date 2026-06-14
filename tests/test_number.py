"""
番号识别模块测试
"""

import pytest
from mdcx.number import (
    is_uncensored,
    is_suren,
    get_number_letters,
    get_file_number,
)


class TestIsUncensored:
    """无码番号检测测试"""

    @pytest.mark.parametrize("number,expected", [
        ("n1234", True),
        ("259LUXU-1456", False),
        ("HEYZO-1234", True),
        ("CWP-123", True),
        ("LAF-456", True),
        ("SSIS-001", False),
        ("ABP-123", False),
        ("sexart.15.06.14", True),
        ("20.05.15.01", True),
    ])
    def test_is_uncensored(self, number, expected):
        assert is_uncensored(number) == expected


class TestIsSuren:
    """素人番号检测测试"""

    @pytest.mark.parametrize("number,expected", [
        ("259LUXU-1456", True),
        ("LUXU-1456", True),
        ("SIRO-4605", True),
        ("300MIUM-382", True),
        ("SSIS-001", False),
        ("ABP-123", False),
    ])
    def test_is_suren(self, number, expected):
        assert is_suren(number) == expected


class TestGetNumberLetters:
    """番号字母部分提取测试"""

    @pytest.mark.parametrize("number,expected", [
        ("SSIS-001", "SSIS"),
        ("ABP-123", "ABP"),
        ("FC2-1234567", "FC2"),
        ("259LUXU-1456", "259LUXU"),
        ("HEYZO-1234", "HEYZO"),
        ("Mywife No.1111", "MYWIFE"),
    ])
    def test_get_number_letters(self, number, expected):
        assert get_number_letters(number) == expected


class TestGetFileNumber:
    """文件名番号提取测试"""

    @pytest.mark.parametrize("filename,expected", [
        ("SSIS-001.mp4", "SSIS-001"),
        ("ABP-123.mkv", "ABP-123"),
        ("FC2-1234567.mp4", "FC2-1234567"),
        ("259LUXU-1456.avi", "259LUXU-1456"),
        ("HEYZO-1234-cd1.mp4", "HEYZO-1234"),
        ("Mywife No.1111.mp4", "Mywife No.1111"),
    ])
    def test_get_file_number(self, filename, expected):
        # 简化测试，不传入 escape_string_list
        assert get_file_number(filename, []) == expected

    def test_fc2_formats(self):
        # 测试 FC2 各种格式
        assert get_file_number("FC2-PPV-1234567.mp4", []) == "FC2-1234567"
        assert get_file_number("FC2PPV1234567.mp4", []) == "FC2-1234567"
        assert get_file_number("fc2_1234567.mp4", []) == "FC2-1234567"

    def test_heyzo_formats(self):
        # 测试 HEYZO 格式
        assert get_file_number("HEYZO-1234.mp4", []) == "HEYZO-1234"
        assert get_file_number("heyzo1234.mp4", []) == "HEYZO-1234"
