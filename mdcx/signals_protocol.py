"""
信号协议定义
用于解耦核心逻辑与具体 UI 框架（PyQt5/WebSocket）
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from .models.types import ShowData


@runtime_checkable
class SignalProtocol(Protocol):
    """信号协议接口"""

    stop: bool

    def add_log(self, *text) -> None:
        """添加日志"""
        ...

    def get_log(self) -> str:
        """获取日志"""
        ...

    def show_traceback_log(self, text: str) -> None:
        """显示错误追踪日志"""
        ...

    def show_log_text(self, text: str) -> None:
        """显示日志文本"""
        ...

    def show_scrape_info(self, before_info: str = "") -> None:
        """显示刮削信息"""
        ...

    def show_net_info(self, text: str) -> None:
        """显示网络信息"""
        ...

    def set_main_info(self, show_data: "ShowData | None" = None) -> None:
        """设置主界面信息"""
        ...

    def show_list_name(self, status: str, show_data: "ShowData", real_number: str = "") -> None:
        """显示列表名称"""
        ...


class NullSignals:
    """空信号实现，用于测试或无 UI 场景"""

    def __init__(self):
        self.stop = False
        self._logs: list[str] = []

    def add_log(self, *text) -> None:
        pass

    def get_log(self) -> str:
        return ""

    def show_traceback_log(self, text: str) -> None:
        print(text)

    def show_log_text(self, text: str) -> None:
        pass

    def show_scrape_info(self, before_info: str = "") -> None:
        pass

    def show_net_info(self, text: str) -> None:
        pass

    def set_main_info(self, show_data: "ShowData | None" = None) -> None:
        pass

    def show_list_name(self, status: str, show_data: "ShowData", real_number: str = "") -> None:
        pass


# 全局信号实例，可被替换
_signal_instance: SignalProtocol | None = None


def get_signal() -> SignalProtocol:
    """获取当前信号实例"""
    global _signal_instance
    if _signal_instance is None:
        # 默认使用 NullSignals
        _signal_instance = NullSignals()
    return _signal_instance


def set_signal_instance(instance: SignalProtocol) -> None:
    """设置信号实例"""
    global _signal_instance
    _signal_instance = instance
