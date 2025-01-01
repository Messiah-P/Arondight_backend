"""
* 功能描述: 操作PIXIV_PRIM表
* @fileName: pixiv_prim_dos.py
* @Author: Lancelot
* @Date: 2024/11/22 13:50
"""
from typing import List

from sqlalchemy import text

from dao.models.pixiv.pixiv_prim_model import PixivPrim


def insert(session, pixiv_prim_po: PixivPrim):
    parameters = {
        "pid": pixiv_prim_po.pid,
        "sn": pixiv_prim_po.sn,
        "title": pixiv_prim_po.title,
        "user_id": pixiv_prim_po.user_id,
        "user_name": pixiv_prim_po.user_name,
        "collect_type": pixiv_prim_po.collect_type,
        "artwork_url": pixiv_prim_po.artwork_url,
        "original_url": pixiv_prim_po.original_url,
        "other_urls": pixiv_prim_po.other_urls,
        "tag": pixiv_prim_po.tag,
        "page_count": pixiv_prim_po.page_count,
        "illust_type": pixiv_prim_po.illust_type,
        "r18_ind": pixiv_prim_po.r18_ind,
        "ai_type": pixiv_prim_po.ai_type,
        "view_count": pixiv_prim_po.view_count,
        "bookmark_count": pixiv_prim_po.bookmark_count,
        "like_count": pixiv_prim_po.like_count,
        "full_path": pixiv_prim_po.full_path,
        "create_date": pixiv_prim_po.create_date,
        "download_date": pixiv_prim_po.download_date,
        "exist_ind": pixiv_prim_po.exist_ind,
    }

    insert_sql = (f"INSERT INTO pixiv_prim "
                  f"(pid, sn, title, user_id, user_name, collect_type, "
                  f"artwork_url, original_url, other_urls, tag, "
                  f"page_count, illust_type, r18_ind, ai_type, "
                  f"view_count, bookmark_count, like_count, "
                  f"full_path, create_date, download_date, exist_ind)"
                  f"VALUES (:pid, :sn, :title, :user_id, :user_name, :collect_type, "
                  f":artwork_url, :original_url, :other_urls, :tag, "
                  f":page_count, :illust_type, :r18_ind, :ai_type, "
                  f":view_count, :bookmark_count, :like_count, "
                  f":full_path, :create_date, :download_date, :exist_ind)"
                  )

    return session.execute(text(insert_sql), parameters)


def select_by_primary_key(session, pixiv_prim_po: PixivPrim):
    parameters = {"pid": pixiv_prim_po.pid,
                  "sn": pixiv_prim_po.sn,
                  "user_id": pixiv_prim_po.user_id,
                  "collect_type": pixiv_prim_po.collect_type}

    sql = (f"SELECT * "
           f"FROM pixiv_prim "
           f"WHERE pid = :pid "
           f"AND sn = :sn "
           f"AND user_id = :user_id "
           f"AND collect_type = :collect_type ")

    return session.execute(text(sql), parameters).one_or_none()


def update_by_primary_key_selective(session, pixiv_prim_po: PixivPrim):
    update_fields = []
    parameters = {"pid": pixiv_prim_po.pid,
                  "sn": pixiv_prim_po.sn,
                  "user_id": pixiv_prim_po.user_id,
                  "collect_type": pixiv_prim_po.collect_type}

    if pixiv_prim_po.title is not None:
        update_fields.append("title = :title")
        parameters["title"] = pixiv_prim_po.title

    if pixiv_prim_po.user_name is not None:
        update_fields.append("user_name = :user_name")
        parameters["user_name"] = pixiv_prim_po.user_name

    if pixiv_prim_po.artwork_url is not None:
        update_fields.append("artwork_url = :artwork_url")
        parameters["artwork_url"] = pixiv_prim_po.artwork_url

    if pixiv_prim_po.original_url is not None:
        update_fields.append("original_url = :original_url")
        parameters["original_url"] = pixiv_prim_po.original_url

    if pixiv_prim_po.other_urls is not None:
        update_fields.append("other_urls = :other_urls")
        parameters["other_urls"] = pixiv_prim_po.other_urls

    if pixiv_prim_po.tag is not None:
        update_fields.append("tag = :tag")
        parameters["tag"] = pixiv_prim_po.tag

    if pixiv_prim_po.page_count is not None:
        update_fields.append("page_count = :page_count")
        parameters["page_count"] = pixiv_prim_po.page_count

    if pixiv_prim_po.illust_type is not None:
        update_fields.append("illust_type = :illust_type")
        parameters["illust_type"] = pixiv_prim_po.illust_type

    if pixiv_prim_po.r18_ind is not None:
        update_fields.append("r18_ind = :r18_ind")
        parameters["r18_ind"] = pixiv_prim_po.r18_ind

    if pixiv_prim_po.ai_type is not None:
        update_fields.append("ai_type = :ai_type")
        parameters["ai_type"] = pixiv_prim_po.ai_type

    if pixiv_prim_po.view_count is not None:
        update_fields.append("view_count = :view_count")
        parameters["view_count"] = pixiv_prim_po.view_count

    if pixiv_prim_po.bookmark_count is not None:
        update_fields.append("bookmark_count = :bookmark_count")
        parameters["bookmark_count"] = pixiv_prim_po.bookmark_count

    if pixiv_prim_po.like_count is not None:
        update_fields.append("like_count = :like_count")
        parameters["like_count"] = pixiv_prim_po.like_count

    if pixiv_prim_po.full_path is not None:
        update_fields.append("full_path = :full_path")
        parameters["full_path"] = pixiv_prim_po.full_path

    if pixiv_prim_po.create_date is not None:
        update_fields.append("create_date = :create_date")
        parameters["create_date"] = pixiv_prim_po.create_date

    if pixiv_prim_po.download_date is not None:
        update_fields.append("download_date = :download_date")
        parameters["download_date"] = pixiv_prim_po.download_date

    if pixiv_prim_po.exist_ind is not None:
        update_fields.append("exist_ind = :exist_ind")
        parameters["exist_ind"] = pixiv_prim_po.exist_ind

    update_fields_str = ', '.join(update_fields)

    if update_fields:
        update_sql = (f"UPDATE pixiv_prim "
                      f"SET {update_fields_str} "
                      f"WHERE pid = :pid "
                      f"AND sn =:sn "
                      f"AND user_id = :user_id "
                      f"AND collect_type = :collect_type ")
        return session.execute(text(update_sql), parameters)


def select_by_user_id_and_collect_type(session, pixiv_prim_po: PixivPrim):
    sql_query = (f"SELECT * "
                 f"FROM pixiv_prim "
                 f"WHERE user_id = :user_id "
                 f"AND collect_type = :collect_type "
                 f"ORDER BY pid ")

    return session.execute(text(sql_query), {'user_id': pixiv_prim_po.user_id,
                                             'collect_type': pixiv_prim_po.collect_type}).fetchall()


def select_by_pid_sn_collect_type(session, pixiv_prim_po: PixivPrim):
    parameters = {"pid": pixiv_prim_po.pid, "sn": pixiv_prim_po.sn, "collect_type": pixiv_prim_po.collect_type}
    sql = (f"SELECT * "
           f"FROM pixiv_prim "
           f"WHERE pid = :pid "
           f"AND sn = :sn "
           f"AND collect_type = :collect_type ")
    return session.execute(text(sql), parameters).one_or_none()


def select_by_pid_sn_collect_type_batch(session, pixiv_prim_pos: List[PixivPrim]):
    parameters = [(po.pid, po.sn, po.collect_type) for po in pixiv_prim_pos]
    sql = (f"SELECT * "
           f"FROM pixiv_prim "
           f"WHERE (pid, sn, collect_type) IN :params ")
    return session.execute(text(sql), {"params": parameters}).fetchall()


def select_by_pid(session, pixiv_prim_po: PixivPrim):
    parameters = {"pid": pixiv_prim_po.pid}
    sql = (f"SELECT * "
           f"FROM pixiv_prim "
           f"WHERE pid = :pid ")
    return session.execute(text(sql), parameters)
