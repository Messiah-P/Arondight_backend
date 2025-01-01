"""
* 功能描述: PIXIV_USER表（ORM模型）
* @fileName: pixiv_user_model.py
* @Author: Messiah
* @Date: 2024/11/10
"""
from dataclasses import dataclass
from sqlalchemy import Integer, String, UniqueConstraint, Index, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from common.database.db_connector import Base


@dataclass
class PixivUser(Base):
    __tablename__ = 'pixiv_user'

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=False,comment='作者ID')
    user_name: Mapped[str] = mapped_column(String(100), nullable=False, comment='作者名')
    latest_pid: Mapped[int] = mapped_column(Integer, nullable=True, comment='最新作品ID')
    follow_ind: Mapped[bool] = mapped_column(Boolean, nullable=True, comment='关注标识', default=False)
    follow_type: Mapped[str] = mapped_column(String(10), nullable=True, comment='关注类型')

    __table_args__ = (
        UniqueConstraint('user_id', 'latest_pid', name='unique_id_pid'),
        Index('index_follow_ind', 'follow_ind'),
    )

    @staticmethod
    def generate_pixiv_user_po(pixiv_user_context):
        return PixivUser(
            user_id=pixiv_user_context.get("user_id"),
            user_name=pixiv_user_context.get("user_name"),
            latest_pid=pixiv_user_context.get("latest_pid"),
            follow_ind=pixiv_user_context.get("follow_ind"),
            follow_type=pixiv_user_context.get("follow_type"),
        )

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "latest_pid": self.latest_pid,
            "follow_ind": self.follow_ind,
            "follow_type": self.follow_type,
        }