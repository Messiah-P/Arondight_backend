"""
* 功能描述: 数据库连接
* @fileName: db_connector.py
* @Author: Messiah
* @Date: 2024/11/30
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from common.log.log_manager import logger

Base = declarative_base()


class DbConnector:
    def __init__(self, database):
        self.database = database
        self.engine = None
        self.ScopedSession = None
        self._create_connection()

    def _create_connection(self):
        user = self.database.get("user")
        password = self.database.get("password")
        host = self.database.get("host")
        port = self.database.get("port")
        database_name = self.database.get("database_name")
        logger.info(f"连接数据库：mysql+pymysql://{user}:{password}@{host}:{port}/{database_name}")

        self.engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database_name}",
                                    max_overflow=10,  # 超过连接池大小外最多创建的连接
                                    pool_size=50,  # 连接池大小
                                    pool_timeout=30,  # 池中没有线程最多等待的时间，否则报错
                                    pool_recycle=3600,  # 多久之后对线程池中的线程进行一次连接的回收（重置）
                                    isolation_level="READ COMMITTED", # 事务只能读取到其他事务已经提交的数据
                                    )
        session_factory = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
        self.ScopedSession = scoped_session(session_factory)

    def create_table(self, table):
        """
        * 功能描述: 建表
        * @fileName: connector.py
        * @Author: Messiah
        * @Date: 2024/11/10
        """
        table.metadata.create_all(self.engine, tables=[table.__table__])

    def drop_table(self, table):
        """
        * 功能描述: 删表
        * @fileName: connector.py
        * @Author: Messiah
        * @Date: 2024/11/10
        """
        table.metadata.drop_all(self.engine, tables=[table.__table__])
