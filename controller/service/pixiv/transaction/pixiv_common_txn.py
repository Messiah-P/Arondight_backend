import asyncio
import copy
import json

from plugin.PixivAide.modules.client import Client
from dao.models.pixiv.pixiv_prim_model import PixivPrim
from dao.service.pixiv import pixiv_prim_service
from plugin.PixivAide.enums.pixiv_collect_type_enum import PixivCollectTypeEnum
from plugin.PixivAide.enums.pixiv_modify_file_date_ind import PixivModifyFileDateIndEnum
from common.context.context import Context, CustomJSONEncoder
from dao.models.plt.tech_parm_model import TechParm
from dao.service.plt import tech_parm_service
from common.utils.plt_utils import generate_unique_8digit
from common.thread.thread_pool import ThreadPool
from service.pixiv.crawler import Crawler
from common.log.log_manager import logger


async def set_pixiv_cookie(initializer, entity):
    """
    * 功能描述: 设置Cookie
    :param initializer: 初始化器
    :param entity: 请求体
    * @fileName: pixiv_common_txn.py
    * @Author: Lancelot
    * @Date: 2024/12/31 9:48
    """
    try:
        # 获取cookies参数
        tech_parm_context = Context()
        tech_parm_context.set("id", 1)
        tech_parm_context.set("parm_cd", "cookies")
        tech_parm_context.set("parm_sn", 0)
        tech_parm_po = TechParm.generate_tech_parm_po(tech_parm_context)
        cookies = tech_parm_service.get_cookies(initializer.scoped_session, tech_parm_po)
        initializer.context.set("config.cookies", cookies)
        return "000", "交易成功", initializer.context.get("config.cookies")
    except Exception as e:
        return "022", f"{e}", None


async def get_prim_inf_by_pid(initializer, entity):
    """
    :功能描述: 根据pid查询主表
    :param initializer: 初始化器
    :param entity: 请求体
    :return: 主表结果
    :Author: Lancelot
    :Date: 2024/12/15 23:37
    """
    try:
        pid = entity.get("arondight.req.entity.pid", "pid为空")
        pixiv_prim_po = PixivPrim(pid=pid)
        result_list = pixiv_prim_service.select_by_pid(initializer.scoped_session, pixiv_prim_po)

        pixiv_prim_po_list = [PixivPrim(**row) for row in result_list.mappings()]
        if pixiv_prim_po_list:
            artwork_url = pixiv_prim_po_list[0].artwork_url
            resp_entity = [pixiv_prim_po.to_dict() for pixiv_prim_po in pixiv_prim_po_list]

            initializer.notifier.notice(message=f"查询画作：{pid}主信息成功", url=artwork_url)
            return "000", "交易成功", resp_entity
        else:
            return "000", "交易成功", f"未查到[{pid}]主信息记录。"
    except Exception as e:
        return "022", f"{e}", None


async def download_by_pid(initializer, entity):
    """
    :功能描述: 通过pid进行下载
    :param initializer: 初始化器
    :param entity: 请求体
    :return: 下载成功
    :Author: Lancelot
    :Date: 2024/12/21 23:06
    """
    thread_pool = ThreadPool(initializer.scoped_session, 1, 1)
    try:
        pid = entity.get("arondight.req.entity.pid", "pid为空")
        sn = entity.get_def("arondight.req.entity.sn", 0)
        collect_type = entity.get_def("arondight.req.entity.collect_type",
                                      PixivCollectTypeEnum.PIXIV_COLLECT_TYPE_8.code)
        modify_file_date_ind = entity.get_def("arondight.req.entity.modify_file_date_ind",
                                              PixivModifyFileDateIndEnum.PIXIV_MODIFY_FILE_DATE_IND_0.code)

        context = copy.deepcopy(initializer.context)
        context.set("pixiv.pid", pid)
        context.set("pixiv.sn", sn)
        context.set("pixiv.collect_type", collect_type)
        context.set("pixiv.modify_file_date_ind", modify_file_date_ind)
        context.set("pixiv.lock_ind", generate_unique_8digit())

        logger.info(f"开始作品[{pid}]下载任务。")
        client = Client(context.get("config.cookies"))
        client.generate_client()
        crawler = Crawler(client=client, scoped_session=initializer.scoped_session)
        crawler.check_exist_prim(context)
        task = asyncio.create_task(asyncio.to_thread(crawler.download_by_pid, context))

        initializer.notifier.notice(message=f"添加作品[{pid}]下载任务成功。")
        return "000", "交易成功", f"添加作品[{pid}]下载任务成功，请稍后查看。"
    except Exception as e:
        return "022", f"{e}", None
    finally:
        thread_pool.close()
