import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from common.log.log_manager import logger

# 自定义函数将 PosixPath 转换为字符串
def path_converter(obj):
    if isinstance(obj, Path):
        return str(obj)  # 将 Path 转换为字符串
    raise TypeError(f"Type {type(obj)} not serializable")

def custom_default(obj):
    if isinstance(obj, Decimal):
        return str(obj)  # 或者使用 float(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()  # 转换为 ISO 格式的字符串
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        return super().default(obj)

class Context(dict):
    """支持点语法访问字典键，并允许返回默认值的类"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _get_nested(self, keys):
        """ 根据嵌套的 keys 获取字典中的值 """
        current_value = self
        for key in keys:
            if isinstance(current_value, dict) and key in current_value:
                current_value = current_value[key]
            else:
                return None  # 找不到路径时返回 None
        return current_value

    def get(self, path, error_msg=None):
        """ 支持通过路径获取值，路径以 '.' 分隔 """
        try:
            keys = path.split('.')
            value = self._get_nested(keys)
            if value is None or value == "":
                if error_msg is None:
                    return None
                else:
                    raise Exception(f"{error_msg}")
            if isinstance(value, dict):
                return Context(value)
            return value
        except Exception as e:
            logger.error(f"context get error: {e}")
            raise Exception(f"{error_msg}")


    def get_def(self, path, default):
        """ 如果获取不到值，返回默认值 """
        try:
            keys = path.split('.')
            value = self._get_nested(keys)
            if value is None or value == "":
                if default is None:
                    return None
                else:
                    return default
            if isinstance(value, dict):
                return Context(value)
            return value
        except Exception as e:
            logger.error(f"context get_def error: {e}")
            raise Exception(f"{e}")

    def set(self, path, value):
        """ 支持通过路径设置值，路径不存在时自动创建 """
        try:
            keys = path.split('.')
            current_value = self
            for key in keys[:-1]:  # 遍历到倒数第二个键
                if key not in current_value:
                    current_value[key] = {}  # 如果不存在，创建一个空字典
                current_value = current_value[key]

            # 设置最终键的值
            current_value[keys[-1]] = value
            return self
        except Exception as e:
            logger.error(f"context set error: {e}")

# logger.debug(context.get("time")) # None
# logger.debug(context.get("time", "无时间")) # 抛出自定义异常！！
# logger.debug(context.get("config.datetime")) # {'time_now': '2024-11-23 22:31:48', 'time_yesterday': '2024-11-22 22:31:48'}
# logger.debug(context.get_def("time")) # 未设置默认值，抛出异常！
# logger.debug(context.get_def("time", "20241123"))  # 20241123
# logger.debug(context.get_def("config.datetime.time_now", "2024-11-23 00:00:00")) # 2024-11-23 22:35:02
# context.set("text", "022")
# logger.debug(context.get("text"))