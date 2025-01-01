from dao.service.plt import tech_parm_service
from common.database.transaction import transaction


@transaction
def insert(scoped_session, context):
    try:
        tech_parm_po = context.get("plt.tech_parm_po", "技术参数表实体为空")
        tech_parm_service.insert(scoped_session, tech_parm_po)
    except Exception as e:
        raise e
