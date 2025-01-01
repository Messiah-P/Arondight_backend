"""
* 功能描述: 操作PIXIV_USER表
* @fileName: pixiv_user_dos.py
* @Author: Messiah
* @Date: 2024/11/21
"""

from sqlalchemy import MetaData, text
from dao.models.pixiv.pixiv_user_model import PixivUser

metadata = MetaData()


def insert(session, pixiv_user_po: PixivUser):
    pixiv_user = PixivUser(user_id=pixiv_user_po.user_id,
                           user_name=pixiv_user_po.user_name,
                           latest_pid=pixiv_user_po.latest_pid,
                           follow_ind=pixiv_user_po.follow_ind,
                           follow_type=pixiv_user_po.follow_type)
    session.add(pixiv_user)
    return pixiv_user


def select_by_primary_key(session, pixiv_user_po: PixivUser):
    parameters = {"user_id": pixiv_user_po.user_id}

    sql = (f"SELECT * "
           f"FROM pixiv_user "
           f"WHERE user_id = :user_id ")

    return session.execute(text(sql), parameters).one_or_none()


def update_by_primary_key_selective(session, pixiv_user_po: PixivUser):
    update_fields = []
    parameters = {"user_id": pixiv_user_po.user_id}

    if pixiv_user_po.user_name is not None:
        update_fields.append("user_name = :user_name")
        parameters["user_name"] = pixiv_user_po.user_name

    if pixiv_user_po.latest_pid is not None:
        update_fields.append("latest_pid = :latest_pid")
        parameters["latest_pid"] = pixiv_user_po.latest_pid

    if pixiv_user_po.follow_ind is not None:
        update_fields.append("follow_ind = :follow_ind")
        parameters["follow_ind"] = pixiv_user_po.follow_ind

    if pixiv_user_po.follow_type is not None:
        update_fields.append("follow_type = :follow_type")
        parameters["follow_type"] = pixiv_user_po.follow_type

    if update_fields:
        update_sql = (f"UPDATE pixiv_user "
                      f"SET {', '.join(update_fields)} "
                      f"WHERE user_id = :user_id ")
        return session.execute(text(update_sql), parameters)


def delete_by_primary_key(session, pixiv_user_po: PixivUser):
    pixiv_user = session.query(PixivUser).filter(user_id=pixiv_user_po.user_id).first()
    if pixiv_user:
        session.delete(pixiv_user)
