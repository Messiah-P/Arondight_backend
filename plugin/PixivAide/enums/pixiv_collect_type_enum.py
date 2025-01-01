from enum import Enum


class PixivCollectTypeEnum(Enum):
    """
    枚举类：作品收集类型
    """
    PIXIV_COLLECT_TYPE_0 = (0, "收集画师作品")
    PIXIV_COLLECT_TYPE_1 = (1, "收集收藏作品")
    PIXIV_COLLECT_TYPE_2 = (2, "收集日榜作品")
    PIXIV_COLLECT_TYPE_3 = (3, "收集周榜作品")
    PIXIV_COLLECT_TYPE_4 = (4, "收集月榜作品")
    PIXIV_COLLECT_TYPE_8 = (8, "手动下载作品")

    def __init__(self, code, desc):
        self._code = code
        self._desc = desc

    @property
    def code(self):
        return self._code

    @property
    def desc(self):
        return self._desc

    @classmethod
    def get_desc(cls, code):
        for item in cls:
            if item.code == code:
                return item.desc
        return Exception(f"未匹配到作品收集类型")


