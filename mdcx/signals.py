import threading
import time
from typing import TYPE_CHECKING, Literal

from .models.types import ShowData
from .signals_protocol import SignalProtocol
from .utils import singleton

if TYPE_CHECKING:
    from .server.signals import ServerSignals


@singleton
class Signals(SignalProtocol):
    """PyQt5 信号实现"""

    def __init__(self):
        self._init_qt()
        self.log_lock = threading.Lock()
        self.detail_log_list = []
        self.stop = False

    def _init_qt(self):
        """延迟初始化 PyQt5 信号"""
        from PyQt5.QtCore import QObject, pyqtSignal

        # 创建一个内部 QObject 来承载信号
        class _SignalEmitter(QObject):
            log_text = pyqtSignal(str)
            scrape_info = pyqtSignal(str)
            net_info = pyqtSignal(str)
            exec_set_main_info = pyqtSignal(ShowData)
            change_buttons_status = pyqtSignal()
            reset_buttons_status = pyqtSignal()
            set_label_file_path = pyqtSignal(str)
            label_result = pyqtSignal(str)
            logs_failed_settext = pyqtSignal(str)
            view_success_file_settext = pyqtSignal(str)
            exec_set_processbar = pyqtSignal(int)
            exec_exit_app = pyqtSignal()
            view_failed_list_settext = pyqtSignal(str)
            exec_show_list_name = pyqtSignal(str, ShowData, str)
            logs_failed_show = pyqtSignal(str)

        self._emitter = _SignalEmitter()

    def __getattr__(self, name: str):
        """代理信号访问到内部 emitter"""
        if name.startswith('_'):
            raise AttributeError(name)
        return getattr(self._emitter, name)

    def add_log(self, *text):
        """打印日志到日志页下方详情框"""
        if self.stop:
            return
        try:
            with self.log_lock:
                self.detail_log_list.append(f" ⏰ {time.strftime('%H:%M:%S', time.localtime())} {' '.join(text)}")
        except Exception:
            pass

    def get_log(self):
        with self.log_lock:
            text = "\n".join(self.detail_log_list)
            self.detail_log_list = []
        return text

    def show_traceback_log(self, text):
        print(text)
        self.add_log(text)

    def show_log_text(self, text):
        self._emitter.log_text.emit(text)

    def show_scrape_info(self, before_info=""):
        self._emitter.scrape_info.emit(before_info)

    def show_net_info(self, text):
        self._emitter.net_info.emit(text)

    def set_main_info(self, show_data=None):
        if show_data is None:
            show_data = ShowData.empty()
        self._emitter.exec_set_main_info.emit(show_data)

    def show_list_name(self, status: Literal["succ", "fail"], show_data: ShowData, real_number=""):
        self._emitter.exec_show_list_name.emit(status, show_data, real_number)


signal_qt = Signals()
signal: "Signals | ServerSignals" = signal_qt


def set_signal(signal_instance: "Signals | ServerSignals"):
    global signal
    signal = signal_instance
