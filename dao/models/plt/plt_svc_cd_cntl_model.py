"""
* 功能描述: TECH_PARM表（ORM模型）
* @fileName: tech_parm_model.py
* @Author: Messiah
* @Date: 2024/11/10
"""
from dataclasses import dataclass

from sqlalchemy import String, Integer, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from common.database.db_connector import Base


@dataclass
class PltSvcCdCntl(Base):
    __tablename__ = 'plt_svc_cd_cntl'

    svc_cd: Mapped[int] = mapped_column(Integer, nullable=False, comment='服务代码')
    svc_cd_nm: Mapped[str] = mapped_column(String(120), nullable=False, comment='服务代码名称')
    svc_cd_stcd: Mapped[int] = mapped_column(Integer, nullable=False, comment='服务代码状态')

    __table_args__ = (
        PrimaryKeyConstraint('svc_cd'),
    )

    @staticmethod
    def generate_plt_svc_cd_cntl_po(plt_svc_cd_cntl_context):
        return PltSvcCdCntl(
            svc_cd=plt_svc_cd_cntl_context.get("svc_cd"),
            svc_cd_nm=plt_svc_cd_cntl_context.get("svc_cd_nm"),
            svc_cd_stcd=plt_svc_cd_cntl_context.get("svc_cd_stcd"),
        )

    def to_dict(self):
        return {
            "svc_cd": self.svc_cd,
            "svc_cd_nm": self.svc_cd_nm,
            "svc_cd_stcd": self.svc_cd_stcd,
        }
