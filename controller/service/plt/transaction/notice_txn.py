from common.context.context import Context
from dao.models.plt.tech_parm_model import TechParm
from dao.service.plt import tech_parm_service
from common.notice.bark import Bark


async def set_notice_bark(initializer, entity):
    # 获取notice参数
    tech_parm_context = Context()
    tech_parm_context.set("id", 0)
    tech_parm_context.set("parm_sn", 0)
    tech_parm_po = TechParm.generate_tech_parm_po(tech_parm_context)
    notice_parms = tech_parm_service.get_notice_parms(initializer.scoped_session, tech_parm_po)
    initializer.context.set("config.notice_parms", notice_parms)

    bark = Bark(bark_url=notice_parms.get("link_bark"),
                pic_url=notice_parms.get("arondight_logo"),
                title="Arondight",
                group="Arondight")
    initializer.notifier = bark
    return "000", "交易成功", initializer.context.get("config.notice_parms")


async def get_notice_parms(initializer, entity):
    try:
        notice_parms = initializer.context.get("config.notice_parms", "通知器参数不存在。")
        return "000", "交易成功", notice_parms
    except Exception as e:
        return "022", f"{e}", None
