import json

from dao.models.pixiv.pixiv_prim_tag_model import PixivPrimTag
from dao.models.pixiv.pixiv_tag_model import PixivTag
from dao.models.plt.plt_svc_cd_cntl_model import PltSvcCdCntl
from plugin.PixivAide.scheduler import Scheduler
from dao.models.plt.tech_parm_model import TechParm
from dao.service.plt import tech_parm_service
from common.constants.file_constant import FileConstant
from common.file.file_manager import FileManager
from common.log.log_manager import LogManager
from common.log.log_manager import logger
from common.config.configurator import Configurator
from common.database.db_connector import DbConnector
from common.context.context import Context
from common.notice.bark import Bark
from dao.models.pixiv.pixiv_user_model import PixivUser
from dao.models.pixiv.pixiv_prim_model import PixivPrim
from dao.models.pixiv.pixiv_rank_model import PixivRank
from dao.models.pixiv.pixiv_dwld_info_model import PixivDwldInfo

if __name__ == '__main__':
    file_manager = FileManager()

    # 1. 初始化日志
    abs_log_path = file_manager.generate_abs_file_path(FileConstant.LOG_PATH)
    LogManager("pixiv_aide", level="DEBUG", log_path=None)
    logger.success(f"1. 初始化日志成功!：{logger}")

    # 2. 加载初始配置文件
    abs_config_path = file_manager.generate_abs_file_path('plugin/PixivAide/config')
    configurator = Configurator(config_path=abs_config_path, config_file_name="config.yml")
    config = json.loads(json.dumps(configurator.load_yml()), object_hook=Context)
    logger.success(f"2. 加载初始配置文件成功!")

    # 3. 读取数据库配置
    db_connector = DbConnector(database=config.get("database"))
    ScopedSession = db_connector.ScopedSession
    logger.success(f"3. 连接数据库成功!")
    # 建表
    db_connector.create_table(TechParm)
    db_connector.create_table(PltSvcCdCntl)
    db_connector.create_table(PixivUser)
    db_connector.create_table(PixivPrim)
    db_connector.create_table(PixivTag)
    db_connector.create_table(PixivPrimTag)
    db_connector.create_table(PixivRank)
    db_connector.create_table(PixivDwldInfo)
    # 获取notice参数
    tech_parm_context = Context()
    tech_parm_context.set("id", 0)
    tech_parm_context.set("parm_sn", 0)
    tech_parm_po = TechParm.generate_tech_parm_po(tech_parm_context)
    notice_parms = tech_parm_service.get_notice_parms(ScopedSession, tech_parm_po)
    config.set("notice_parms", notice_parms)
    # 获取cookies参数
    tech_parm_context.set("id", 1)
    tech_parm_context.set("parm_cd", "cookies")
    tech_parm_context.set("parm_sn", 0)
    tech_parm_po = TechParm.generate_tech_parm_po(tech_parm_context)
    cookies = tech_parm_service.get_cookies(ScopedSession, tech_parm_po)
    config.set("cookies", cookies)

    # 4. 生成配置
    config.set("config", config)
    logger.debug(f"生成配置：\n {config}")
    logger.success(f"4. 生成配置文件成功!")

    # Bark通知
    bark = Bark(bark_url=config.get("config.notice_parms.link_bark"),
                pic_url=config.get("config.notice_parms.arondight_logo"))
    bark.notice(title="PixivAide启动！", group="PixivAide", message=f"插件PixivAide启动。")
    s = Scheduler(context=config)
    s.run(ScopedSession)
