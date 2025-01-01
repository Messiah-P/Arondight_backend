from common.database.transaction import get_session
from common.log.log_manager import logger
from dao.dos.pixiv import pixiv_tag_dos


def insert(scoped_session, pixiv_tag_po):
    return pixiv_tag_dos.insert(get_session(scoped_session), pixiv_tag_po)


def select_by_primary_key(scoped_session, pixiv_tag_po):
    return pixiv_tag_dos.select_by_primary_key(get_session(scoped_session), pixiv_tag_po)


def update_by_primary_key_selective(scoped_session, pixiv_tag_po):
    return pixiv_tag_dos.update_by_primary_key_selective(get_session(scoped_session), pixiv_tag_po)


def check_pixiv_tag(scoped_session, pixiv_tag_po):
    results = select_by_primary_key(get_session(scoped_session), pixiv_tag_po)
    if not results:
        result = insert(get_session(scoped_session), pixiv_tag_po)
        logger.success(f"新增标签[{pixiv_tag_po.tag}]信息成功。")
        return result
    else:
        result = update_by_primary_key_selective(get_session(scoped_session), pixiv_tag_po)
        logger.success(f"更新标签[{pixiv_tag_po.tag}]信息成功。")
        return result