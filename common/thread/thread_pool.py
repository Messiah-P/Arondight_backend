"""
* 功能描述: 一个基于thread和queue的线程池,
           任务为队列元素,动态创建线程并重复利用.
           将任务放入队列、创建新线程（如果需要）、创建并启动线程，线程开始执行 self.call()，从队列中获取并执行任务
           通过close和terminate关闭线程池.
* @fileName: thread_pool.py
* @Author: Messiah
* @Date: 2024/9/5 15:52
"""

import queue
import threading
import contextlib

from common.thread.listener import Listener
from common.log.log_manager import logger

# 创建空对象,用于停止线程
StopEvent = object()


class ThreadPool:

    def __init__(self, scoped_session, max_thread_num=1, max_task_num=1):
        """
        * 功能描述: 初始化线程池
        * @param: max_thread_num: 线程池最大线程数量
        * @param: max_task_num: 任务队列长度
        * @fileName: thread_pool.py
        * @Author: Messiah
        * @Date: 2024/9/5 15:55
        """
        self.scoped_session = scoped_session
        if max_task_num:
            # 如果提供了最大任务数的参数，则将队列的最大元素个数设置为这个值。
            self.queue = queue.Queue(max_task_num)
        else:
            # 默认队列可接受无限多个的任务
            self.queue = queue.Queue()
        # 设置线程池最多可实例化的线程数
        self.max_thread_num = max_thread_num
        # 任务取消标识
        self.cancel = False
        # 任务中断标识
        self.terminal = False
        # 已实例化的线程列表
        self.generate_threads_list = []
        # 处于空闲状态的线程列表
        self.free_threads_list = []

    def call(self):
        """
        循环去获取任务函数并执行任务函数。在正常情况下，每个线程都保存生存状态,直到获取线程终止的flag。
        """
        # 获取当前线程的名字
        current_thread = threading.current_thread().name
        # 将当前线程的名字加入已实例化的线程列表中
        self.generate_threads_list.append(current_thread)
        # 从任务队列中获取一个任务，若任务列表无新增任务，则等待
        event = self.queue.get()
        # 让获取的任务不是终止线程的标识对象时
        while event != StopEvent:
            # 解析任务中封装的三个参数
            func, thread_context, listener = event
            logger.debug(f"启动线程：{current_thread}。")
            try:
                listener.before_action(self.scoped_session, thread_context)
                # 抓取异常，防止线程因为异常退出
                try:
                    # 正常执行任务函数
                    func(thread_context)
                    status = True
                    msg = "任务执行成功！"
                    logger.debug(f"线程{current_thread}任务执行成功！")
                except Exception as e:
                    status = False
                    msg = f"任务执行失败：{e}"
                    logger.error(f"线程{current_thread}任务执行失败：{e}")
                listener.after_action(self.scoped_session, thread_context, status, msg)
            except Exception as e:
                logger.error(f"线程失败{current_thread}：{e}")
            # 当某个线程正常执行完一个任务时，先执行worker_state方法
            with self.worker_state(current_thread):
                # 如果强制关闭线程的flag开启，则传入一个StopEvent元素
                if self.terminal:
                    event = StopEvent
                # 否则获取一个正常的任务，并回调worker_state方法的yield语句
                else:
                    # 从这里开始又是一个正常的任务循环
                    event = self.queue.get()
        else:
            # 一旦发现任务是个终止线程的标识元素，将线程从已创建线程列表中删除
            self.generate_threads_list.remove(current_thread)

    def generate_thread(self):
        """
        创建一个线程
        """
        # 每个线程都执行call方法
        new_thread = threading.Thread(target=self.call)
        new_thread.start()

    def put(self, func, thread_context, listener=Listener()):
        """
        * 功能描述: 往任务队列里放入一个任务
        * @param: func: 任务函数
        * @param: thread_context: 变量池
        * @param: listener: 监听函数
        * @return: 如果线程池已经终止，则返回True否则None
        * @fileName: thread_pool.py
        * @Author: Messiah
        * @Date: 2024/9/5 16:00
        """
        # 先判断标识，看看任务是否取消了
        if self.cancel:
            return
        # 如果没有空闲的线程，并且已创建的线程的数量小于预定义的最大线程数，则创建新线程。
        if len(self.free_threads_list) == 0 and len(self.generate_threads_list) < self.max_thread_num:
            self.generate_thread()
        # 构造任务参数元组，分别是调用的函数，变量池，监听函数。
        w = (func, thread_context, listener,)
        # 将任务放入队列
        self.queue.put(w)
        logger.debug(f"新任务入队列。")

    def close(self):
        """
        * 功能描述: 执行完所有的任务后，让所有线程都停止
        * @fileName: thread_pool.py
        * @Author: Messiah
        * @Date: 2024/9/6 15:57
        """
        # 设置flag
        self.cancel = True
        # 计算已创建线程列表中线程的个数，
        # 然后往任务队列里推送相同数量的终止线程的标识元素
        full_size = len(self.generate_threads_list)
        while full_size:
            self.queue.put(StopEvent)
            full_size -= 1
        logger.debug(f"清理线程池。")

    def terminate(self):
        """
        * 功能描述: 在任务执行过程中，终止线程，提前退出。
        * @fileName: thread_pool.py
        * @Author: Messiah
        * @Date: 2024/9/6 15:58
        """
        self.terminal = True
        # 强制性的停止线程
        while self.generate_threads_list:
            self.queue.put(StopEvent)

    @contextlib.contextmanager
    def worker_state(self, worker_thread):
        """
        * 功能描述: 用于记录空闲的线程，或从空闲列表中取出线程处理任务，装饰器用于上下文管理
        * @fileName: thread_pool.py
        * @Author: Messiah
        * @Date: 2024/9/6 15:58
        """
        # 任务执行结束
        # 将当前线程，添加到空闲线程列表中
        self.free_threads_list.append(worker_thread)
        # 捕获异常
        try:
            # 获取任务，若没有任务，则等待
            yield
        finally:
            # 将线程从空闲列表中移除
            self.free_threads_list.remove(worker_thread)
            # 开始执行任务
