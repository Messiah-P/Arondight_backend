from common.database.transaction import get_session
from common.log.log_manager import logger
from dao.dos.pixiv import pixiv_rank_dos


def insert(scoped_session, pixiv_rank_po):
    return pixiv_rank_dos.insert(get_session(scoped_session), pixiv_rank_po)


def select_by_primary_key(scoped_session, pixiv_rank_po):
    return pixiv_rank_dos.select_by_primary_key(get_session(scoped_session), pixiv_rank_po)


def update_by_primary_key_selective(scoped_session, pixiv_rank_po):
    return pixiv_rank_dos.update_by_primary_key_selective(get_session(scoped_session), pixiv_rank_po)


def check_pixiv_rank(scoped_session, pixiv_rank_po):
    results = select_by_primary_key(get_session(scoped_session), pixiv_rank_po)
    if not results:
        result = insert(get_session(scoped_session), pixiv_rank_po)
        logger.success(f"新增榜单信息成功。")
        return result
    else:
        result = update_by_primary_key_selective(get_session(scoped_session), pixiv_rank_po)
        logger.success(f"更新榜单信息成功。")
        return result
