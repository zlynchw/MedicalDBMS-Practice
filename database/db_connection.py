# db_connection.py
"""
数据库连接基类
"""

import pymysql
import logging
from typing import Optional, List, Dict, Any
import os

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class BaseConnection:
    """数据库连接基类"""

    def __init__(self, config_file: str = None):
        """
        初始化数据库连接

        Args:
            config_file: 配置文件路径
        """
        # 设置日志
        self.logger = logging.getLogger(self.__class__.__name__)

        # 数据库配置
        self.config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'med_user',
            'password': 'MedsAlpha',
            'database': 'medical_db',
            'charset': 'utf8mb4'
        }

        # 如果有配置文件，从配置文件加载
        if config_file and os.path.exists(config_file):
            self._load_config(config_file)

        self.connection = None

    def _load_config(self, config_file: str):
        """从配置文件加载配置"""
        try:
            import configparser
            config = configparser.ConfigParser()
            config.read(config_file)

            if 'database' in config:
                db_config = config['database']
                self.config.update({
                    'host': db_config.get('host', 'localhost'),
                    'port': int(db_config.get('port', 3306)),
                    'user': db_config.get('user', 'root'),
                    'password': db_config.get('password', ''),
                    'database': db_config.get('database', 'medical_db'),
                    'charset': db_config.get('charset', 'utf8mb4')
                })
        except Exception as e:
            self.logger.warning(f"加载配置文件失败: {e}")

    def connect(self) -> bool:
        """连接数据库"""
        try:
            self.connection = pymysql.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database'],
                charset=self.config['charset'],
                cursorclass=pymysql.cursors.DictCursor
            )

            self.logger.info("数据库连接成功")
            return True

        except pymysql.Error as e:
            self.logger.error(f"数据库连接失败: {e}")
            self.connection = None
            return False

    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.logger.info("数据库连接已关闭")
            self.connection = None

    def execute(self, sql: str, params=None, fetch_all=False,
                fetch_one=False, commit=False) -> Optional[Any]:
        """
        执行SQL查询

        Args:
            sql: SQL语句
            params: 参数
            fetch_all: 是否获取所有结果
            fetch_one: 是否获取单个结果
            commit: 是否提交事务

        Returns:
            查询结果
        """
        if not self.connection:
            self.logger.error("数据库未连接")
            return None

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, params)

                if fetch_all:
                    result = cursor.fetchall()
                elif fetch_one:
                    result = cursor.fetchone()
                else:
                    result = None

                if commit:
                    self.connection.commit()

                return result

        except pymysql.Error as e:
            self.logger.error(f"执行SQL时发生错误: {e}")
            if self.connection:
                self.connection.rollback()
            return None
        except Exception as e:
            self.logger.error(f"执行SQL时发生未知错误: {e}")
            return None

    def execute_many(self, sql: str, params_list: List) -> bool:
        """执行批量插入/更新"""
        if not self.connection:
            self.logger.error("数据库未连接")
            return False

        try:
            with self.connection.cursor() as cursor:
                cursor.executemany(sql, params_list)
                self.connection.commit()
                return True

        except pymysql.Error as e:
            self.logger.error(f"批量执行SQL时发生错误: {e}")
            if self.connection:
                self.connection.rollback()
            return False

    def get_cursor(self):
        """获取游标"""
        if not self.connection:
            self.connect()

        if self.connection:
            return self.connection.cursor()
        return None

    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self.connection is not None

    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            self.connect()
            if self.connection:
                with self.connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    return result is not None
            return False
        except Exception as e:
            self.logger.error(f"测试连接失败: {e}")
            return False
        finally:
            self.close()


# 单例模式
_db_instance = None

def get_db_connection(config_file: str = None) -> BaseConnection:
    """获取数据库连接实例（单例）"""
    global _db_instance
    if _db_instance is None:
        _db_instance = BaseConnection(config_file)
    return _db_instance


if __name__ == "__main__":
    # 测试数据库连接
    db = BaseConnection()
    if db.test_connection():
        print("✅ 数据库连接测试成功")
    else:
        print("❌ 数据库连接测试失败")