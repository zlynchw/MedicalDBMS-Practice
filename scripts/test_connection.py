#!/usr/bin/env python3
"""
数据库连接测试脚本
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
import database.db_config
import database.db_connection
import database.medical_dao
import database.connection_pool
DatabaseConfig = database.db_config.DatabaseConfig
BaseConnection = database.db_connection.BaseConnection
MedicalDAO = database.medical_dao.MedicalDAO
get_connection_pool = database.connection_pool.get_connection_pool

def test_connection():
    """测试数据库连接"""
    print("🧪 测试数据库连接...")
    print("-" * 40)

    # 方法1：使用默认配置
    print("1. 使用默认配置连接:")
    try:
        db = BaseConnection()
        db.connect()

        if db.ping():
            print("   ✅ 连接成功!")
        else:
            print("   ❌ 连接失败")
            return False

        # 测试查询
        tables = db.get_tables()
        print(f"   📊 数据库表数量: {len(tables)}")

        for table in tables:
            count = db.count(table)
            print(f"   📈 {table}: {count} 行")

        db.close()
        print("   ✅ 连接关闭正常")

    except Exception as e:
        print(f"   ❌ 连接失败: {e}")
        return False

    # 方法2：使用自定义配置
    print("\n2. 使用自定义配置连接:")
    try:
        config = DatabaseConfig(
            host="localhost",
            user="med_user",
            password="Medical@2024",
            database="medical_db"
        )

        db = BaseConnection(config)
        db.connect()

        if db.ping():
            print("   ✅ 连接成功!")
        else:
            print("   ❌ 连接失败")
            return False

        # 测试复杂查询
        sql = """
        SELECT 
            (SELECT COUNT(*) FROM patients) as patient_count,
            (SELECT COUNT(*) FROM doctors) as doctor_count,
            (SELECT COUNT(*) FROM medical_visits) as visit_count,
            (SELECT COUNT(*) FROM examination_records) as exam_count
        """

        result = db.execute(sql, fetch_one=True)
        if result:
            print("   📈 数据统计:")
            print(f"      患者: {result['patient_count']} 人")
            print(f"      医生: {result['doctor_count']} 人")
            print(f"      就诊: {result['visit_count']} 次")
            print(f"      检查: {result['exam_count']} 次")

        db.close()
        print("   ✅ 连接关闭正常")

    except Exception as e:
        print(f"   ❌ 连接失败: {e}")
        return False

    # 方法3：测试事务
    print("\n3. 测试事务功能:")
    try:
        db = BaseConnection()
        db.connect()

        with db.transaction():
            # 获取当前最大ID
            sql = "SELECT MAX(patient_id) as max_id FROM patients"
            result = db.execute(sql, fetch_one=True)
            max_id = result.get("max_id", 0) if result else 0

            print(f"   当前最大患者ID: {max_id}")
            print("   ✅ 事务测试通过")

        db.close()

    except Exception as e:
        print(f"   ❌ 事务测试失败: {e}")
        return False

    print("\n" + "=" * 40)
    print("🎉 所有测试通过！")
    print("=" * 40)
    return True


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)