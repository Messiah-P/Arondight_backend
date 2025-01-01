from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def convert_timestamp(timestamp: int, tz_name: str) -> datetime:
    """
    将 Unix 时间戳转换为指定时区的 datetime 对象。

    参数:
    - timestamp (int): Unix 时间戳（自 1970-01-01 UTC 起的秒数）。
    - tz_name (str): 时区名称（例如 'Asia/Shanghai'）。

    返回:
    - datetime: 时区感知的 datetime 对象。

    异常:
    - ValueError: 如果提供的时区名称无效。
    """
    try:
        # 将时间戳转换为 UTC 时间（时区感知对象）
        utc_time = datetime.fromtimestamp(timestamp, timezone.utc)

        # 创建指定时区对象
        target_timezone = ZoneInfo(tz_name)

        # 转换为目标时区时间
        target_time = utc_time.astimezone(target_timezone)

        return target_time
    except Exception as e:
        raise ValueError(f"无法转换时间戳。错误: {e}")
