from functools import wraps

from sqlalchemy.orm import Session


# 事务装饰器
def transaction(func):
    @wraps(func)
    def wrapper(self, scoped_session, *args, **kwargs):
        session = scoped_session()  # 创建一个新的会话
        try:
            result = func(self, session, *args, **kwargs)  # 传递session给被装饰的函数
            session.commit()  # 如果一切成功，提交事务
            return result
        except Exception as e:
            session.rollback()  # 如果发生异常，回滚事务
            raise e
        finally:
            session.close()  # 关闭会话

    return wrapper


def get_session(scoped_session):
    """
    :功能描述: 判断传入的 scoped_session 是否已经是会话对象，如果是会话对象直接返回，如果是 scoped_session 工厂则创建一个新的会话对象。
    :Author: Lancelot
    :Date: 2024/12/28 22:03
    """
    # 如果 scoped_session 是一个会话对象（Session 实例），直接返回
    if isinstance(scoped_session, Session):
        return scoped_session
    # 如果 scoped_session 是 scoped_session 的工厂函数（即作用域管理器），调用它获取会话对象
    elif callable(scoped_session):
        return scoped_session()
    # 如果 scoped_session 既不是会话对象，也不是工厂函数，抛出异常
    raise TypeError("传入的 scoped_session 既不是会话对象也不是 scoped_session 工厂函数")
