import asyncio
import time
from multiprocessing import Process

from common.database.db_connector import DbConnector
from common.enums.plt_svc_cd_cntl_enum import PltSvcCdCntlEnum
from dao.models.plt.plt_svc_cd_cntl_model import PltSvcCdCntl
from dao.service.plt import plt_svc_cd_cntl_service
from plugin.PixivAide.modules.client import Client
from common.log.log_manager import logger, LogManager
from plugin.PixivAide.enums.pixiv_collect_type_enum import PixivCollectTypeEnum
from plugin.PixivAide.enums.pixiv_organize_mode_enum import PixivOrganizeModeEnum


class Scheduler(object):
    def __init__(self, context):
        self.context = context

    async def run_tasks(self, Crawler, collect_type, sleep_time):
        scoped_session = DbConnector(database=self.context.get("config.database")).ScopedSession
        while True:
            try:
                logger.info(f"初始化客户端")
                client = Client(self.context.get("config.cookies"))
                client.generate_client()
                crawler = Crawler(client=client, scoped_session=scoped_session)
                handle_metadata_task = asyncio.create_task(asyncio.to_thread(crawler.handle_metadata))
                execute_download_task = asyncio.create_task(asyncio.to_thread(crawler.execute_download_task, collect_type))
                await asyncio.gather(handle_metadata_task, execute_download_task)
                logger.info(f"进入休眠")
                await asyncio.sleep(sleep_time)
            except Exception as e:
                logger.warning(e)

    def scheduler_organize_illust_user(self):
        from common.constants.file_constant import FileConstant
        from plugin.PixivAide.modules.illust_manager import IllustManager
        LogManager("pixiv_aide_illust_organizer_user", level="INFO", log_path=None)
        scoped_session = DbConnector(database=self.context.get("config.database")).ScopedSession

        logger.info(f"初始化客户端")
        client = Client(self.context)
        client.generate_client()
        pattern = r'\[pid=(\d+)\]-p(\d+)'
        illust_manager = IllustManager(self.context, client, scoped_session)
        while True:
            collect_type = PixivCollectTypeEnum.PIXIV_COLLECT_TYPE_0.code
            illust_manager.organize_illust_file(FileConstant.USER_PATH,
                                                pattern,
                                                collect_type,
                                                replace_ind=True,
                                                rename_ind=True, modify_date_ind=True,
                                                organize_mode=PixivOrganizeModeEnum.PIXIV_ORGANIZE_MODE_0.code,
                                                unlink_ind=True)
            logger.warning(f"进入休眠")
            time.sleep(self.context.get("config.timer.organize_user"))

    def scheduler_organize_illust_daily(self):
        from common.constants.file_constant import FileConstant
        from plugin.PixivAide.modules.illust_manager import IllustManager
        LogManager("pixiv_aide_illust_organizer_daily", level="INFO", log_path=None)
        scoped_session = DbConnector(database=self.context.get("config.database")).ScopedSession

        logger.info(f"初始化客户端")
        client = Client(self.context)
        client.generate_client()
        pattern = r"(\d+)\s+-.*\[pid=(\d+)\]"
        illust_manager = IllustManager(self.context, client, scoped_session)
        while True:
            collect_type = PixivCollectTypeEnum.PIXIV_COLLECT_TYPE_2.code
            # 选择移动，会生成大量的作者目录
            # 选择移动且重命名，对于关注画师的作品，会删除日榜中的文件，适合去重的时候使用
            # 选择移动但不重命名，关注画师目录中会多出日榜文件
            # 一般不移动且不重命名，也不修改日期
            # 全量更新可删除源文件，也可以不删除
            # 增量更新时，一般删除源文件
            illust_manager.organize_illust_file(FileConstant.DAILY_PATH,
                                                pattern,
                                                collect_type,
                                                replace_ind=True,
                                                rename_ind=True, modify_date_ind=False,
                                                organize_mode=PixivOrganizeModeEnum.PIXIV_ORGANIZE_MODE_0.code,
                                                unlink_ind=True)
            logger.warning(f"进入休眠")
            time.sleep(self.context.get("config.timer.organize_daily"))

    def scheduler_user_crawler(self):
        from plugin.PixivAide.user_crawler import UserCrawler
        LogManager("pixiv_aide_user_crawler", level="INFO", log_path=None)
        asyncio.run(self.run_tasks(UserCrawler, PixivCollectTypeEnum.PIXIV_COLLECT_TYPE_0.code, 86400))

    def scheduler_daily_crawler(self):
        from plugin.PixivAide.daily_crawler import DailyCrawler
        LogManager("pixiv_aide_daily_crawler", level="INFO", log_path=None)
        asyncio.run(self.run_tasks(DailyCrawler, PixivCollectTypeEnum.PIXIV_COLLECT_TYPE_2.code, 86400))


    def run(self, scoped_session):
        logger.success(f"==========PixivAide==========")

        if self.context.get("config.switch.pixiv_organize_user"):
            logger.info(f"开始整理画师目录中的文件。")
            pixiv_illust_organizer_user = Process(target=self.scheduler_organize_illust_user)
            pixiv_illust_organizer_user.start()
            pixiv_illust_organizer_user.join()
            logger.info(f"整理画师目录完成。")

        if self.context.get("config.switch.pixiv_organize_daily"):
            logger.info(f"开始整理日榜目录中的文件。")
            pixiv_illust_organizer_daily = Process(target=self.scheduler_organize_illust_daily)
            pixiv_illust_organizer_daily.start()
            pixiv_illust_organizer_daily.join()
            logger.info(f"整理日榜目录完成。")

        # 检查关注画师服务控制状态
        plt_svc_cd_cntl_po = PltSvcCdCntl(svc_cd=880000)
        result = plt_svc_cd_cntl_service.select_by_primary_key(scoped_session, plt_svc_cd_cntl_po)
        if PltSvcCdCntlEnum.STATE_1.state == result.svc_cd_stcd:
            logger.success(f"开始获取关注画师。")
            pixiv_user_crawler = Process(target=self.scheduler_user_crawler)
            pixiv_user_crawler.start()
            pixiv_user_crawler.join()

        # 查看日榜服务控制状态
        plt_svc_cd_cntl_po = PltSvcCdCntl(svc_cd=880002)
        result = plt_svc_cd_cntl_service.select_by_primary_key(scoped_session, plt_svc_cd_cntl_po)
        if PltSvcCdCntlEnum.STATE_1.state == result.svc_cd_stcd:
            logger.success(f"开始获取日榜插画。")
            pixiv_daily_crawler = Process(target=self.scheduler_daily_crawler)
            pixiv_daily_crawler.start()
            pixiv_daily_crawler.join()
