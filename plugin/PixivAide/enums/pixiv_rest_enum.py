from enum import Enum


class PixivRestEnum(Enum):
    """
    枚举类：公开/非公开关注
    """
    PIXIV_REST_SHOW = ("show", "公开关注")
    PIXIV_REST_HIDE = ("hide", "非公开关注")

    def __init__(self, state, msg):
        self._state = state
        self._msg = msg

    @property
    def state(self):
        return self._state

    @property
    def msg(self):
        return self._msg
