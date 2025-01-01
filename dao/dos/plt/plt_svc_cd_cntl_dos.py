from sqlalchemy import MetaData, text

from dao.models.plt.plt_svc_cd_cntl_model import PltSvcCdCntl

metadata = MetaData()


def insert(session, plt_svc_cd_cntl_po: PltSvcCdCntl):
    plt_svc_cd_cntl = PltSvcCdCntl(svc_cd=plt_svc_cd_cntl_po.svc_cd,
                                   svc_cd_nm=plt_svc_cd_cntl_po.svc_cd_nm,
                                   svc_cd_stcd=plt_svc_cd_cntl_po.svc_cd_stcd,
                                   )
    session.add(plt_svc_cd_cntl)
    return plt_svc_cd_cntl


def select_by_primary_key(session, plt_svc_cd_cntl_po: PltSvcCdCntl):
    parameters = {"svc_cd": plt_svc_cd_cntl_po.svc_cd}

    sql = (f"SELECT * "
           f"FROM plt_svc_cd_cntl "
           f"WHERE svc_cd = :svc_cd ")

    return session.execute(text(sql), parameters).one_or_none()
