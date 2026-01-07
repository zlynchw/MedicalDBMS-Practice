"""
数据验证脚本
验证模拟数据是否成功生成
"""

import pymysql
from pymysql import cursors
import sys

def verify_data():
    """验证数据完整性"""
    db_config = {
        'host': 'localhost',
        'user': 'med_user',
        'password': 'MedsAlpha',
        'database': 'medical_db',
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }

    try:
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()

        print("=" * 60)
        print("医疗数据库数据验证报告")
        print("=" * 60)

        # 1. 基本数据量验证
        tables = [
            'users', 'patients', 'hospitals', 'departments',
            'doctors', 'examination_items', 'medical_visits',
            'examination_records'
        ]

        print("\n📊 1. 各表数据量统计:")
        print("-" * 40)

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            result = cursor.fetchone()
            print(f"{table:20} | {result['count']:6d} 行")

        # 2. 关键业务数据验证
        print("\n🔍 2. 业务数据验证:")
        print("-" * 40)

        # 验证患者就诊覆盖
        cursor.execute("""
            SELECT 
                COUNT(*) as total_patients,
                COUNT(DISTINCT mv.patient_id) as patients_with_visits,
                ROUND(COUNT(DISTINCT mv.patient_id) * 100.0 / COUNT(*), 1) as coverage_rate
            FROM patients p
            LEFT JOIN medical_visits mv ON p.patient_id = mv.patient_id
        """)
        coverage = cursor.fetchone()
        print(
            f"患者就诊覆盖率: {coverage['coverage_rate']}% ({coverage['patients_with_visits']}/{coverage['total_patients']})")

        # 验证医生有就诊记录
        cursor.execute("""
            SELECT 
                COUNT(*) as total_doctors,
                COUNT(DISTINCT mv.doctor_id) as doctors_with_visits
            FROM doctors d
            LEFT JOIN medical_visits mv ON d.doctor_id = mv.doctor_id
        """)
        doctors = cursor.fetchone()
        print(f"医生就诊参与率: {doctors['doctors_with_visits']}/{doctors['total_doctors']}")

        # 3. 数据质量检查
        print("\n✅ 3. 数据质量检查:")
        print("-" * 40)

        checks = [
            ("患者有EMPI编码", "SELECT COUNT(*) FROM patients WHERE empi_code IS NOT NULL"),
            ("医生有工号", "SELECT COUNT(*) FROM doctors WHERE doctor_number IS NOT NULL"),
            ("检查记录有结果", "SELECT COUNT(*) FROM examination_records WHERE result_summary IS NOT NULL"),
            ("就诊记录有诊断", "SELECT COUNT(*) FROM medical_visits WHERE diagnosis IS NOT NULL"),
        ]

        for check_name, sql in checks:
            cursor.execute(sql)
            result = cursor.fetchone()
            count = list(result.values())[0]
            status = "✓" if count > 0 else "✗"
            print(f"{status} {check_name}: {count}")

        # 4. 查看样本数据
        print("\n👥 4. 数据样本查看:")
        print("-" * 40)

        # 查看一个完整的就诊流程样本
        cursor.execute("""
            SELECT 
                p.name as patient_name,
                p.gender,
                p.blood_type,
                mv.visit_date,
                mv.diagnosis,
                d.name as doctor_name,
                d.title as doctor_title,
                COUNT(er.exam_id) as exam_count
            FROM medical_visits mv
            JOIN patients p ON mv.patient_id = p.patient_id
            JOIN doctors d ON mv.doctor_id = d.doctor_id
            LEFT JOIN examination_records er ON mv.visit_id = er.visit_id
            GROUP BY mv.visit_id
            ORDER BY RAND()
            LIMIT 3
        """)

        print("随机就诊样本:")
        for i, row in enumerate(cursor.fetchall(), 1):
            print(f"\n 样本{i}:")
            print(f"   患者: {row['patient_name']}({row['gender']}, {row['blood_type']}型)")
            print(f"   就诊: {row['visit_date'].strftime('%Y-%m-%d')} - {row['diagnosis']}")
            print(f"   医生: {row['doctor_name']} {row['doctor_title']}")
            print(f"   检查: {row['exam_count']}项")

        print("\n" + "=" * 60)
        print("✅ 数据验证完成！")

    except pymysql.Error as e:
        print(f"❌ 数据库连接错误: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

    return True


if __name__ == "__main__":
    success = verify_data()
    sys.exit(0 if success else 1)