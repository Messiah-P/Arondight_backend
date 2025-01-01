"""
* 功能描述: TECH_PARM表（ORM模型）
* @fileName: tech_parm_model.py
* @Author: Messiah
* @Date: 2024/11/10
"""
from dataclasses import dataclass

from sqlalchemy import String, Integer, Text, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from common.database.db_connector import Base


@dataclass
class TechParm(Base):
    __tablename__ = 'tech_parm'

    id: Mapped[int] = mapped_column(Integer, nullable=False, comment='编号')
    parm_cd: Mapped[str] = mapped_column(String(30), nullable=False, comment='参数代码')
    parm_sn: Mapped[int] = mapped_column(Integer, nullable=False, comment='参数序号')
    parm_nm: Mapped[str] = mapped_column(String(240), nullable=True, comment='参数名称')
    parm_val: Mapped[str] = mapped_column(String(600), nullable=True, comment='参数取值')
    parm_type_cd: Mapped[str] = mapped_column(String(10), nullable=True, comment='参数类型代码')
    parm_clob_val: Mapped[str] = mapped_column(Text, nullable=True, comment='参数长文本')

    __table_args__ = (
        PrimaryKeyConstraint('id', 'parm_cd', 'parm_sn'),
    )

    @staticmethod
    def generate_tech_parm_po(tech_parm_context):
        return TechParm(
            id=tech_parm_context.get("id"),
            parm_cd=tech_parm_context.get("parm_cd"),
            parm_sn=tech_parm_context.get("parm_sn"),
            parm_nm=tech_parm_context.get("parm_nm"),
            parm_val=tech_parm_context.get("parm_val"),
            parm_type_cd=tech_parm_context.get("parm_type_cd"),
            parm_clob_val=tech_parm_context.get("parm_clob_val"),
        )

    def to_dict(self):
        return {
            "id": self.id,
            "parm_cd": self.parm_cd,
            "parm_sn": self.parm_sn,
            "parm_nm": self.parm_nm,
            "parm_val": self.parm_val,
            "parm_type_cd": self.parm_type_cd,
            "parm_clob_val": self.parm_clob_val,
        }