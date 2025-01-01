from enum import Enum


class PixivRankTypeEnum(Enum):
    """
    枚举类：榜单类型
    """
    PIXIV_RANK_TYPE_0 = (0, "收集日榜作品。")
    PIXIV_RANK_TYPE_1 = (1, "收集周榜作品。")
    PIXIV_RANK_TYPE_2 = (2, "收集月榜作品。")

    def __init__(self, code, msg):
        self._code = code
        self._msg = msg

    @property
    def code(self):
        return self._code

    @property
    def msg(self):
        return self._msg

    @classmethod
    def get_msg_by_code(cls, code):
        for rank in cls:
            if rank.code == code:
                return rank.msg
        return None
