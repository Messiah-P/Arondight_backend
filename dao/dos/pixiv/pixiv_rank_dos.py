"""
* 功能描述: 操作PIXIV_RANK表
* @fileName: pixiv_rank_dos.py
* @Author: Messiah
* @Date: 2024/12/2
"""
from sqlalchemy import MetaData, text
from dao.models.pixiv.pixiv_rank_model import PixivRank

metadata = MetaData()


def insert(session, pixiv_rank_po: PixivRank):
    parameters = {
        "pid": pixiv_rank_po.pid,
        "sn": pixiv_rank_po.sn,
        "user_id": pixiv_rank_po.user_id,
        "rank_type": pixiv_rank_po.rank_type,
        "rank_position": pixiv_rank_po.rank_position,
        "rank_date": pixiv_rank_po.rank_date,
    }
    insert_sql = (f"INSERT INTO pixiv_rank "
                  f"(pid, sn, user_id, "
                  f"rank_type, rank_position, rank_date)"
                  f"VALUES (:pid, :sn, :user_id, "
                  f":rank_type, :rank_position, :rank_date) ")
    return session.execute(text(insert_sql), parameters)


def select_by_primary_key(session, pixiv_rank_po: PixivRank):
    parameters = {"pid": pixiv_rank_po.pid,
                  "sn": pixiv_rank_po.sn,
                  "user_id": pixiv_rank_po.user_id}

    sql = (f"SELECT * "
           f"FROM pixiv_rank "
           f"WHERE pid = :pid "
           f"AND sn = :sn "
           f"AND user_id = :user_id ")

    return session.execute(text(sql), parameters).one_or_none()


def update_by_primary_key_selective(session, pixiv_rank_po: PixivRank):
    update_fields = []
    parameters = {"pid": pixiv_rank_po.pid,
                  "sn": pixiv_rank_po.sn,
                  "user_id": pixiv_rank_po.user_id}

    if pixiv_rank_po.rank_type is not None:
        update_fields.append("rank_type = :rank_type")
        parameters["rank_type"] = pixiv_rank_po.rank_type

    if pixiv_rank_po.rank_position is not None:
        update_fields.append("rank_position = :rank_position")
        parameters["rank_position"] = pixiv_rank_po.rank_position

    if pixiv_rank_po.rank_date is not None:
        update_fields.append("rank_date = :rank_date")
        parameters["rank_date"] = pixiv_rank_po.rank_date

    if update_fields:
        update_sql = (f"UPDATE pixiv_rank "
                      f"SET {', '.join(update_fields)} "
                      f"WHERE pid = :pid "
                      f"AND sn = :sn "
                      f"AND user_id = :user_id")

        return session.execute(text(update_sql), parameters)
