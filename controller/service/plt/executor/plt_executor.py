from controller.common.executor import Executor


class PltExecutor(Executor):
    def _initialize_mapping(self):
        """
        :功能描述: 初始化交易码和子码映射关系
        :return: 返回交易码和子码的映射规则
        :Author: Lancelot
        :Date: 2024/12/15 23:33
        """
        return {
            "PLT01": {
                # 技术参数表相关交易
                "module": "tech_parm_txn",
                "subcode_mapping": {
                    "001": "insert",
                    "002": "select_by_primary_key"
                }
            },
            "PLT02": {
                # 通知器相关交易
                "module": "notice_txn",
                "subcode_mapping": {
                    "001": "set_notice_bark",  # 初始化Bark参数
                    "002": "get_notice_parms",  # 查询通知器参数
                }
            },
        }
