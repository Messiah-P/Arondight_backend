import importlib

from common.context.context import Context
from common.log.log_manager import logger


class Executor:
    def __init__(self, module_base="transaction"):
        """
        初始化 Executor。
        :param module_base: 交易模块的基础包路径
        """
        self.module_base = module_base
        self.txn_mapping = self._initialize_mapping()

    def _initialize_mapping(self):
        """
        初始化交易码和子码映射关系。
        :return: 返回交易码和子码的映射规则
        """
        return {}

    async def execute(self, initializer, txn_code, txn_subcode, entity):
        """
        根据交易码和子码执行对应逻辑。
        :param initializer: 初始化器
        :param txn_code: 交易码
        :param txn_subcode: 交易子码
        :param entity: 请求体数据
        :return: 子码函数的返回结果
        """
        try:
            # 获取交易码的映射信息
            txn_info = self.txn_mapping.get(txn_code)
            if not txn_info:
                logger.error(f"交易码 {txn_code} 无对应模块")
                raise ValueError(f"交易码 {txn_code} 无对应模块")

            module_name = txn_info["module"]
            subcode_mapping = txn_info["subcode_mapping"]

            # 检查子码是否存在
            func_name = subcode_mapping.get(txn_subcode)
            if not func_name:
                logger.error(f"交易码 {txn_code} 的子码 {txn_subcode} 未定义")
                raise ValueError(f"交易码 {txn_code} 的子码 {txn_subcode} 未定义")

            # 动态加载模块
            full_module_name = f"{self.module_base}.{module_name}"
            module = importlib.import_module(full_module_name)

            # 检查函数是否存在
            if not hasattr(module, func_name):
                logger.error(f"模块 {module_name} 中未定义函数 {func_name}")
                raise ValueError(f"模块 {module_name} 中未定义函数 {func_name}")
            func = getattr(module, func_name)

            # 转换entity为变量池
            req_entity = Context()
            req_entity.set("arondight.req.entity", entity)

            # 执行对应函数
            logger.info(f"开始执行：{module_name}.{func_name}。")
            return await func(initializer, req_entity)

        except ModuleNotFoundError:
            logger.error(f"交易码 {txn_code} 对应的模块未找到")
            raise ValueError(f"交易码 {txn_code} 对应的模块未找到")
        except Exception as e:
            logger.error(f"交易：{txn_code}-{txn_subcode} 执行出错: {e}")
            raise RuntimeError(f"交易：{txn_code}-{txn_subcode} 执行出错: {e}")
