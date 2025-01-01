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
from sqlalchemy import Integer, String, Text, PrimaryKeyConstraint, Index, \
    ForeignKeyConstraint, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from common.context.context import path_converter
from common.database.db_connector import Base


@dataclass
class PixivDwldInfo(Base):
    __tablename__ = 'pixiv_dwld_info'

    pid: Mapped[int] = mapped_column(Integer, nullable=False, comment='作品ID')
    sn: Mapped[int] = mapped_column(Integer, nullable=False, comment='作品序号')
    title: Mapped[str] = mapped_column(Text, nullable=False, comment='作品完整标题')
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='作者ID')
    user_name: Mapped[str] = mapped_column(String(100), nullable=False, comment='作者名')
    collect_type: Mapped[int] = mapped_column(TINYINT, nullable=False, comment='收集类型')
    artwork_url: Mapped[str] = mapped_column(String(240), nullable=True, comment='作品链接')
    original_url: Mapped[str] = mapped_column(String(240), nullable=True, comment='原始下载链接')
    page_count: Mapped[int] = mapped_column(Integer, nullable=True, comment='页数')
    illust_type: Mapped[int] = mapped_column(TINYINT, nullable=True, comment='作品类型')
    zip_info_url: Mapped[str] = mapped_column(String(240), nullable=True, comment='动图zip信息链接')
    zip_path: Mapped[str] = mapped_column(String(240), nullable=True, comment='动图zip保存地址')
    frames_path: Mapped[str] = mapped_column(String(240), nullable=True, comment='动图zip解压地址')
    full_path: Mapped[str] = mapped_column(String(240), nullable=True, comment='保存地址')
    create_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True, comment='创作日期')
    download_status: Mapped[int] = mapped_column(TINYINT, nullable=True, comment='下载状态')
    download_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True, comment='下载日期')
    lock_ind: Mapped[str] = mapped_column(String(32), nullable=True, comment='锁')
    illust_metadata: Mapped[str] = mapped_column(JSON, nullable=False, comment='作品元数据')

    # 与生成表结构无关，仅用于查询方便
    # USER = relationship("PIXIV_USER", backref='PRIM')

    __table_args__ = (
        PrimaryKeyConstraint('pid', 'sn', 'user_id', 'collect_type'),
        Index('index_user_id', 'user_id'),
        ForeignKeyConstraint(['user_id'], ['pixiv_user.user_id'], name="fk_user_id_dwld_to_user"),
    )

    @staticmethod
    def generate_pixiv_dwld_info_po(pixiv_dwld_info_context):
        return PixivDwldInfo(
            pid=pixiv_dwld_info_context.get("pid"),
            sn=pixiv_dwld_info_context.get("sn"),
            title=pixiv_dwld_info_context.get("title"),
            user_id=pixiv_dwld_info_context.get("user_id"),
            user_name=pixiv_dwld_info_context.get("user_name"),
            collect_type=pixiv_dwld_info_context.get("collect_type"),
            artwork_url=pixiv_dwld_info_context.get("artwork_url"),
            original_url=pixiv_dwld_info_context.get("original_url"),
            page_count=pixiv_dwld_info_context.get("page_count"),
            illust_type=pixiv_dwld_info_context.get("illust_type"),
            zip_info_url=pixiv_dwld_info_context.get("zip_info_url"),
            zip_path=pixiv_dwld_info_context.get("zip_path"),
            frames_path=pixiv_dwld_info_context.get("frames_path"),
            full_path=pixiv_dwld_info_context.get("full_path"),
            create_date=pixiv_dwld_info_context.get("create_date"),
            download_status=pixiv_dwld_info_context.get("download_status"),
            download_date=pixiv_dwld_info_context.get("download_date"),
            lock_ind=pixiv_dwld_info_context.get("lock_ind"),
            illust_metadata=pixiv_dwld_info_context.get("illust_metadata"))
        
    def to_dict(self):
        return {
            "pid": self.pid,
            "sn": self.sn,
            "title": self.title,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "collect_type": self.collect_type,
            "artwork_url": self.artwork_url,
            "original_url": self.original_url,
            "page_count": self.page_count,
            "illust_type": self.illust_type,
            "zip_info_url": self.zip_info_url,
            "zip_path": self.zip_path,
            "frames_path": self.frames_path,
            "full_path": self.full_path,
            "create_date": self.create_date,
            "download_status": self.download_status,
            "download_date": self.download_date,
            "lock_ind": self.lock_ind,
            "illust_metadata": self.illust_metadata,
        }
