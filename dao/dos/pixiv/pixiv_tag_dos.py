from sqlalchemy import MetaData, text

from dao.models.pixiv.pixiv_tag_model import PixivTag

metadata = MetaData()


def insert(session, pixiv_tag_po: PixivTag):
    parameters = {"tag": pixiv_tag_po.tag,
                  "translation": pixiv_tag_po.translation}

    insert_sql = (f"INSERT INTO pixiv_tag "
                  f"(tag, translation)"
                  f"VALUES (:tag, :translation) ")
    return session.execute(text(insert_sql), parameters)


def select_by_primary_key(session, pixiv_tag_po: PixivTag):
    parameters = {"tag": pixiv_tag_po.tag}

    sql = (f"SELECT * "
           f"FROM pixiv_tag "
           f"WHERE tag = :tag ")

    return session.execute(text(sql), parameters).one_or_none()


def update_by_primary_key_selective(session, pixiv_tag_po: PixivTag):
    update_fields = []
    parameters = {"tag": pixiv_tag_po.tag}

    if pixiv_tag_po.translation is not None:
        update_fields.append("translation = :translation")
        parameters["translation"] = pixiv_tag_po.translation

    if update_fields:
        update_sql = (f"UPDATE pixiv_tag "
                      f"SET {', '.join(update_fields)} "
                      f"WHERE tag = :tag ")

        return session.execute(text(update_sql), parameters)
