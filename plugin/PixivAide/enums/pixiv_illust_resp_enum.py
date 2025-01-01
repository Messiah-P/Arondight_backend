from enum import Enum


class PixivIllustRespEnum(Enum):
    """
    枚举类：ajax请求illust响应
    """
    PIXIV_ILLUST_RESP_1 = ("1", "该作品已被删除, 或作品ID不存在。")
    PIXIV_ILLUST_RESP_2 = ("2", "无法找到您所请求的页面")
    PIXIV_ILLUST_RESP_3 = ("3", "作者已设置为私密,尚无权限浏览该作品")
    PIXIV_ILLUST_RESP_4 = ("4", "尚无权限浏览该作品")
    PIXIV_ILLUST_RESP_5 = ("5", "出现错误。请稍后再试。")

    def __init__(self, code, msg):
        self._code = code
        self._msg = msg

    @property
    def code(self):
        return self._code

    @property
    def msg(self):
        return self._msg
