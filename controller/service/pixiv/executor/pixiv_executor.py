from controller.common.executor import Executor


class PixivExecutor(Executor):
    def _initialize_mapping(self):
        """
        :功能描述: 初始化交易码和子码映射关系
        :return: 返回交易码和子码的映射规则
        :Author: Lancelot
        :Date: 2024/12/15 23:33
        """
        return {
            # 交易码 PIXIV01 对应 pixiv_common 模块
            "PIXIV01": {
                "module": "pixiv_common_txn",
                "subcode_mapping": {
                    # 设置Cookie
                    "001": "set_pixiv_cookie",  # 子码001 -> 模块中的函数
                    # 通过pid查询主表数据
                    "002": "get_prim_inf_by_pid",
                    # 通过pid下载
                    "003": "download_by_pid",
                }
            },
        }
