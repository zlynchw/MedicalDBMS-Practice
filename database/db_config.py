"""
数据库配置文件
"""

import os
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """数据库配置类"""
    host: str = "localhost"
    port: int = 3306
    user: str = "med_user"
    password: str = "MedsAlpha"
    database: str = "medical_db"
    charset: str = "utf8mb4"
    pool_size: int = 5
    pool_recycle: int = 3600
    connect_timeout: int = 10

    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """从环境变量创建配置"""
        return cls(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "med_user"),
            password=os.getenv("DB_PASSWORD", "Medical@2024"),
            database=os.getenv("DB_NAME", "medical_db"),
            charset=os.getenv("DB_CHARSET", "utf8mb4"),
            pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
            pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "3600")),
            connect_timeout=int(os.getenv("DB_CONNECT_TIMEOUT", "10"))
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
            "database": self.database,
            "charset": self.charset
        }

    def to_uri(self) -> str:
        """转换为连接URI"""
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?charset={self.charset}"


# 默认配置
DEFAULT_CONFIG = DatabaseConfig()