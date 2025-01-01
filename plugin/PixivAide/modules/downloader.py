import copy
import os
import json
import re
import datetime
from functools import partial

import imageio
import zipfile
import urllib3

from common.context.context import Context, path_converter
from common.database.transaction import transaction
from common.file.file_manager import FileManager
from common.log.log_manager import logger
from plugin.PixivAide.constants.pixiv_constant import PixivConstant
from dao.models.pixiv.pixiv_dwld_info_model import PixivDwldInfo
from dao.models.pixiv.pixiv_user_model import PixivUser
from dao.service.pixiv import pixiv_user_service, pixiv_dwld_info_service
from plugin.PixivAide.enums.pixiv_collect_type_enum import PixivCollectTypeEnum
from plugin.PixivAide.enums.pixiv_download_status_enum import PixivDownloadStatusEnum
from plugin.PixivAide.enums.pixiv_illust_resp_enum import PixivIllustRespEnum
from plugin.PixivAide.enums.pixiv_modify_file_date_ind import PixivModifyFileDateIndEnum
from plugin.PixivAide.modules.extractor import Extractor
from common.utils.timer import Timer

# 强制取消警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Downloader:
    """
    :功能描述: 下载信息入表、下载图片
    :Author: Lancelot
    :Date: 2024/12/15 22:48
    """

    def __init__(self, client, scoped_session):
        self.class_name = self.__class__.__name__
        self.client = client
        self.scoped_session = scoped_session
        self.file_manager = FileManager()
        self.extractor = Extractor(client)
        self.ugoira_url = PixivConstant.UGOIRA_URL
        self.multi_url = PixivConstant.MULTI_URL

    def handle_download_metadata(self, context):
        """
        :功能描述: 获取元数据并入下载表
        :param context: 变量池
        :return: 无
        :Author: Lancelot
        :Date: 2024/12/15 22:47
        """
        pid = context.get("pixiv.metadata_task.pid")
        rank_date = context.get("pixiv.metadata_task.rank_date")
        rank_position = context.get("pixiv.metadata_task.rank_position")
        collect_type = context.get("pixiv.metadata_task.collect_type")

        try:
            illust_metadata = Timer(120).retry(partial(self.extractor.get_illust_metadata,
                                                       pid,
                                                       collect_type,
                                                       rank_date,
                                                       rank_position))
        except Exception as e:
            logger.warning(f"获取{pid}元数据出错：{e}")
            raise Exception(f"获取{pid}元数据出错：{e}")

        try:
            self.save_dwld_info(self.scoped_session, illust_metadata)
        except Exception as e:
            logger.warning(f"下载数据入表{pid}出错：{e}")
            raise Exception(f"下载数据入表{pid}出错：{e}")

    @staticmethod
    def insert_or_update_dwld_info(scoped_session, illust_metadata):
        """
        :功能描述: 插入或更新下载表
        :param scoped_session: 会话
        :param illust_metadata: 作品元数据
        :return: 无
        :Author: Lancelot
        :Date: 2024/12/15 22:46
        """
        pixiv_dwld_info_po = PixivDwldInfo(pid=illust_metadata.get("pid"),
                                           sn=illust_metadata.get("sn"),
                                           title=illust_metadata.get("title"),
                                           user_id=illust_metadata.get("user_id"),
                                           user_name=illust_metadata.get("user_name"),
                                           collect_type=illust_metadata.get("collect_type"),
                                           artwork_url=illust_metadata.get("artwork_url"),
                                           original_url=illust_metadata.get("original_url"),
                                           page_count=illust_metadata.get("page_count"),
                                           illust_type=illust_metadata.get("illust_type"),
                                           zip_info_url=illust_metadata.get("zip_info_url"),
                                           zip_path=illust_metadata.get("zip_path"),
                                           frames_path=illust_metadata.get("frames_path"),
                                           full_path=illust_metadata.get("full_path"),
                                           create_date=illust_metadata.get("create_date"),
                                           download_status=PixivDownloadStatusEnum.PIXIV_DOWNLOAD_STATUS_0.code,
                                           illust_metadata=json.dumps(illust_metadata, default=path_converter, ensure_ascii=False))

        result = pixiv_dwld_info_service.select_by_primary_key(scoped_session, pixiv_dwld_info_po)
        if not result:
            # 不存在该图下载记录
            pixiv_dwld_info_service.insert(scoped_session, pixiv_dwld_info_po)
            logger.success(f"新增下载信息成功：{illust_metadata.get("pid")}_{illust_metadata.get_def("sn", 0)}。")
        elif result.download_status != PixivDownloadStatusEnum.PIXIV_DOWNLOAD_STATUS_1.code and result.lock_ind is None:
            # 图片未下载成功且未上锁（下载中），更新
            pixiv_dwld_info_service.update_by_primary_key_selective(scoped_session, pixiv_dwld_info_po)
            logger.success(f"更新下载信息成功：{illust_metadata.get("pid")}_{illust_metadata.get_def("sn", 0)}。")

    @staticmethod
    def complete_metadata_path_single(illust_metadata, save_path, rank_position=None):
        """
        :功能描述: 完善单图下载数据
        :param illust_metadata: 作品元数据
        :param save_path: 保存路径
        :param rank_position: 榜单位次
        :return illust_metadata: 完善后的元数据
        :Author: Lancelot
        :Date: 2024/12/15 22:47
        """
        pid = illust_metadata.get("pid")
        sn = illust_metadata.get("sn")
        title = illust_metadata.get("title")
        user_name = illust_metadata.get("user_name")
        original_url = illust_metadata.get("original_url")

        # 图片保存地址
        if rank_position:
            file_name = f"{rank_position} - {title} - {user_name} - [pid={pid}_p{sn}].{original_url.split(".")[-1]}"
        else:
            file_name = f"{title} - {user_name} - [pid={pid}_p{sn}].{original_url.split(".")[-1]}"
        safe_file_name = re.sub(r'[/:*?"<>|]', '_', file_name)
        full_path = os.path.join(save_path, safe_file_name)
        illust_metadata.set("full_path", full_path)

        return illust_metadata

    def complete_metadata_path_gif(self, illust_metadata, save_path, rank_position=None):
        """
        :功能描述: 完善动图下载数据
        :param illust_metadata: 作品元数据
        :param save_path: 保存路径
        :param rank_position: 榜单位次
        :return illust_metadata: 完善后的元数据
        :Author: Lancelot
        :Date: 2024/12/15 22:47
        """
        pid = illust_metadata.get("pid")
        sn = illust_metadata.get("sn")
        title = illust_metadata.get("title")
        user_name = illust_metadata.get("user_name")

        # 动图zip信息链接
        zip_info_url = self.ugoira_url.format(pid)
        illust_metadata.set("zip_info_url", zip_info_url)
        # 动图zip保存地址
        if rank_position:
            zip_name = f"{rank_position} - {title} - {user_name} - [pid={pid}_p{sn}].zip"
        else:
            zip_name = f"{title} - {user_name} - [pid={pid}_p{sn}].zip"
        safe_zip_name = re.sub(r'[/:*?"<>|]', '_', zip_name)
        zip_path = os.path.join(save_path, safe_zip_name)
        illust_metadata.set("zip_path", zip_path)
        # 动图zip解压地址
        if rank_position:
            frames_name = f"{rank_position} - {title} - {user_name} - [pid={pid}_p{sn}]"
        else:
            frames_name = f"{title} - {user_name} - [pid={pid}_p{sn}]"
        safe_frames_name = re.sub(r'[/:*?"<>|]', '_', frames_name)
        frames_path = os.path.join(save_path, safe_frames_name)
        illust_metadata.set("frames_path", frames_path)
        # 存储GIF的文件路径
        if rank_position:
            file_name = f"{rank_position} - {title} - {user_name} - [pid={pid}_p{sn}].gif"
        else:
            file_name = f"{title} - {user_name} - [pid={pid}_p{sn}].gif"
        safe_file_name = re.sub(r'[/:*?"<>|]', '_', file_name)
        full_path = os.path.join(save_path, safe_file_name)
        illust_metadata.set("full_path", full_path)

        return illust_metadata

    def complete_metadata_path_multi(self, illust_metadata, save_path, rank_position=None):
        """
        :功能描述: 完善多图下载数据
        :param illust_metadata: 作品元数据
        :param save_path: 保存路径
        :param rank_position: 榜单位次
        :return illust_metadata_list: 完善后的元数据
        :Author: Lancelot
        :Date: 2024/12/15 22:47
        """
        illust_metadata_list = []
        pid = illust_metadata.get("pid")
        title = illust_metadata.get("title")
        user_name = illust_metadata.get("user_name")

        multi_resp = self.client.base_request(options={"url": self.multi_url.format(pid)})
        if multi_resp is None:
            logger.error(f"下载元数据失败：{pid}-{title}")
            raise Exception(f"下载元数据失败：{pid}-{title}")
        multi_json = json.loads(multi_resp.text, object_hook=Context)
        if multi_json.get("error") is True or multi_json.get("body") == []:
            logger.error(f"该作品{pid}已被删除,或作品ID不存在,或被限制访问。")
            raise Exception(f"该作品{pid}已被删除,或作品ID不存在,或被限制访问。")

        for illust in multi_json.get("body"):
            # 创建新的illust_metadata对象，基于原始对象深拷贝
            new_illust_metadata = copy.deepcopy(illust_metadata)
            # 获取下载路径
            original_url = illust.get("urls.original")
            new_illust_metadata.set("original_url", original_url)
            # 生成序号
            sn = re.search(r'/([^/]+_p(\d+))\.\w+$', original_url).group(2)
            new_illust_metadata.set("sn", int(sn))
            if rank_position:
                file_name = f"{rank_position} - {title} - {user_name} - [pid={pid}_p{sn}].{original_url.split(".")[-1]}"
            else:
                file_name = f"{title} - {user_name} - [pid={pid}_p{sn}].{original_url.split(".")[-1]}"
            safe_file_name = re.sub(r'[/:*?"<>|]', '_', file_name)
            full_path = os.path.join(save_path, safe_file_name)
            new_illust_metadata.set("full_path", full_path)
            illust_metadata_list.append(new_illust_metadata)

        return illust_metadata_list

    @transaction
    def save_dwld_info(self, scoped_session, illust_metadata):
        """
        :功能描述: 根据pageCount和illustType判定作品id类型，下载作品数据并入表
        :param scoped_session: 会话
        :param illust_metadata: 作品元数据
        :return: 无
        :Author: Lancelot
        :Date: 2024/12/15 22:47
        ==================以下为判定规则==================
                      单图  多图  动图  漫画单图  漫画多图
            pageCount  1	 n 	  1      1       n
            illustType 0	 0 	  2      1	     1
        ================================================
        """
        try:
            pid = illust_metadata.get("pid")
            title = illust_metadata.get("title")
            user_id = illust_metadata.get("user_id")
            user_name = illust_metadata.get("user_name")
            user_path = self.file_manager.check_user_path_without_mkidr(user_id, user_name)

            collect_type = illust_metadata.get("collect_type")
            if collect_type == PixivCollectTypeEnum.PIXIV_COLLECT_TYPE_2.code:
                rank_date = illust_metadata.get("rank_date", "上榜日期为空，请检查。")
                save_path = self.file_manager.check_daily_path_without_mkidr(rank_date)
            elif collect_type == PixivCollectTypeEnum.PIXIV_COLLECT_TYPE_8.code:
                # 手动下载作品
                save_path = self.file_manager.check_download_path_without_mkidr()
            else:
                save_path = user_path

            logger.info(f"开始下载任务入表:{pid} - {title} - {user_name}")
            page_count = illust_metadata.get("page_count")
            illust_type = illust_metadata.get("illust_type")

            # 检查画师表
            pixiv_user_context = Context()
            pixiv_user_context.set("user_id", user_id)
            pixiv_user_context.set("user_name", user_name)
            pixiv_user_context.set("user_name", user_name)
            pixiv_user_po = PixivUser.generate_pixiv_user_po(pixiv_user_context)
            pixiv_user_service.check_pixiv_user(scoped_session, pixiv_user_po)
            # 手动刷新
            scoped_session.flush()

            # 存入下载表：PIXIV_DWLD_INFO
            if page_count == 1:
                if illust_type == 2:
                    logger.info(f"动图下载任务入表:{pid} - {title} - {user_name}")
                    illust_metadata.set("sn", 0)
                    illust_metadata = self.complete_metadata_path_gif(illust_metadata, save_path,
                                                                      illust_metadata.get("rank_position"))
                    self.insert_or_update_dwld_info(scoped_session, illust_metadata)
                else:
                    logger.info(f"单图下载任务入表:{pid} - {title} - {user_name}")
                    illust_metadata.set("sn", 0)
                    illust_metadata = self.complete_metadata_path_single(illust_metadata, save_path,
                                                                         illust_metadata.get("rank_position"))
                    self.insert_or_update_dwld_info(scoped_session, illust_metadata)
            else:
                logger.info(f"多图下载任务入表:{pid} - {title} - {user_name}")
                illust_metadata_list = self.complete_metadata_path_multi(illust_metadata, save_path,
                                                                         illust_metadata.get("rank_position"))
                for illust_metadata in illust_metadata_list:
                    self.insert_or_update_dwld_info(scoped_session, illust_metadata)
        except Exception as e:
            logger.warning(f"下载数据入表出错：{e}")
            raise Exception(f"下载数据入表出错：{e}")

    def download_illust_single(self, context):
        """
        :功能描述: 下载单图
        :param context: 变量池
        :return: 无
        :Author: Lancelot
        :Date: 2024/12/15 22:47
        """
        pixiv_dwld_info_po = context.get("pixiv.download_task.pixiv_dwld_info_po")
        illust_metadata = json.loads(pixiv_dwld_info_po.illust_metadata, object_pairs_hook=Context)
        title = illust_metadata.get("title")
        original_url = illust_metadata.get("original_url")
        full_path = illust_metadata.get("full_path")
        if os.path.exists(full_path) and os.path.getsize(full_path) > 1000:
            logger.info(f"作品已存在：{full_path}")
            # 不更新download_date
        else:
            logger.info(f"获取下载数据：{original_url}")
            response = self.client.base_request(options={"url": original_url})
            if response is None:
                raise Exception(PixivIllustRespEnum.PIXIV_ILLUST_RESP_5.msg)
            logger.info(f"获取图片数据成功，开始写入：{full_path}")
            size = self.file_manager.write_content(full_path, response.content)
            # 修改时间
            logger.success(f"作品下载成功! 标题：{title}，大小:{size}")
            context.set("pixiv.download_task.download_date", datetime.datetime.now())

    def download_illust_gif(self, context):
        """
        :功能描述: 下载动图
        :param context: 变量池
        :return: 无
        :Author: Lancelot
        :Date: 2024/12/15 22:47
        """
        pixiv_dwld_info_po = context.get("pixiv.download_task.pixiv_dwld_info_po")
        illust_metadata = json.loads(pixiv_dwld_info_po.illust_metadata, object_pairs_hook=Context)
        title = illust_metadata.get("title")
        zip_info_url = illust_metadata.get("zip_info_url")
        zip_path = illust_metadata.get("zip_path")
        frames_path = illust_metadata.get("frames_path")
        full_path = illust_metadata.get("full_path")

        if os.path.exists(full_path) and os.path.getsize(full_path) > 1000:
            logger.info(f"作品已存在：{full_path}")
            # 不更新download_date
        else:
            zip_info = self.client.base_request(options={"url": zip_info_url})
            if zip_info is None:
                raise PixivIllustRespEnum.PIXIV_ILLUST_RESP_5.msg
            zip_json = json.loads(zip_info.text, object_hook=Context)
            zip_url = zip_json.get("body.originalSrc")
            # item["delay"]为对应图片停留间隔,单位毫秒
            delay = [item["delay"] / 1000 for item in zip_json.get("body.frames")]
            # 下载zip
            zip_resp = self.client.base_request(options={"url": zip_url})
            if zip_resp is None:
                raise PixivIllustRespEnum.PIXIV_ILLUST_RESP_5.msg
            with open(zip_path, "ab") as f1:
                f1.write(zip_resp.content)
            # 解压zip
            with zipfile.ZipFile(zip_path, "r") as f2:
                for file in f2.namelist():
                    f2.extract(file, frames_path)
            # 删除zip
            os.remove(zip_path)
            # 扫描解压出来的图片
            files = [os.path.join(frames_path, i) for i in os.listdir(frames_path)]
            # 添加图片到待合成列表
            frames = []
            for i in range(1, len(files)):
                frames.append(imageio.v2.imread(files[i]))
            # 合成gif
            imageio.mimsave(full_path, frames, duration=delay)
            # 下载成功
            size = os.path.getsize(full_path)
            logger.success(f"作品下载成功! 标题：{title}，大小:{size}")
            # 删除解压出来的图片
            for j in files:
                os.remove(os.path.join(frames_path, j))
            context.set("pixiv.download_task.download_date", datetime.datetime.now())

    def download_illust(self, context):
        """
        :功能描述: 根据pageCount和illustType判定作品id类型，下载作品数据
        :param context: 变量池
        :return: illust_metadata
        :Author: Lancelot
        :Date: 2024/12/15 22:47
        ==================以下为判定规则=================
                      单图  多图  动图  漫画单图  漫画多图
            pageCount  1	 n 	  1      1       n
            illustType 0	 0 	  2      1	     1
        ===============================================
        """
        try:
            pixiv_dwld_info_po = context.get("pixiv.download_task.pixiv_dwld_info_po")
            modify_file_date_ind = context.get("pixiv.download_task.modify_file_date_ind")
            pid = pixiv_dwld_info_po.pid
            title = pixiv_dwld_info_po.title
            user_name = pixiv_dwld_info_po.user_name
            illust_type = pixiv_dwld_info_po.illust_type
            modify_file_date_ind = modify_file_date_ind if modify_file_date_ind else PixivModifyFileDateIndEnum.PIXIV_MODIFY_FILE_DATE_IND_0.code

            if illust_type != 2:
                logger.info(f"开始单图下载:{pid} - {title} - {user_name}")
                self.download_illust_single(context)
            else:
                logger.info(f"开始动图下载:{pid} - {title} - {user_name}")
                self.download_illust_gif(context)

            if PixivModifyFileDateIndEnum.PIXIV_MODIFY_FILE_DATE_IND_1.code == modify_file_date_ind:
                illust_metadata = json.loads(pixiv_dwld_info_po.illust_metadata, object_pairs_hook=Context)
                create_date = illust_metadata.get("create_date")
                full_path = illust_metadata.get("full_path")
                self.file_manager.modify_file_date(full_path, create_date)
                logger.info(f"开始修改作品时间成功:{pid} - {title} - {user_name}")

        except Exception as e:
            logger.warning(f"下载出错：{e}")
            raise Exception(f"下载出错：{e}")
