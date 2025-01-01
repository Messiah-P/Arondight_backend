from enum import Enum


class PixivDownloadStatusEnum(Enum):
    """
    枚举类：下载状态
    """
    PIXIV_DOWNLOAD_STATUS_0 = ("0", "作品未下载。")
    PIXIV_DOWNLOAD_STATUS_1 = ("1", "作品下载成功。")
    PIXIV_DOWNLOAD_STATUS_2 = ("2", "作品下载失败。")

    def __init__(self, code, msg):
        self._code = code
        self._msg = msg

    @property
    def code(self):
        return self._code

    @property
    def msg(self):
        return self._msg
