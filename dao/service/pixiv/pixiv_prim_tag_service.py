from common.database.transaction import get_session
from common.log.log_manager import logger
from dao.dos.pixiv import pixiv_prim_tag_dos


def insert(scoped_session, pixiv_prim_tag_po):
    return pixiv_prim_tag_dos.insert(get_session(scoped_session), pixiv_prim_tag_po)


def select_by_primary_key(scoped_session, pixiv_prim_tag_po):
    return pixiv_prim_tag_dos.select_by_primary_key(get_session(scoped_session), pixiv_prim_tag_po)


def check_pixiv_prim_tag(scoped_session, pixiv_prim_tag_po):
    results = select_by_primary_key(get_session(scoped_session), pixiv_prim_tag_po)
    if not results:
        result = insert(get_session(scoped_session), pixiv_prim_tag_po)
        logger.success(f"新增标签[{pixiv_prim_tag_po.tag}]关联信息成功。")
        return result
    else:
        logger.success(f"标签[{pixiv_prim_tag_po.tag}]关联信息已存在。")
