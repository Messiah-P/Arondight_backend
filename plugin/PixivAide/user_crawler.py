from functools import partial

from common.database.transaction import transaction
from common.utils.plt_utils import generate_unique_8digit
from common.utils.timer import Timer
from dao.models.pixiv.pixiv_prim_model import PixivPrim
from plugin.PixivAide.modules.downloader import Downloader
from common.file.file_manager import FileManager
from common.log.log_manager import logger
from common.thread.thread_pool import ThreadPool
from common.context.context import Context
from dao.service.pixiv import pixiv_prim_service, pixiv_user_service, pixiv_dwld_info_service
from plugin.PixivAide.enums.pixiv_collect_type_enum import PixivCollectTypeEnum
from plugin.PixivAide.enums.pixiv_download_status_enum import PixivDownloadStatusEnum
from plugin.PixivAide.enums.pixiv_modify_file_date_ind import PixivModifyFileDateIndEnum
from plugin.PixivAide.modules.extractor import Extractor
from plugin.PixivAide.thread.pixiv_dwld_listener import PixivDwldListener


class UserCrawler(object):

    def __init__(self, client, scoped_session):
        self.class_name = self.__class__.__name__
        self.client = client
        self.scoped_session = scoped_session
        self.file_manager = FileManager()
        self.downloader = Downloader(client, scoped_session)
        self.extractor = Extractor(client)

    @transaction
    def add_following_user(self, scoped_session, pixiv_user_po):
        pixiv_user_service.check_pixiv_user(scoped_session, pixiv_user_po)

    def handle_metadata(self):
        logger.info("开始轮询获取关注画师作品。")
        logger.info("=" * 48)
        collect_type = PixivCollectTypeEnum.PIXIV_COLLECT_TYPE_0.code
        thread_pool = ThreadPool(self.scoped_session, 1, 1)
        try:
            pixiv_user_po_list = self.extractor.get_user_info_list()
        except Exception as e:
            logger.warning(f"获取关注画师列表出错：{e}")
            raise Exception(f"获取关注画师列表出错：{e}")
        else:
            if not pixiv_user_po_list:
                logger.warning(f"关注画师列表为空。")
                raise Exception(f"关注画师列表为空。")
            else:
                logger.success(f"成功获取关注画师列表.共关注{len(pixiv_user_po_list)}位用户。")
                for user in pixiv_user_po_list:
                    logger.debug(f"用户信息：{user.user_id}-{user.user_name}。")

        # 开始处理元数据和下载信息入表
        try:
            for index, pixiv_user_po in enumerate(pixiv_user_po_list):
                user_name = pixiv_user_po.user_name
                user_id = pixiv_user_po.user_id
                logger.info(f"开始获取画师{user_name}-{user_id}的作品。")

                # 获取所有作品ID
                all_pid_list = self.extractor.get_all_pid_list(pixiv_user_po)
                logger.debug(f"作品id列表：{all_pid_list}。")

                # 强制使用数据库去重，注意，先运行批量任务将已存在的画师和图片入库
                self.add_following_user(self.scoped_session, pixiv_user_po)
                db_latest_pid = pixiv_user_service.check_user_latest_pid(self.scoped_session, pixiv_user_po)
                logger.info(f"画师最新的作品ID：{db_latest_pid}")
                # 查询归类到画师目录下的作品数量
                pixiv_prim_po = PixivPrim(user_id=user_id,
                                          collect_type=collect_type,)
                collected_list = pixiv_prim_service.select_by_user_id_and_collect_type(self.scoped_session,
                                                                                       pixiv_prim_po)
                collected_pid_list = []
                for illust in collected_list:
                    collected_pid_list.append(illust.pid)
                collected_pid_num = len(collected_pid_list)
                # 去重，生成pid下载列表
                download_pid_list = []
                for pid in all_pid_list:
                    if pid not in collected_pid_list:
                        download_pid_list.append(pid)

                position = "({}/{})".format(index + 1, len(pixiv_user_po_list))
                # 满足作品更新条件
                if collected_pid_num < len(all_pid_list):
                    logger.info(
                        f"{position}更新画师：{user_id} - {user_name} | "
                        f"作品数：{len(all_pid_list)} | "
                        f"最新作品：{pixiv_user_po.latest_pid}")
                    logger.debug(f"需要更新的作品列表：{download_pid_list}")
                    for pid in download_pid_list:
                        thread_context = Context()
                        thread_context.set("pixiv.metadata_task.pid", pid)
                        thread_context.set("pixiv.metadata_task.collect_type", collect_type)
                        thread_pool.put(self.downloader.handle_download_metadata, thread_context)
        except Exception as e:
            logger.warning(e)
            raise
        finally:
            thread_pool.close()

        logger.info(f"获取关注画师更新作品元数据，添加下载任务结束。")

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
                                   PixivModifyFileDateIndEnum.PIXIV_MODIFY_FILE_DATE_IND_1.code)
                thread_context.set("pixiv.download_task.lock_ind", generate_unique_8digit())
                thread_pool.put(self.downloader.download_illust, thread_context, PixivDwldListener())
        except Exception as e:
            logger.warning(e)
            raise
        finally:
            thread_pool.close()

        logger.info(f"执行下载任务结束。")
