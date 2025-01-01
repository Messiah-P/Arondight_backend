"""
* 功能描述: 操作PIXIV_DWLD_INFO表
* @fileName: pixiv_dwld_info_dos.py
* @Author: Messiah
* @Date: 2024/11/21
"""

from sqlalchemy import MetaData, text
from dao.models.pixiv.pixiv_dwld_info_model import PixivDwldInfo

metadata = MetaData()


def insert(session, pixiv_dwld_info_po: PixivDwldInfo):
    parameters = {
        "pid": pixiv_dwld_info_po.pid,
        "sn": pixiv_dwld_info_po.sn,
        "title": pixiv_dwld_info_po.title,
        "user_id": pixiv_dwld_info_po.user_id,
        "user_name": pixiv_dwld_info_po.user_name,
        "collect_type": pixiv_dwld_info_po.collect_type,
        "artwork_url": pixiv_dwld_info_po.artwork_url,
        "original_url": pixiv_dwld_info_po.original_url,
        "page_count": pixiv_dwld_info_po.page_count,
        "illust_type": pixiv_dwld_info_po.illust_type,
        "zip_info_url": pixiv_dwld_info_po.zip_info_url,
        "zip_path": pixiv_dwld_info_po.zip_path,
        "frames_path": pixiv_dwld_info_po.frames_path,
        "full_path": pixiv_dwld_info_po.full_path,
        "create_date": pixiv_dwld_info_po.create_date,
        "download_status": pixiv_dwld_info_po.download_status,
        "download_date": pixiv_dwld_info_po.download_date,
        "lock_ind": pixiv_dwld_info_po.lock_ind,
        "illust_metadata": pixiv_dwld_info_po.illust_metadata
    }

    insert_sql = (f"INSERT INTO pixiv_dwld_info "
                  f"(pid, sn, title, user_id, user_name, collect_type, "
                  f"artwork_url, original_url, page_count, illust_type, "
                  f"zip_info_url, zip_path, frames_path, full_path, create_date, "
                  f"download_status, download_date, lock_ind, illust_metadata)"
                  f"VALUES (:pid, :sn, :title, :user_id, :user_name, :collect_type, "
                  f":artwork_url, :original_url, :page_count, :illust_type, "
                  f":zip_info_url, :zip_path, :frames_path, :full_path, :create_date, "
                  f":download_status, :download_date, :lock_ind, :illust_metadata)"
                  )

    return session.execute(text(insert_sql), parameters)


def select_by_primary_key(session, pixiv_dwld_info_po: PixivDwldInfo):
    parameters = {"pid": pixiv_dwld_info_po.pid,
                  "sn": pixiv_dwld_info_po.sn,
                  "user_id": pixiv_dwld_info_po.user_id,
                  "collect_type": pixiv_dwld_info_po.collect_type}

    sql = (f"SELECT * "
           f"FROM pixiv_dwld_info "
           f"WHERE pid = :pid "
           f"AND sn = :sn "
           f"AND user_id = :user_id "
           f"AND collect_type = :collect_type ")

    return session.execute(text(sql), parameters).one_or_none()


def update_by_primary_key_selective(session, pixiv_dwld_info_po: PixivDwldInfo):
    # 动态构建更新语句
    update_fields = []
    parameters = {"pid": pixiv_dwld_info_po.pid,
                  "sn": pixiv_dwld_info_po.sn,
                  "user_id": pixiv_dwld_info_po.user_id,
                  "collect_type": pixiv_dwld_info_po.collect_type}

    if pixiv_dwld_info_po.title is not None:
        update_fields.append("title = :title")
        parameters["title"] = pixiv_dwld_info_po.title

    if pixiv_dwld_info_po.user_name is not None:
        update_fields.append("user_name = :user_name")
        parameters["user_name"] = pixiv_dwld_info_po.user_name

    if pixiv_dwld_info_po.artwork_url is not None:
        update_fields.append("artwork_url = :artwork_url")
        parameters["artwork_url"] = pixiv_dwld_info_po.artwork_url

    if pixiv_dwld_info_po.original_url is not None:
        update_fields.append("original_url = :original_url")
        parameters["original_url"] = pixiv_dwld_info_po.original_url

    if pixiv_dwld_info_po.page_count is not None:
        update_fields.append("page_count = :page_count")
        parameters["page_count"] = pixiv_dwld_info_po.page_count

    if pixiv_dwld_info_po.illust_type is not None:
        update_fields.append("illust_type = :illust_type")
        parameters["illust_type"] = pixiv_dwld_info_po.illust_type

    if pixiv_dwld_info_po.zip_info_url is not None:
        update_fields.append("zip_info_url = :zip_info_url")
        parameters["zip_info_url"] = pixiv_dwld_info_po.zip_info_url

    if pixiv_dwld_info_po.zip_path is not None:
        update_fields.append("zip_path = :zip_path")
        parameters["zip_path"] = pixiv_dwld_info_po.zip_path

    if pixiv_dwld_info_po.frames_path is not None:
        update_fields.append("frames_path = :frames_path")
        parameters["frames_path"] = pixiv_dwld_info_po.frames_path

    if pixiv_dwld_info_po.full_path is not None:
        update_fields.append("full_path = :full_path")
        parameters["full_path"] = pixiv_dwld_info_po.full_path

    if pixiv_dwld_info_po.create_date is not None:
        update_fields.append("create_date = :create_date")
        parameters["create_date"] = pixiv_dwld_info_po.create_date

    if pixiv_dwld_info_po.download_status is not None:
        update_fields.append("download_status = :download_status")
        parameters["download_status"] = pixiv_dwld_info_po.download_status

    if pixiv_dwld_info_po.download_date is not None:
        update_fields.append("download_date = :download_date")
        parameters["download_date"] = pixiv_dwld_info_po.download_date

    if pixiv_dwld_info_po.lock_ind is not None:
        update_fields.append("lock_ind = :lock_ind")
        parameters["lock_ind"] = pixiv_dwld_info_po.lock_ind

    if pixiv_dwld_info_po.illust_metadata is not None:
        update_fields.append("illust_metadata = :illust_metadata")
        parameters["illust_metadata"] = pixiv_dwld_info_po.illust_metadata

    # 动态添加 WHERE 子句中的 lock_ind 条件
    where_clauses = [
        "pid = :pid",
        "sn = :sn",
        "user_id = :user_id",
        "collect_type = :collect_type"
    ]
    if pixiv_dwld_info_po.lock_ind is not None:
        where_clauses.append("lock_ind = :lock_ind")
        parameters["lock_ind"] = pixiv_dwld_info_po.lock_ind

    if update_fields:
        # 拼接更新语句
        update_sql = (f"UPDATE pixiv_dwld_info "
                      f"SET {', '.join(update_fields)} "
                      f"WHERE {' AND '.join(where_clauses)}")

        return session.execute(text(update_sql), parameters)


def select_undownloaded_task_by_pid_and_collect_type(session, pid, collect_type, download_status):
    """
    :功能描述: 根据pid和collect_type查询未下载的作品
    :Author: Lancelot
    :Date: 2024/12/22 00:47
    """
    parameters = {"pid": pid, "collect_type": collect_type, "download_status": download_status}
    sql = (f"SELECT * "
           f"FROM pixiv_dwld_info "
           f"WHERE pid = :pid "
           f"AND collect_type = :collect_type "
           f"AND download_status != :download_status "
           f"AND lock_ind IS NULL ")

    return session.execute(text(sql), parameters).fetchall()


def select_undownloaded_task_by_collect_type(session, collect_type, download_status):
    """
    * 功能描述: 根据collect_type查询未下载的作品
    * @fileName: pixiv_dwld_info_dos.py
    * @Author: Lancelot
    * @Date: 2024/12/31 17:22
    """
    parameters = {"collect_type": collect_type, "download_status": download_status}
    sql = (f"SELECT * "
           f"FROM pixiv_dwld_info "
           f"WHERE collect_type = :collect_type "
           f"AND download_status != :download_status "
           f"AND lock_ind IS NULL ")

    return session.execute(text(sql), parameters).fetchall()


def lock_download_task(session, pixiv_dwld_info_po: PixivDwldInfo):
    parameters = {"pid": pixiv_dwld_info_po.pid,
                  "sn": pixiv_dwld_info_po.sn,
                  "user_id": pixiv_dwld_info_po.user_id,
                  "download_status": pixiv_dwld_info_po.download_status,
                  "lock_ind": pixiv_dwld_info_po.lock_ind}

    update_sql = (f"UPDATE pixiv_dwld_info "
                  f"SET lock_ind = :lock_ind "
                  f"WHERE pid = :pid "
                  f"AND sn = :sn "
                  f"AND user_id = :user_id "
                  f"AND download_status = :download_status "
                  f"AND lock_ind IS NULL ")

    return session.execute(text(update_sql), parameters)


def unlock_download_task(session, pixiv_dwld_info_po: PixivDwldInfo):
    parameters = {"pid": pixiv_dwld_info_po.pid,
                  "sn": pixiv_dwld_info_po.sn,
                  "user_id": pixiv_dwld_info_po.user_id,
                  "download_status": pixiv_dwld_info_po.download_status,
                  "lock_ind": pixiv_dwld_info_po.lock_ind}

    update_sql = (f"UPDATE pixiv_dwld_info "
                  f"SET lock_ind = NULL "
                  f"WHERE pid = :pid "
                  f"AND sn = :sn "
                  f"AND user_id = :user_id "
                  f"AND download_status = :download_status "
                  f"AND lock_ind = :lock_ind ")

    return session.execute(text(update_sql), parameters)
