from dao.dos.plt import plt_svc_cd_cntl_dos
from common.database.transaction import get_session


def insert(scoped_session, plt_svc_cd_cntl_po):
    plt_svc_cd_cntl_dos.insert(get_session(scoped_session), plt_svc_cd_cntl_po)


def select_by_primary_key(scoped_session, plt_svc_cd_cntl_po):
    result = plt_svc_cd_cntl_dos.select_by_primary_key(get_session(scoped_session), plt_svc_cd_cntl_po)
    return result
