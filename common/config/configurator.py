"""
* 功能描述: 加载配置
* @fileName: configurator.py
* @Author: Lancelot
* @Date: 2024/10/28 17:13
"""
import json
import yaml
from pathlib import Path
from common.log.log_manager import logger


class Configurator:
    def __init__(self, config_path, config_file_name):
        self.config = None
        self.config_path = config_path
        self.config_file_name = config_file_name

    def load_yml(self):
        # 读取YAML文件
        full_config_file_path = Path(self.config_path) / self.config_file_name
        if not full_config_file_path.exists() or not full_config_file_path.read_text(encoding="utf-8").strip():
            logger.error(f"配置文件不存在或为空：{full_config_file_path.name}。")
        else:
            # 使用正确的编码读取 YAML 文件
            logger.info(f"加载配置文件：{full_config_file_path.name}。")
            with full_config_file_path.open('r', encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
                logger.debug(f"配置文件：\n {json.dumps(self.config, indent=4)}")
                logger.success(f"加载配置文件成功！")
            return self.config
