from enum import Enum


class PltSvcCdCntlEnum(Enum):
    """
    枚举类：服务状态代码
    """
    STATE_1 = (1, "启用")
    STATE_2 = (2, "停用")

    def __init__(self, state, msg):
        self._state = state
        self._msg = msg

    @property
    def state(self):
        return self._state

    @property
    def msg(self):
        return self._msg
