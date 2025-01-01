from controller.common.initializer import Initializer


# 创建一个依赖项，用于注入 Initializer 实例
def get_initializer() -> Initializer:
    # 可以在这里添加初始化器的其他配置
    return Initializer()
