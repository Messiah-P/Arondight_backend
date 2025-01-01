import json

from controller.constant.arondight_constant import ArondightConstant
from common.constants.file_constant import FileConstant
from dao.models.pixiv.pixiv_dwld_info_model import PixivDwldInfo
from dao.models.pixiv.pixiv_prim_model import PixivPrim
from dao.models.pixiv.pixiv_prim_tag_model import PixivPrimTag
from dao.models.pixiv.pixiv_rank_model import PixivRank
from dao.models.pixiv.pixiv_tag_model import PixivTag
from dao.models.pixiv.pixiv_user_model import PixivUser
from common.config.configurator import Configurator
from common.context.context import Context
from common.database.db_connector import DbConnector
from dao.models.plt.plt_svc_cd_cntl_model import PltSvcCdCntl
from dao.models.plt.tech_parm_model import TechParm
from common.file.file_manager import FileManager
from common.log.log_manager import logger, LogManager


class Initializer(object):
    _instance = None  # 用于保存唯一实例

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            logger.debug(f"开始初始化。")
            cls._instance = super(Initializer, cls).__new__(cls, *args, **kwargs)
        else:
            logger.debug(f"无需初始化。")
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):  # 确保只初始化一次
            self.context = Context()
            self.scoped_session = None
            self.notifier = None
            self._initialize()
            self.initialized = True  # 标记初始化完成

    def _initialize(self):
        file_manager = FileManager()

        # 1. 初始化日志
        abs_log_path = file_manager.generate_abs_file_path(FileConstant.LOG_PATH)
        LogManager("Arondight", level="INFO", log_path=abs_log_path)
        logger.success(f"1. 初始化日志成功!：{logger}")

        # 2. 加载初始配置文件
        abs_config_path = file_manager.generate_abs_file_path(ArondightConstant.CONFIG_PATH)
        configurator = Configurator(config_path=abs_config_path, config_file_name="config.yml")
        config = json.loads(json.dumps(configurator.load_yml()), object_hook=Context)
        logger.success(f"2. 加载初始配置文件成功!")

        # 3. 读取数据库配置
        db_connector = DbConnector(database=config.get("database"))
        self.scoped_session = db_connector.ScopedSession
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

        # 4. 生成配置
        self.context.set("config", config)
        logger.debug(f"生成配置：\n {config}")
        logger.success(f"4. 生成配置文件成功!")
