import os
import sys
import time

from loguru import logger

from common.constants.file_constant import FileConstant
from common.file.file_manager import FileManager
from pathlib import Path


class LogManager:
    def __init__(self, module_name, level="DEBUG", log_path=None):
        self.file_manager = FileManager()
        self.module_name = module_name
        self.level = level
        self.log_path = log_path or self._default_log_path()
        self._setup_logger()

    def _default_log_path(self):
        """返回默认日志路径"""
        abs_log_path = self.file_manager.generate_abs_file_path(FileConstant.LOG_PATH)
        return abs_log_path

    def _setup_logger(self):
        """设置日志记录器"""
        os.makedirs(self.log_path, exist_ok=True)

        # 移除默认 logger
        logger.remove()

        # 添加控制台和文件输出
        self._add_console_handler()
        self._add_file_handler()

    def _add_console_handler(self):
        """添加控制台日志处理器"""
        logger.add(sys.stderr, level=self.level)

    def _add_file_handler(self):
        """添加文件日志处理器"""
        log_file_path = Path(self.log_path) / f"{self.module_name}_{time.strftime('%Y-%m-%d')}.log"
        logger.add(log_file_path, encoding="utf-8", rotation="00:00", enqueue=True, level=self.level)
