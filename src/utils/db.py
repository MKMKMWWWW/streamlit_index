import pymysql
from sqlalchemy import create_engine
import pandas as pd

class DatabaseConnection:
    def __init__(self, config):
        self.config = config["database"]
        self.connection = None
        self.engine = None
        
    def connect(self):
        """创建数据库连接"""
        if not self.connection:
            self.connection = pymysql.connect(
                host=self.config["host"],
                port=self.config["port"],
                user=self.config["user"],
                password=self.config["password"],
                database=self.config["database"],
                charset='utf8mb4'
            )
        return self.connection
    
    def get_engine(self):
        """获取SQLAlchemy引擎，用于pandas读取"""
        if not self.engine:
            connection_string = (
                f'mysql+pymysql://{self.config["user"]}:{self.config["password"]}'
                f'@{self.config["host"]}:{self.config["port"]}/{self.config["database"]}'
            )
            self.engine = create_engine(connection_string)
        return self.engine
    
    def query_to_df(self, sql):
        """执行SQL查询并返回DataFrame"""
        try:
            return pd.read_sql(sql, self.get_engine())
        except Exception as e:
            print(f"查询出错: {e}")
            return None
    
    def execute_query(self, sql):
        """执行SQL查询"""
        try:
            with self.connect().cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchall()
        except Exception as e:
            print(f"查询出错: {e}")
            return None
        
    def close(self):
        """关闭连接"""
        if self.connection:
            self.connection.close()
            self.connection = None 