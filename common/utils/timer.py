import time
import random
import threading

from common.log.log_manager import logger


def random_cycle_time():
    return random.choice([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41])


class Timer:
    def __init__(self, max_wait_time=120):
        # 每轮等待时间
        self.poll_cycle_time = random_cycle_time
        # 记录已等待时间
        self.wait_time = 0
        # 官方限制时间-粗略估算
        self.max_wait_time = max_wait_time

    def retry(self, func):
        """
        * 功能描述: 根据时间间隔重复执行函数，直到成功或超过最大等待时间
        * @fileName: timer.py
        * @Author: Lancelot
        * @Date: 2024/12/31 14:27
        """
        while self.wait_time <= self.max_wait_time:
            try:
                return func()
            except Exception as e:
                logger.warning(e)
                logger.info(
                    f"线程ID:{threading.get_ident()}:已休眠{self.wait_time}/{self.max_wait_time}秒,尝试重新访问。")
                time.sleep(self.poll_cycle_time())
                self.wait_time += self.poll_cycle_time()

        logger.info(
            f"线程ID:{threading.get_ident()}:已休眠{self.wait_time}/{self.max_wait_time}秒，尝试多次失败，超过限制时间，任务失败。")
        raise Exception(
            f"线程ID:{threading.get_ident()}:已休眠{self.wait_time}/{self.max_wait_time}秒，尝试多次失败，超过限制时间，任务失败。")
