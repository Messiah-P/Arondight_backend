from enum import Enum


class PixivOrganizeModeEnum(Enum):
    """
    枚举类：数据库更新类型
    """
    # 全量更新：忽略原本的数据库记录
    PIXIV_ORGANIZE_MODE_0 = (0, "全量更新。")
    # 增量更新：根据原本的数据库记录
    PIXIV_ORGANIZE_MODE_1 = (1, "增量更新。")

    def __init__(self, code, msg):
        self._code = code
        self._msg = msg

    @property
    def code(self):
        return self._code

    @property
    def msg(self):
        return self._msg
