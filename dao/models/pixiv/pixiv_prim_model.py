"""
* 功能描述: PIXIV_PRIM表（ORM模型）
* @fileName: pixiv_prim_model.py
* @Author: Messiah
* @Date: 2024/11/10
"""
import datetime
import json
from dataclasses import dataclass

from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy import Integer, String, Text, PrimaryKeyConstraint, Index, BigInteger, \
    ForeignKeyConstraint, DateTime, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from common.database.db_connector import Base


@dataclass
class PixivPrim(Base):
    __tablename__ = 'pixiv_prim'

    pid: Mapped[int] = mapped_column(Integer, nullable=False, comment='作品ID')
    sn: Mapped[int] = mapped_column(Integer, nullable=False, comment='作品序号')
    title: Mapped[str] = mapped_column(Text, nullable=False, comment='作品完整标题')
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='作者ID')
    user_name: Mapped[str] = mapped_column(String(100), nullable=False, comment='作者名')
    collect_type: Mapped[int] = mapped_column(TINYINT, nullable=False, comment='收集类型')
    artwork_url: Mapped[str] = mapped_column(String(240), nullable=True, comment='作品链接')
    original_url: Mapped[str] = mapped_column(String(240), nullable=True, comment='原始下载链接')
    other_urls: Mapped[str] = mapped_column(JSON, nullable=True, comment='其他链接')
    tag: Mapped[str] = mapped_column(JSON, nullable=True, comment='标签')
    page_count: Mapped[int] = mapped_column(Integer, nullable=True, comment='页数')
    illust_type: Mapped[int] = mapped_column(TINYINT, nullable=True, comment='作品类型')
    r18_ind: Mapped[bool] = mapped_column(Boolean, nullable=True, comment='R18标志')
    ai_type: Mapped[int] = mapped_column(TINYINT, nullable=True, comment='AI标志')
    view_count: Mapped[int] = mapped_column(BigInteger, nullable=True, comment='浏览人数')
    bookmark_count: Mapped[int] = mapped_column(BigInteger, nullable=True, comment='收藏人数')
    like_count: Mapped[int] = mapped_column(BigInteger, nullable=True, comment='赞/喜欢人数')
    full_path: Mapped[str] = mapped_column(String(240), nullable=True, comment='保存地址')
    create_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True, comment='创作日期')
    download_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True, comment='下载日期')
    exist_ind: Mapped[bool] = mapped_column(Boolean, nullable=False, comment='作品本地存在标识')

    # 与生成表结构无关，仅用于查询方便
    # USER = relationship("PIXIV_USER", backref='PRIM')

    __table_args__ = (
        PrimaryKeyConstraint('pid', 'sn', 'user_id', 'collect_type'),
        Index('index_user_id', 'user_id'),
        ForeignKeyConstraint(['user_id'], ['pixiv_user.user_id'], name="fk_user_id_prim_to_user"),
    )

    @staticmethod
    def generate_pixiv_prim_po(pixiv_prim_context):
        return PixivPrim(
            pid=pixiv_prim_context.get("pid"),
            sn=pixiv_prim_context.get("sn"),
            title=pixiv_prim_context.get("title"),
            user_id=pixiv_prim_context.get("user_id"),
            user_name=pixiv_prim_context.get("user_name"),
            collect_type=pixiv_prim_context.get("collect_type"),
            artwork_url=pixiv_prim_context.get("artwork_url"),
            original_url=pixiv_prim_context.get("original_url"),
            other_urls=json.dumps(pixiv_prim_context.get("other_urls"), ensure_ascii=False) if pixiv_prim_context.get(
                "other_urls") else None,
            tag=json.dumps(pixiv_prim_context.get("tag"), ensure_ascii=False) if pixiv_prim_context.get(
                "tag") else None,
            page_count=pixiv_prim_context.get("page_count"),
            illust_type=pixiv_prim_context.get("illust_type"),
            r18_ind=pixiv_prim_context.get("r18_ind"),
            ai_type=pixiv_prim_context.get("ai_type"),
            view_count=pixiv_prim_context.get("view_count"),
            bookmark_count=pixiv_prim_context.get("bookmark_count"),
            like_count=pixiv_prim_context.get("like_count"),
            full_path=pixiv_prim_context.get("full_path"),
            create_date=pixiv_prim_context.get("create_date"),
            download_date=pixiv_prim_context.get("download_date"),
            exist_ind=pixiv_prim_context.get("exist_ind"),
        )

    def to_dict(self):
        return {
            'pid': self.pid,
            'sn': self.sn,
            'title': self.title,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'collect_type': self.collect_type,
            'artwork_url': self.artwork_url,
            'original_url': self.original_url,
            'other_urls': json.loads(self.other_urls),
            'tag': json.loads(self.tag),
            'page_count': self.page_count,
            'illust_type': self.illust_type,
            'r18_ind': self.r18_ind,
            'ai_type': self.ai_type,
            'view_count': self.view_count,
            'bookmark_count': self.bookmark_count,
            'like_count': self.like_count,
            'full_path': self.full_path,
            'create_date': self.create_date,
            'download_date': self.download_date,
            'exist_ind': self.exist_ind
        }
