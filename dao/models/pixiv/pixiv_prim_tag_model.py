from sqlalchemy import Integer, ForeignKeyConstraint, String
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.orm import relationship, Mapped, mapped_column
from common.database.db_connector import Base
from dao.models.pixiv.pixiv_prim_model import PixivPrim
from dao.models.pixiv.pixiv_tag_model import PixivTag


class PixivPrimTag(Base):
    __tablename__ = 'pixiv_prim_tag'

    pid: Mapped[int] = mapped_column(Integer, primary_key=True, comment='作品ID')
    sn: Mapped[int] = mapped_column(Integer, primary_key=True, comment='作品序号')
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='作者ID')
    collect_type: Mapped[int] = mapped_column(TINYINT, primary_key=True, comment='收集类型')
    tag: Mapped[str] = mapped_column(String(255), primary_key=True, comment='标签')

    __table_args__ = (
        ForeignKeyConstraint(['pid', 'sn', 'user_id', "collect_type"],
                             ['pixiv_prim.pid', 'pixiv_prim.sn', 'pixiv_prim.user_id', 'pixiv_prim.collect_type'],
                             name="fk_prim_pk", ondelete='CASCADE'),
        ForeignKeyConstraint(['tag'], ['pixiv_tag.tag'], name="fk_tag", ondelete='CASCADE'),
    )

    pixiv_prim: Mapped['PixivPrim'] = relationship('PixivPrim', backref='tags')
    pixiv_tag: Mapped['PixivTag'] = relationship('PixivTag', backref='prims')

    @staticmethod
    def generate_pixiv_prim_tag_po(pixiv_prim_tag_context):
        return PixivPrimTag(pid=pixiv_prim_tag_context.get("pid"),
                            sn=pixiv_prim_tag_context.get("sn"),
                            user_id=pixiv_prim_tag_context.get("user_id"),
                            collect_type=pixiv_prim_tag_context.get("collect_type"),
                            tag=pixiv_prim_tag_context.get("tag"))
