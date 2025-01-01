"""
* 功能描述: PIXIV_RANK表（ORM模型）
* @fileName: pixiv_rank_model.py
* @Author: Messiah
* @Date: 2024/11/10
"""
import datetime
from dataclasses import dataclass
from sqlalchemy import Integer, PrimaryKeyConstraint, Index, ForeignKeyConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from common.database.db_connector import Base


@dataclass
class PixivRank(Base):
    __tablename__ = 'pixiv_rank'

    pid: Mapped[int] = mapped_column(Integer, nullable=False, comment='作品ID')
    sn: Mapped[int] = mapped_column(Integer, nullable=False, comment='作品序号')
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='作者ID')
    rank_type: Mapped[int] = mapped_column(Integer, nullable=True, comment='上榜类型')
    rank_position: Mapped[int] = mapped_column(Integer, nullable=True, comment='上榜名次')
    rank_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True, comment='上榜日期')

    # 与生成表结构无关，仅用于查询方便
    # USER = relationship("PIXIV_USER", backref='RANK')
    # PIC = relationship("PIXIV_PRIM", backref='RANK')

    __table_args__ = (
        PrimaryKeyConstraint('pid', 'sn', 'user_id'),
        Index('index_user_id', 'user_id'),
        ForeignKeyConstraint(['pid', 'sn', 'user_id'], ['pixiv_prim.pid', 'pixiv_prim.sn', 'pixiv_prim.user_id'],
                             name='fk_pic_rank_to_prim'),
        ForeignKeyConstraint(['user_id'], ['pixiv_user.user_id'], name="fk_user_id_rank_to_user"),
    )

    @staticmethod
    def generate_pixiv_rank_po(pixiv_rank_context):
        return PixivRank(
            pid=pixiv_rank_context.get("pid"),
            sn=pixiv_rank_context.get("sn"),
            user_id=pixiv_rank_context.get("user_id"),
            rank_type=pixiv_rank_context.get("rank_type"),
            rank_position=pixiv_rank_context.get("rank_position"),
            rank_date=pixiv_rank_context.get("rank_date"),
        )

    def to_dict(self):
        return {
            "pid": self.pid,
            "sn": self.sn,
            "user_id": self.user_id,
            "rank_type": self.rank_type,
            "rank_position": self.rank_position,
            "rank_date": self.rank_date,
        }