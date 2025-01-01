"""
* 功能描述: 操作TECH_PARM表
* @fileName: tech_parm_dos.py
* @Author: Messiah
* @Date: 2024/11/10
"""
from sqlalchemy import MetaData, text

from dao.models.plt.tech_parm_model import TechParm

metadata = MetaData()


def insert(session, tech_parm_po: TechParm):
    tech_parm = TechParm(id=tech_parm_po.id,
                         parm_cd=tech_parm_po.parm_cd,
                         parm_sn=tech_parm_po.parm_sn,
                         parm_nm=tech_parm_po.parm_nm,
                         parm_val=tech_parm_po.parm_val,
                         parm_type_cd=tech_parm_po.parm_type_cd,
                         parm_clob_val=tech_parm_po.parm_clob_val)
    session.add(tech_parm)
    return tech_parm


def select_by_primary_key(session, tech_parm_po: TechParm):
    parameters = {"id": tech_parm_po.id,
                  "parm_cd": tech_parm_po.parm_cd,
                  "parm_sn": tech_parm_po.parm_sn}

    sql = (f"SELECT * "
           f"FROM tech_parm "
           f"WHERE id = :id "
           f"AND parm_cd = :parm_cd "
           f"AND parm_sn = :parm_sn ")

    return session.execute(text(sql), parameters).one_or_none()
