import datetime
import re
import shutil
from pathlib import Path

from common.context.context import Context
from common.file.file_manager import FileManager
from common.thread.thread_pool import ThreadPool
from plugin.PixivAide.constants.pixiv_constant import PixivConstant
from dao.models.pixiv.pixiv_prim_model import PixivPrim
from dao.models.pixiv.pixiv_rank_model import PixivRank
from dao.models.pixiv.pixiv_user_model import PixivUser
from dao.service.pixiv import pixiv_prim_service, pixiv_user_service, pixiv_rank_service
from plugin.PixivAide.modules.downloader import Downloader
from plugin.PixivAide.enums.pixiv_collect_type_enum import PixivCollectTypeEnum
from plugin.PixivAide.enums.pixiv_organize_mode_enum import PixivOrganizeModeEnum
from plugin.PixivAide.enums.pixiv_rank_type_enum import PixivRankTypeEnum
from plugin.PixivAide.modules.extractor import Extractor
from common.log.log_manager import logger
from plugin.PixivAide.mapper.collect_type_to_rank_type_mapper import CollectToRankMapper


class IllustManager(object):

    def __init__(self, context, client, scoped_session):
        self.class_name = self.__class__.__name__
        self.context = context
        self.client = client
        self.scoped_session = scoped_session
        self.file_manager = FileManager()
        self.downloader = Downloader(client, scoped_session)
        self.extractor = Extractor(client)
        self.thread_pool = ThreadPool(scoped_session, 1, 1)
        self.multi_url = PixivConstant.MULTI_URL

    @staticmethod
    def complete_metadata_method(file, new_parent_path, replace_ind: bool):
        def complete_metadata(illust_metadata, method):
            current_full_path = Path(file).resolve()
            current_parent_path = file.parent
            if not replace_ind:
                logger.info(f"不需要移动文件:{current_full_path}。")
                illust_metadata_result = method(illust_metadata, save_path=current_parent_path)
            else:
                logger.info(f"需要移动文件:{current_full_path}到目录：{new_parent_path}")
                illust_metadata_result = method(illust_metadata, save_path=new_parent_path)
            return illust_metadata_result

        return complete_metadata

    @staticmethod
    def process_illust_metadata_full_path(illust_metadata, current_full_path, new_parent_path, replace_ind: bool,
                                          rename_ind: bool):
        if not replace_ind:
            if not rename_ind:
                logger.info(f"不移动且不重命名：{current_full_path}")
                illust_metadata.set("full_path", current_full_path)
            else:
                logger.info(f"不移动且重命名：{illust_metadata.get("full_path")}")
                pass
        else:
            if not rename_ind:
                logger.info(f"移动且不重命名：{current_full_path}。")
                new_full_path = Path(new_parent_path) / Path(current_full_path).name
                logger.info(f"需要移动到{new_full_path}。")
                illust_metadata.set("full_path", new_full_path)
            else:
                logger.info(f"移动且重命名：{illust_metadata.get("full_path")}。")

    @staticmethod
    def process_rename_replace(file, illust_metadata, unlink_ind: bool):
        current_full_path = Path(file).resolve()
        logger.info(f"开始移动文件:{current_full_path}。")
        full_path = Path(illust_metadata.get("full_path"))
        logger.info(f"目标文件:{full_path}。")
        if full_path == current_full_path:
            logger.info(f"源文件不移动且不重命名：:{full_path}")
        else:
            if full_path.exists():
                logger.info(f"目标目录中已存在同名文件：{full_path}")
                if unlink_ind:
                    logger.info(f"删除源文件：{current_full_path}")
                    file.unlink()
                else:
                    logger.info(f"保留源文件：{current_full_path}")
            else:
                logger.info(f"移动文件到目标目录:{full_path}")
                full_path.parent.mkdir(parents=True, exist_ok=True)
                if unlink_ind:
                    logger.info(f"删除源文件：{current_full_path}")
                    file.rename(full_path)
                else:
                    logger.info(f"保留源文件：{current_full_path}")
                    shutil.copy2(current_full_path, full_path)
        logger.success(f"移动并重命名处理成功:\n"
                       f"源文件：{current_full_path}\n"
                       f"目标文件{full_path}。")

    def process_file_date(self, illust_metadata, modify_date_ind: bool):
        full_path = illust_metadata.get("full_path")
        if not modify_date_ind:
            logger.info(f"不修改时间:{full_path}")
            pass
        else:
            create_date = illust_metadata.get("create_date")
            logger.info(f"修改时间:{full_path}-{create_date}")
            self.file_manager.modify_file_date(full_path, create_date)

    @staticmethod
    def match_filename_method_user(match):
        pid = match.group(1)
        sn = match.group(2)
        return pid, sn

    @staticmethod
    def match_filename_method_daily(match):
        rank_position = match.group(1)
        pid = match.group(2)
        sn = 0
        return pid, sn, rank_position

    def organize_illust_file(self, path, pattern, collect_type, replace_ind: bool, rename_ind: bool,
                             modify_date_ind: bool, organize_mode, unlink_ind: bool):
        abs_path = self.file_manager.generate_abs_file_path(path)
        logger.info(f"开始整理文件夹: {abs_path}。")
        logger.info(f"模式为: {pattern}。")
        # 递归遍历所有子文件夹中的文件
        for file in abs_path.rglob('*'):
            logger.info(f"开始匹配: {file.name}。")
            if file.is_file():
                # 匹配文件名
                match = re.search(pattern, file.name)
                if match:
                    if PixivCollectTypeEnum.PIXIV_COLLECT_TYPE_0.code == collect_type:
                        pid, sn = self.match_filename_method_user(match)
                    elif PixivCollectTypeEnum.PIXIV_COLLECT_TYPE_1.code == collect_type:
                        pid, sn = self.match_filename_method_user(match)
                    else:
                        pid, sn, rank_position = self.match_filename_method_daily(match)
                        self.context.set("pixiv.organize_illust_file.rank_position", rank_position)

                    current_full_path = Path(file).resolve()
                    logger.success(f"匹配成功! {current_full_path}")
                    pixiv_prim_po = PixivPrim(pid=pid,
                                              sn=sn,
                                              collect_type=collect_type)
                    result = pixiv_prim_service.select_by_pid_sn_collect_type(self.scoped_session, pixiv_prim_po)
                    if not result or PixivOrganizeModeEnum.PIXIV_ORGANIZE_MODE_0.code == organize_mode:
                        logger.info(f"主表无记录或需要全量更新。 pid: {pid}, sn: {sn}")
                        try:
                            illust_metadata = self.extractor.get_illust_metadata(pid, collect_type)
                            try:
                                pid = illust_metadata.get("pid")
                                title = illust_metadata.get("title")
                                page_count = illust_metadata.get("page_count")
                                illust_type = illust_metadata.get("illust_type")
                                user_id = illust_metadata.get("user_id")
                                user_name = illust_metadata.get("user_name")
                                user_path = self.file_manager.check_user_path_without_mkidr(user_id, user_name)
                                complete_metadata_method = self.complete_metadata_method(file,
                                                                                         user_path,
                                                                                         replace_ind)
                                self.context.set("pixiv.organize_illust_file.user_id", user_id)

                                pixiv_user_context = Context()
                                pixiv_user_context.set("user_id", user_id)
                                pixiv_user_context.set("user_name", user_name)
                                pixiv_user_context.set("user_name", user_name)
                                pixiv_user_po = PixivUser.generate_pixiv_user_po(pixiv_user_context)
                                pixiv_user_service.check_pixiv_user(self.scoped_session, pixiv_user_po)

                                if page_count == 1:
                                    if illust_type == 2:
                                        logger.info(f"开始获取动图完整元数据:{pid} - {title} - {user_name}")
                                        illust_metadata.set("sn", 0)
                                        illust_metadata = complete_metadata_method(illust_metadata,
                                                                                   self.downloader.complete_metadata_path_gif)
                                    else:
                                        logger.info(f"获取单图完整元数据:{pid} - {title} - {user_name}")
                                        illust_metadata.set("sn", 0)
                                        illust_metadata = complete_metadata_method(illust_metadata,
                                                                                   self.downloader.complete_metadata_path_single)
                                    self.process_illust_metadata_full_path(illust_metadata,
                                                                           current_full_path,
                                                                           user_path,
                                                                           replace_ind,
                                                                           rename_ind)
                                    self.process_rename_replace(file, illust_metadata, unlink_ind)
                                    self.process_file_date(illust_metadata, modify_date_ind)
                                    logger.success(f"获取动图/单图完整元数据成功:{pid} - {title} - {user_name}")
                                    illust_metadata.set("exist_ind", True)
                                    pixiv_prim_po = PixivPrim.generate_pixiv_prim_po(illust_metadata)
                                    pixiv_prim_service.check_pixiv_prim(self.scoped_session, pixiv_prim_po)
                                    self.context.set("pixiv.organize_illust_file.full_path",
                                                     illust_metadata.get("full_path"))
                                    logger.success(f"新增（或更新）动图（或单图）作品主信息成功！")
                                else:
                                    logger.info(f"获取多图完整元数据:{pid} - {title} - {user_name}")
                                    illust_metadata_list = complete_metadata_method(illust_metadata,
                                                                                    self.downloader.complete_metadata_path_multi)
                                    for illust_metadata in illust_metadata_list:
                                        if illust_metadata.get("sn") == sn:
                                            self.process_illust_metadata_full_path(illust_metadata,
                                                                                   current_full_path,
                                                                                   user_path,
                                                                                   replace_ind,
                                                                                   rename_ind)
                                            self.process_rename_replace(file, illust_metadata, unlink_ind)
                                            self.process_file_date(illust_metadata, modify_date_ind)
                                            illust_metadata.set("exist_ind", True)
                                            pixiv_prim_po = PixivPrim.generate_pixiv_prim_po(illust_metadata)
                                            pixiv_prim_service.check_pixiv_prim(self.scoped_session, pixiv_prim_po)
                                            self.context.set("pixiv.organize_illust_file.full_path",
                                                             illust_metadata.get("full_path"))
                                            logger.success(f"新增（或更新）多图作品主信息成功！")

                            except Exception as e:
                                logger.error(f"获取{pid}完整元数据出错：{e}")
                                return
                                # raise f"获取{pid}完整元数据出错：{e}"
                        except Exception as e:
                            logger.error(f"新增{pid}完整元数据出错！：{e}")
                            return
                            # raise f"新增{pid}完整元数据出错：{e}"
                    else:
                        logger.info(f"主表有记录且为增量更新：{pid}-{sn}")
                        if unlink_ind:
                            logger.info(f"删除源文件：{current_full_path}")
                            file.unlink()
                        else:
                            logger.info(f"不删除源文件：{current_full_path}")
                        self.context.set("pixiv.organize_illust_file.user_id", pixiv_prim_po.user_id)
                        self.context.set("pixiv.organize_illust_file.full_path", pixiv_prim_po.full_path)

                    if collect_type in CollectToRankMapper.collect_to_rank:
                        try:
                            rank_type = CollectToRankMapper.get_rank_type(collect_type)
                            logger.info(f"整理榜单作品，检查排行表。")
                            logger.info(f"榜单类型：{PixivRankTypeEnum.get_msg_by_code(rank_type)}")

                            user_id = self.context.get("pixiv.organize_illust_file.user_id")
                            rank_position = self.context.get("pixiv.organize_illust_file.rank_position")
                            full_path = self.context.get("pixiv.organize_illust_file.full_path")

                            pixiv_rank_context = Context()
                            pixiv_rank_context.set("pid", pid)
                            pixiv_rank_context.set("sn", sn)
                            pixiv_rank_context.set("user_id", user_id)
                            pixiv_rank_context.set("rank_type", rank_type)
                            pixiv_rank_context.set("rank_date", datetime.datetime.fromtimestamp(Path(full_path).stat().st_ctime))
                            pixiv_rank_context.set("rank_position", rank_position)
                            pixiv_rank_po = PixivRank.generate_pixiv_rank_po(pixiv_rank_context)
                            pixiv_rank_service.check_pixiv_rank(self.scoped_session, pixiv_rank_po)
                        except Exception as e:
                            logger.error(f"整理榜单作品出错！：{e}")

        logger.success(f"处理成功！")
