import json

from common.context.context import Context
from common.database.transaction import transaction
from common.thread.listener import Listener
from common.log.log_manager import logger
from dao.models.pixiv.pixiv_dwld_info_model import PixivDwldInfo
from dao.models.pixiv.pixiv_prim_model import PixivPrim
from dao.models.pixiv.pixiv_rank_model import PixivRank
from dao.service.pixiv import pixiv_prim_service, pixiv_dwld_info_service, pixiv_rank_service
from plugin.PixivAide.enums.pixiv_download_status_enum import PixivDownloadStatusEnum
from plugin.PixivAide.enums.pixiv_rank_type_enum import PixivRankTypeEnum
from plugin.PixivAide.mapper.collect_type_to_rank_type_mapper import CollectToRankMapper
from plugin.PixivAide.modules.extractor import Extractor


class PixivDwldListener(Listener):
    @transaction
    def before_action(self, scoped_session, context):
        try:
            illust_metadata = json.loads(context.get("pixiv.download_task.pixiv_dwld_info_po").illust_metadata,
                                         object_hook=Context)
            lock_ind = context.get("pixiv.download_task.lock_ind", "锁为空")

            pixiv_dwld_info_po = PixivDwldInfo(pid=illust_metadata.get("pid"),
                                               sn=illust_metadata.get("sn"),
                                               user_id=illust_metadata.get("user_id"),
                                               download_status=PixivDownloadStatusEnum.PIXIV_DOWNLOAD_STATUS_0.code,
                                               lock_ind=lock_ind)
            result = pixiv_dwld_info_service.lock_download_task(scoped_session, pixiv_dwld_info_po)
            if result.rowcount != 1:
                raise Exception(f"加锁失败！")
            logger.success("加锁成功，开始下载。")
        except Exception as e:
            logger.error(f"加锁失败：{e}")
            raise

    @transaction
    def after_action(self, scoped_session, context, status, msg):
        download_status = None
        download_date = context.get("pixiv.download_task.download_date")

        illust_metadata = json.loads(context.get("pixiv.download_task.pixiv_dwld_info_po").illust_metadata,
                                     object_hook=Context)
        illust_metadata.set("download_date", download_date)
        illust_metadata.set("exist_ind", True)
        lock_ind = context.get("pixiv.download_task.lock_ind", "锁为空")

        try:
            if status:
                logger.success("下载成功！")
                pixiv_prim_po = PixivPrim.generate_pixiv_prim_po(illust_metadata)
                # 新增主表信息
                pixiv_prim_service.check_pixiv_prim(scoped_session, pixiv_prim_po)
                # 处理标签
                Extractor.handel_tags(scoped_session, illust_metadata)
                download_status = PixivDownloadStatusEnum.PIXIV_DOWNLOAD_STATUS_1.code

                # 更新排行表
                collect_type = illust_metadata.get("collect_type")
                if collect_type in CollectToRankMapper.collect_to_rank:
                    rank_date = illust_metadata.get("rank_date", "入榜日期不存在，请检查。")
                    rank_position = illust_metadata.get("rank_position", "上榜名次不存在，请检查。")
                    try:
                        rank_type = CollectToRankMapper.get_rank_type(collect_type)
                        logger.info(f"榜单类型：{PixivRankTypeEnum.get_msg_by_code(rank_type)}")
                        pixiv_rank_po = PixivRank(pid=illust_metadata.get("pid"),
                                                  sn=illust_metadata.get("sn"),
                                                  user_id=illust_metadata.get("user_id"),
                                                  rank_type=rank_type,
                                                  rank_date=rank_date,
                                                  rank_position=rank_position)
                        pixiv_rank_service.check_pixiv_rank(scoped_session, pixiv_rank_po)
                    except Exception as e:
                        logger.error(f"更新排行表出错：{e}")
                        raise
            else:
                logger.error(f"下载失败：{msg}")
                download_status = PixivDownloadStatusEnum.PIXIV_DOWNLOAD_STATUS_2.code
        except Exception as e:
            download_status = PixivDownloadStatusEnum.PIXIV_DOWNLOAD_STATUS_2.code
            logger.error(e)
            raise
        finally:
            try:
                pixiv_dwld_info_po = PixivDwldInfo(pid=illust_metadata.get("pid"),
                                                   sn=illust_metadata.get("sn"),
                                                   user_id=illust_metadata.get("user_id"),
                                                   collect_type=illust_metadata.get("collect_type"),
                                                   download_status=download_status if download_status is not None else PixivDownloadStatusEnum.PIXIV_DOWNLOAD_STATUS_2.code,
                                                   download_date=download_date,
                                                   lock_ind=lock_ind)
                pixiv_dwld_info_service.update_by_primary_key_selective(scoped_session, pixiv_dwld_info_po)

                result = pixiv_dwld_info_service.unlock_download_task(scoped_session, pixiv_dwld_info_po)
                if result.rowcount != 1:
                    raise Exception(f"解锁失败！")
                logger.success("下载任务结束，解锁。")
            except Exception as e:
                logger.error(f"解锁失败：{e}")
                raise
