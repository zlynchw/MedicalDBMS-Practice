"""
数据库连接池管理器
"""

import pymysql
from pymysql import cursors
from queue import Queue, Empty
from threading import Lock
import time
from typing import Dict
import logging
from contextlib import contextmanager
from .db_config import DatabaseConfig, DEFAULT_CONFIG

logger = logging.getLogger(__name__)


class ConnectionPool:
    """数据库连接池"""

    def __init__(self, config: DatabaseConfig, max_size: int = 10):
        """
        初始化连接池

        Args:
            config: 数据库配置
            max_size: 最大连接数
        """
        self.config = config
        self.max_size = max_size
        self._pool = Queue(maxsize=max_size)
        self._active_connections = 0
        self._lock = Lock()

        # 初始化连接池
        self._initialize_pool()

    def _initialize_pool(self) -> None:
        """初始化连接池"""
        initial_size = min(3, self.max_size)

        for _ in range(initial_size):
            try:
                conn = self._create_connection()
                self._pool.put(conn)
            except Exception as e:
                logger.error(f"初始化连接池失败: {e}")

    def _create_connection(self) -> pymysql.Connection:
        """创建新连接"""
        return pymysql.connect(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            password=self.config.password,
            database=self.config.database,
            charset=self.config.charset,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )

    def get_connection(self, timeout: float = 5.0) -> pymysql.Connection:
        """
        从连接池获取连接

        Args:
            timeout: 超时时间（秒）

        Returns:
            数据库连接

        Raises:
            TimeoutError: 获取连接超时
        """
        with self._lock:
            if not self._pool.empty():
                try:
                    conn = self._pool.get(timeout=1)
                    self._active_connections += 1
                    return conn
                except Empty:
                    pass

            # 如果没有可用连接但可以创建新连接
            if self._active_connections < self.max_size:
                try:
                    conn = self._create_connection()
                    self._active_connections += 1
                    return conn
                except Exception as e:
                    logger.error(f"创建新连接失败: {e}")
                    raise ConnectionError(f"无法创建数据库连接: {e}")

            # 等待连接释放
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    conn = self._pool.get(timeout=0.1)
                    self._active_connections += 1
                    return conn
                except Empty:
                    continue

            raise TimeoutError("获取数据库连接超时")

    def return_connection(self, conn: pymysql.Connection) -> None:
        """
        归还连接到连接池

        Args:
            conn: 数据库连接
        """
        with self._lock:
            if conn.open:
                try:
                    # 检查连接是否仍然有效
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT 1")
                except Exception:
                    # 连接已失效，创建新的代替
                    try:
                        conn = self._create_connection()
                    except Exception as e:
                        logger.error(f"创建替换连接失败: {e}")
                        self._active_connections -= 1
                        return

                self._pool.put(conn)
            else:
                self._active_connections -= 1

    def close_all(self) -> None:
        """关闭所有连接"""
        with self._lock:
            while not self._pool.empty():
                try:
                    conn = self._pool.get_nowait()
                    if conn.open:
                        conn.close()
                except Empty:
                    break

            self._active_connections = 0

    def stats(self) -> Dict:
        """获取连接池统计信息"""
        with self._lock:
            return {
                "pool_size": self._pool.qsize(),
                "max_size": self.max_size,
                "active_connections": self._active_connections,
                "available_connections": self._pool.qsize(),
                "used_percentage": (self._active_connections / self.max_size) * 100
            }

    @contextmanager
    def connection(self, timeout: float = 5.0):
        """
        连接上下文管理器

        Args:
            timeout: 超时时间

        Yields:
            数据库连接
        """
        conn = None
        try:
            conn = self.get_connection(timeout)
            yield conn
        finally:
            if conn:
                self.return_connection(conn)


# 全局连接池实例
_pool_instance = None
_pool_lock = Lock()


def get_connection_pool(config: DatabaseConfig = None, max_size: int = 10) -> ConnectionPool:
    """
    获取全局连接池实例（单例模式）

    Args:
        config: 数据库配置
        max_size: 最大连接数

    Returns:
        连接池实例
    """
    global _pool_instance

    with _pool_lock:
        if _pool_instance is None:
            if config is None:
                config = DEFAULT_CONFIG
            _pool_instance = ConnectionPool(config, max_size)

        return _pool_instance