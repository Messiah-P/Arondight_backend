from dao.dos.plt import tech_parm_dos
from common.database.transaction import get_session


def insert(scoped_session, tech_parm_po):
    tech_parm_dos.insert(get_session(scoped_session), tech_parm_po)

def select_by_primary_key(scoped_session, tech_parm_po):
    result = tech_parm_dos.select_by_primary_key(get_session(scoped_session), tech_parm_po)
    return result

def get_notice_parms(scoped_session, tech_parm_po):
    """
    * 功能描述: 获取notice参数
    * @fileName: tech_parm_service.py
    * @Author: Messiah
    * @Date: 2024/11/20
    """
    tech_parm_po.parm_cd = "link_bark"
    link_bark = tech_parm_dos.select_by_primary_key(get_session(scoped_session), tech_parm_po).parm_val
    tech_parm_po.parm_cd = "arondight_logo"
    arondight_logo = tech_parm_dos.select_by_primary_key(get_session(scoped_session), tech_parm_po).parm_val
    return {
        "link_bark": link_bark,
        "arondight_logo": arondight_logo
    }


def get_cookies(scoped_session, tech_parm_po):
    """
    * 功能描述: 获取cookies
    * @fileName: tech_parm_service.py
    * @Author: Messiah
    * @Date: 2024/11/20
    """
    cookies = tech_parm_dos.select_by_primary_key(get_session(scoped_session), tech_parm_po).parm_clob_val
    return cookies.split(',')
