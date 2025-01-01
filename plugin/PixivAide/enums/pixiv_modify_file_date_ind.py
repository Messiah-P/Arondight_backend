from enum import Enum


class PixivModifyFileDateIndEnum(Enum):
    """
    枚举类：下载状态
    """
    PIXIV_MODIFY_FILE_DATE_IND_0 = (0, "不修改文件时间")
    PIXIV_MODIFY_FILE_DATE_IND_1 = (1, "修改文件时间。")

    def __init__(self, code, msg):
        self._code = code
        self._msg = msg

    @property
    def code(self):
        return self._code

    @property
    def msg(self):
        return self._msg
