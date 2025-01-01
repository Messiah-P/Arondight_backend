from functools import partial

from dao.models.pixiv.pixiv_prim_model import PixivPrim
from dao.service.pixiv import pixiv_prim_service, pixiv_dwld_info_service
from plugin.PixivAide.modules.downloader import Downloader
from plugin.PixivAide.enums.pixiv_collect_type_enum import PixivCollectTypeEnum
from plugin.PixivAide.enums.pixiv_download_status_enum import PixivDownloadStatusEnum
from plugin.PixivAide.enums.pixiv_modify_file_date_ind import PixivModifyFileDateIndEnum
from plugin.PixivAide.modules.extractor import Extractor
from plugin.PixivAide.thread.pixiv_dwld_listener import PixivDwldListener
from common.context.context import Context
from common.file.file_manager import FileManager
from common.thread.thread_pool import ThreadPool
from common.log.log_manager import logger
from common.utils.timer import Timer


class Crawler(object):
    def __init__(self, client, scoped_session):
        self.class_name = self.__class__.__name__
        self.client = client
        self.scoped_session = scoped_session
        self.file_manager = FileManager()
        self.downloader = Downloader(client, scoped_session)
        self.extractor = Extractor(client)

    def _submit_tasks_to_thread_pool(self, pixiv_dwld_info_po_list, context):
        """
        :功能描述: 提交下载任务
        :param pixiv_dwld_info_po_list: 待下载列表
        :Author: Lancelot
        :Date: 2024/12/22 22:18
        """
        modify_file_date_ind = context.get_def("pixiv.modify_file_date_ind",
                                               PixivModifyFileDateIndEnum.PIXIV_MODIFY_FILE_DATE_IND_0.code)
        thread_pool = ThreadPool(self.scoped_session, 1, 1)
        try:
            for pixiv_dwld_info_po in pixiv_dwld_info_po_list:
                thread_context = Context()
                thread_context.set("pixiv.download_task.pixiv_dwld_info_po", pixiv_dwld_info_po)
                thread_context.set("pixiv.download_task.modify_file_date_ind", modify_file_date_ind)
                thread_context.set("pixiv.download_task.lock_ind", context.get("pixiv.lock_ind"))
                logger.info(f"开始下载任务线程。")
                thread_pool.put(self.downloader.download_illust, thread_context, PixivDwldListener())
        except Exception as e:
            logger.warning(e)
            raise
        finally:
            thread_pool.close()

    def check_exist_prim(self, context):
        try:
            pid = context.get("pixiv.pid", "pid为空")
            sn = context.get_def("pixiv.sn", 0)
            collect_type = context.get("pixiv.collect_type", "作品收集类型为空")

            logger.info(f"查询主表中作品[{pid}]记录。")
            pixiv_prim_po = PixivPrim(pid=pid,
                                      sn=sn,
                                      collect_type=collect_type)
            result = pixiv_prim_service.select_by_pid_sn_collect_type(self.scoped_session, pixiv_prim_po)
            if result is None:
                logger.info(f"主表中无作品[{pid}]记录。")
            else:
                logger.warning(
                    f"主表中存在作品[{pid}-{sn}]记录，收集类型为[{PixivCollectTypeEnum.get_desc(collect_type)}]。")
                raise Exception(
                    f"主表中存在作品[{pid}-{sn}]记录，收集类型为[{PixivCollectTypeEnum.get_desc(collect_type)}]。")
        except Exception as e:
            logger.warning(e)
            raise

    def handle_metadata(self, context):
        thread_pool = ThreadPool(self.scoped_session, 1, 1)
        try:
            pid = context.get("pixiv.pid", "pid为空")
            collect_type = context.get("pixiv.collect_type", "作品收集类型为空")

            logger.info(f"开始下载作品[{pid}]。")
            thread_context = Context()
            thread_context.set("pixiv.metadata_task.pid", pid)
            thread_context.set("pixiv.metadata_task.collect_type", collect_type)
            logger.info(f"启动获取作品[{pid}]元数据并添加下载任务线程。")
            thread_pool.put(self.downloader.handle_download_metadata, thread_context)
        except Exception as e:
            logger.warning(e)
            raise
        finally:
            thread_pool.close()

    def execute_download_task(self, context):
        logger.info(f"获取下载任务进行下载。")
        pid = context.get("pixiv.pid", "pid为空")
        collect_type = context.get("pixiv.collect_type", "作品收集类型为空")
        try:
            # 获取待下载列表
            pixiv_dwld_info_po_list = pixiv_dwld_info_service.select_undownloaded_task_by_pid_and_collect_type(
                self.scoped_session,
                pid,
                collect_type)
            if pixiv_dwld_info_po_list:
                logger.info(f"获取到[pid={pid}]，收集类型为[{PixivCollectTypeEnum.get_desc(collect_type)}]的下载任务")
                self._submit_tasks_to_thread_pool(pixiv_dwld_info_po_list, context)
            else:
                raise Exception(f"未获取到[pid={pid}]，收集类型为[{PixivCollectTypeEnum.get_desc(collect_type)}]的下载任务。")
        except Exception as e:
            logger.warning(e)
            raise

    def download_by_pid(self, context):
        try:
            self.handle_metadata(context)
            Timer(120).retry(partial(self.execute_download_task, context))
        except Exception:
            raise
