from sqlalchemy import MetaData, text

from dao.models.pixiv.pixiv_prim_tag_model import PixivPrimTag

metadata = MetaData()


def insert(session, pixiv_prim_tag_po: PixivPrimTag):
    parameters = {"pid": pixiv_prim_tag_po.pid,
                  "sn": pixiv_prim_tag_po.sn,
                  "user_id": pixiv_prim_tag_po.user_id,
                  "collect_type": pixiv_prim_tag_po.collect_type,
                  "tag": pixiv_prim_tag_po.tag, }

    insert_sql = (f"INSERT INTO pixiv_prim_tag "
                  f"(pid, sn, user_id, collect_type, tag )"
                  f"VALUES (:pid, :sn, :user_id, :collect_type, :tag)")
    return session.execute(text(insert_sql), parameters)


def select_by_primary_key(session, pixiv_prim_tag_po: PixivPrimTag):
    parameters = {"pid": pixiv_prim_tag_po.pid,
                  "sn": pixiv_prim_tag_po.sn,
                  "user_id": pixiv_prim_tag_po.user_id,
                  "collect_type": pixiv_prim_tag_po.collect_type,
                  "tag": pixiv_prim_tag_po.tag}

    sql = (f"SELECT * "
           f"FROM pixiv_prim_tag "
           f"WHERE pid = :pid "
           f"AND sn = :sn "
           f"AND user_id = :user_id "
           f"AND collect_type = :collect_type "
           f"AND tag = :tag")

    return session.execute(text(sql), parameters).one_or_none()
