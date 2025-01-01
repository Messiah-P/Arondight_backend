import datetime

from common.utils.plt_utils import generate_unique_8digit
from dao.models.pixiv.pixiv_prim_model import PixivPrim
from plugin.PixivAide.modules.downloader import Downloader
from common.file.file_manager import FileManager
from common.log.log_manager import logger
from common.thread.thread_pool import ThreadPool
from common.context.context import Context
from dao.service.pixiv import pixiv_prim_service, pixiv_dwld_info_service
from plugin.PixivAide.enums.pixiv_collect_type_enum import PixivCollectTypeEnum
from plugin.PixivAide.enums.pixiv_modify_file_date_ind import PixivModifyFileDateIndEnum
from plugin.PixivAide.modules.extractor import Extractor
from plugin.PixivAide.thread.pixiv_dwld_listener import PixivDwldListener


class DailyCrawler(object):

    def __init__(self, client, scoped_session):
        self.class_name = self.__class__.__name__
        self.client = client
        self.scoped_session = scoped_session
        self.file_manager = FileManager()
        self.downloader = Downloader(client, scoped_session)
        self.extractor = Extractor(client)

    def handle_metadata(self):
        logger.info("开始获取日榜作品。")
        logger.info("=" * 48)
        collect_type = PixivCollectTypeEnum.PIXIV_COLLECT_TYPE_2.code
        thread_pool = ThreadPool(self.scoped_session, 1, 1)
        try:
            pid_rank_list = self.extractor.get_page_info_daily(page_num=2)
            logger.success(f"获取日榜插画结束，共{len(pid_rank_list)}张！")
            logger.debug(f"作品id列表：{pid_rank_list}。")
            # 开始处理元数据和下载信息入表
            download_pid_rank_list = []
            pixiv_prim_pos = []
            # 查询主表中作品记录
            logger.info(f"查询主表中作品记录进行去重。")
            for illust in pid_rank_list:
                pixiv_prim_po = PixivPrim(pid=illust.get("pid"), sn=0, collect_type=collect_type)
                pixiv_prim_pos.append(pixiv_prim_po)

            result_list = pixiv_prim_service.select_by_pid_sn_collect_type_batch(self.scoped_session, pixiv_prim_pos)
            existing_pids = set((row.pid, row.sn, row.collect_type) for row in result_list)
            for illust in pid_rank_list:
                key = (illust.get("pid"), 0, collect_type)
                if key not in existing_pids:
                    download_pid_rank_list.append(illust)

            logger.success(f"生成需要更新的作品列表，长度为：{len(download_pid_rank_list)}")
            logger.debug(f"需要更新的作品列表：{download_pid_rank_list}")
            # TODO 修改下载数量控制
            for illust in download_pid_rank_list[:50]:
                thread_context = Context()
                thread_context.set("pixiv.metadata_task.pid", illust.get("pid"))
                thread_context.set("pixiv.metadata_task.rank_position", illust.get("rank_position"))
                thread_context.set("pixiv.metadata_task.rank_date", datetime.datetime.now().strftime("%Y-%m-%d"))
                thread_context.set("pixiv.metadata_task.collect_type", collect_type)
                thread_pool.put(self.downloader.handle_download_metadata, thread_context)
        except Exception as e:
            logger.warning("Exception:{}".format(e))
        finally:
            thread_pool.close()

    logger.info(f"获取日榜作品元数据，添加下载任务结束。")

    def execute_download_task(self, collect_type):
        thread_pool = ThreadPool(self.scoped_session, 1, 1)
        try:
            logger.info(f"获取下载任务进行下载。")
            logger.info("=" * 48)
            pixiv_dwld_info_po_list = pixiv_dwld_info_service.select_undownloaded_task_by_collect_type(
                self.scoped_session,
                collect_type)
            for pixiv_dwld_info_po in pixiv_dwld_info_po_list:
                thread_context = Context()
                thread_context.set("pixiv.download_task.pixiv_dwld_info_po", pixiv_dwld_info_po)
                thread_context.set("pixiv.download_task.modify_file_date_ind",
                                   PixivModifyFileDateIndEnum.PIXIV_MODIFY_FILE_DATE_IND_0.code)
                thread_context.set("pixiv.download_task.lock_ind", generate_unique_8digit())
                thread_pool.put(self.downloader.download_illust, thread_context, PixivDwldListener())
        except Exception as e:
            logger.warning(e)
        finally:
            thread_pool.close()

        logger.info(f"执行下载任务结束。")
