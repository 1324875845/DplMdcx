from asyncio import Event
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypedDict

from .enums import FileMode
from .types import ScrapeResult


class FileDoneDict(TypedDict):
    poster: Path | None
    thumb: Path | None
    fanart: Path | None
    trailer: Path | None
    local_poster: Path | None
    local_thumb: Path | None
    local_fanart: Path | None
    local_trailer: Path | None


@dataclass
class ScrapeProgress:
    """刮削进度状态 - 可移入 Scraper 实例"""
    rest_time_convert: int = 0
    rest_time_convert_: int = 0
    total_kills: int = 0
    now_kill: int = 0
    success_save_time: float = 0.0
    next_start_time: float = 0.0
    count_claw: int = 0
    can_save_remain: bool = False
    remain_list: list[Path] = field(default_factory=list)
    new_again_dic: dict[Path, tuple[str, str, str]] = field(default_factory=dict)
    again_dic: dict[Path, tuple[str, str, str]] = field(default_factory=dict)
    start_time: float = 0.0
    file_mode: FileMode = FileMode.Default
    counting_order: int = 0
    total_count: int = 0
    rest_now_begin_count: int = 0
    sleep_end: Event = field(default_factory=Event)
    rest_next_begin_time: float = 0.0
    scrape_starting: int = 0
    scrape_started: int = 0
    scrape_done: int = 0
    succ_count: int = 0
    fail_count: int = 0
    scrape_start_time: float = 0.0
    success_list: set[Path] = field(default_factory=set)
    stop_other: bool = True
    reachable_sites: list = field(default_factory=list)

    def reset(self) -> None:
        self.rest_time_convert = 0
        self.rest_time_convert_ = 0
        self.total_kills = 0
        self.now_kill = 0
        self.success_save_time = 0.0
        self.next_start_time = 0.0
        self.count_claw = 0
        self.can_save_remain = False
        self.remain_list = []
        self.new_again_dic = {}
        self.again_dic = {}
        self.start_time = 0.0
        self.file_mode = FileMode.Default
        self.counting_order = 0
        self.total_count = 0
        self.rest_now_begin_count = 0
        self.sleep_end.set()
        self.rest_next_begin_time = 0.0
        self.scrape_starting = 0
        self.scrape_started = 0
        self.scrape_done = 0
        self.succ_count = 0
        self.fail_count = 0
        self.scrape_start_time = 0.0
        self.success_list = set()
        self.stop_other = True
        self.reachable_sites = []


@dataclass
class ScrapeCache:
    """刮削缓存数据"""
    file_new_path_dic: dict[Path, list[Path]] = field(default_factory=dict)
    pic_catch_set: set[Path] = field(default_factory=set)
    file_done_dic: dict[str, FileDoneDict] = field(default_factory=dict)
    extrafanart_deal_set: set[Path] = field(default_factory=set)
    trailer_deal_set: set[Path] = field(default_factory=set)
    theme_videos_deal_set: set[Path] = field(default_factory=set)
    nfo_deal_set: set[Path] = field(default_factory=set)
    json_get_set: set[str] = field(default_factory=set)
    json_data_dic: dict[str, ScrapeResult] = field(default_factory=dict)
    failed_list: list[tuple[Path, str]] = field(default_factory=list)

    def reset(self) -> None:
        self.file_new_path_dic = {}
        self.pic_catch_set = set()
        self.file_done_dic = {}
        self.extrafanart_deal_set = set()
        self.trailer_deal_set = set()
        self.theme_videos_deal_set = set()
        self.nfo_deal_set = set()
        self.json_get_set = set()
        self.json_data_dic = {}
        self.failed_list = []


@dataclass
class GlobalFlags:
    """全局状态 - 跨刮削任务持久化"""
    # 指定刮削
    appoint_url: str = ""
    website_name: str = ""
    img_path: str = ""

    # show
    log_txt: Any = None
    scrape_like_text: str = ""
    main_mode_text: str = ""

    single_file_path: Path = field(default_factory=Path)

    # for missing
    actor_numbers_dic: dict[str, list[str]] = field(default_factory=dict)
    local_number_set: set[str] = field(default_factory=set)
    local_number_cnword_set: set[str] = field(default_factory=set)


# 向后兼容：保留 Flags 作为全局单例
@dataclass
class _Flags:
    """向后兼容的 Flags 类，组合 ScrapeProgress、ScrapeCache 和 GlobalFlags"""
    progress: ScrapeProgress = field(default_factory=ScrapeProgress)
    cache: ScrapeCache = field(default_factory=ScrapeCache)
    global_flags: GlobalFlags = field(default_factory=GlobalFlags)

    def reset(self) -> None:
        self.progress.reset()
        self.cache.reset()

    # 代理属性访问，保持向后兼容
    def __getattr__(self, name: str):
        if name in ('progress', 'cache', 'global_flags', 'reset'):
            return super().__getattribute__(name)
        # 尝试从 progress 获取
        if hasattr(self.progress, name):
            return getattr(self.progress, name)
        # 尝试从 cache 获取
        if hasattr(self.cache, name):
            return getattr(self.cache, name)
        # 尝试从 global_flags 获取
        if hasattr(self.global_flags, name):
            return getattr(self.global_flags, name)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def __setattr__(self, name: str, value):
        if name in ('progress', 'cache', 'global_flags'):
            super().__setattr__(name, value)
            return
        # 尝试设置到 progress
        if hasattr(self.progress, name):
            setattr(self.progress, name, value)
            return
        # 尝试设置到 cache
        if hasattr(self.cache, name):
            setattr(self.cache, name, value)
            return
        # 尝试设置到 global_flags
        if hasattr(self.global_flags, name):
            setattr(self.global_flags, name, value)
            return
        super().__setattr__(name, value)


Flags = _Flags()
