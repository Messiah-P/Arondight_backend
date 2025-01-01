from controller.service.plt.component import tech_parm_component
from common.context.context import Context
from dao.models.plt.tech_parm_model import TechParm
from dao.service.plt import tech_parm_service


async def insert(initializer, entity):
    try:
        tech_parm_context = Context()
        tech_parm_context.set("id", entity.get("id"))
        tech_parm_context.set("parm_cd", entity.get("parm_cd"))
        tech_parm_context.set("parm_sn", entity.get("parm_sn"))
        tech_parm_context.set("parm_nm", entity.get("parm_nm"))
        tech_parm_context.set("parm_val", entity.get("parm_val"))
        tech_parm_context.set("parm_type_cd", entity.get("parm_type_cd"))
        tech_parm_context.set("parm_clob_val", entity.get("parm_clob_val"))
        tech_parm_po = TechParm.generate_tech_parm_po(tech_parm_context)

        context = Context()
        context.set("plt.tech_parm_po", tech_parm_po)
        tech_parm_component.insert(initializer.scoped_session, tech_parm_po)
        return "000", "交易成功", None
    except Exception as e:
        return "022", "交易失败", f"错误原因：{e}"


async def select_by_primary_key(initializer, entity):
    tech_parm_context = Context()
    tech_parm_context.set("id", entity.get("id"))
    tech_parm_context.set("parm_cd", entity.get("parm_cd"))
    tech_parm_context.set("parm_sn", entity.get("parm_sn"))
    tech_parm_po = TechParm.generate_tech_parm_po(tech_parm_context)
    result = tech_parm_service.select_by_primary_key(initializer.scoped_session, tech_parm_po)

    resp_code = "000"
    resp_desc = "交易成功"
    entity = result.to_dict()
    return resp_code, resp_desc, entity
