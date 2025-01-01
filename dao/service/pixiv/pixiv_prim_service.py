from common.database.transaction import get_session
from common.log.log_manager import logger
from dao.dos.pixiv import pixiv_prim_dos


def insert(scoped_session, pixiv_prim_po):
    return pixiv_prim_dos.insert(get_session(scoped_session), pixiv_prim_po)


def select_by_primary_key(scoped_session, pixiv_prim_po):
    return pixiv_prim_dos.select_by_primary_key(get_session(scoped_session), pixiv_prim_po)


def update_by_primary_key_selective(scoped_session, pixiv_prim_po):
    return pixiv_prim_dos.update_by_primary_key_selective(get_session(scoped_session), pixiv_prim_po)


def select_by_user_id_and_collect_type(scoped_session, pixiv_prim_po):
    return pixiv_prim_dos.select_by_user_id_and_collect_type(get_session(scoped_session), pixiv_prim_po)


def select_by_pid_sn_collect_type(scoped_session, pixiv_prim_po):
    return pixiv_prim_dos.select_by_pid_sn_collect_type(get_session(scoped_session), pixiv_prim_po)


def select_by_pid_sn_collect_type_batch(scoped_session, pixiv_prim_pos):
    return pixiv_prim_dos.select_by_pid_sn_collect_type_batch(get_session(scoped_session), pixiv_prim_pos)


def select_by_pid(scoped_session, pixiv_prim_po):
    return pixiv_prim_dos.select_by_pid(get_session(scoped_session), pixiv_prim_po)


def check_pixiv_prim(scoped_session, pixiv_prim_po):
    results = select_by_primary_key(get_session(scoped_session), pixiv_prim_po)
    if not results:
        result = insert(get_session(scoped_session), pixiv_prim_po)
        logger.success(f"新增主信息成功。")
        return result
    else:
        result = update_by_primary_key_selective(get_session(scoped_session), pixiv_prim_po)
        logger.success(f"更新主信息成功。")
        return result
