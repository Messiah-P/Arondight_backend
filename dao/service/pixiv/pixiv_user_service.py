from common.database.transaction import get_session
from common.log.log_manager import logger
from dao.dos.pixiv import pixiv_user_dos


def insert(scoped_session, pixiv_user_po):
    pixiv_user_dos.insert(get_session(scoped_session), pixiv_user_po)


def select_by_primary_key(scoped_session, pixiv_user_po):
    result = pixiv_user_dos.select_by_primary_key(get_session(scoped_session), pixiv_user_po)
    return result


def update_by_primary_key_selective(scoped_session, pixiv_user_po):
    return pixiv_user_dos.update_by_primary_key_selective(get_session(scoped_session), pixiv_user_po)


def check_pixiv_user(scoped_session, pixiv_user_po):
    result = select_by_primary_key(get_session(scoped_session), pixiv_user_po)
    if not result:
        insert(get_session(scoped_session), pixiv_user_po)
        logger.success(f"新增画师信息成功。")
    else:
        update_by_primary_key_selective(get_session(scoped_session), pixiv_user_po)
        logger.success(f"更新画师信息成功。")


def check_user_latest_pid(scoped_session, pixiv_user_po):
    """
    * 功能描述: 检查画师记录是否存在，若存在，返回表中LATEST_PID
    * @fileName: pixiv_user_service.py
    * @Author: Messiah
    * @Date: 2024/11/22
    """
    result = pixiv_user_dos.select_by_primary_key(get_session(scoped_session), pixiv_user_po)
    return result.latest_pid
