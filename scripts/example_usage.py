"""
数据库连接程序使用示例
"""

import sys
import os
from datetime import datetime, date, timedelta
import json

# 添加模块路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
import database.db_config
import database.db_connection
import database.medical_dao
import database.connection_pool
DatabaseConfig = database.db_config.DatabaseConfig
BaseConnection = database.db_connection.BaseConnection
MedicalDAO = database.medical_dao.MedicalDAO
get_connection_pool = database.connection_pool.get_connection_pool

def example_base_connection():
    """基础连接使用示例"""
    print("=" * 60)
    print("基础数据库连接示例")
    print("=" * 60)

    # 创建连接
    db = BaseConnection()

    try:
        # 连接数据库
        db.connect()
        print("✅ 数据库连接成功")

        # 测试连接
        if db.ping():
            print("✅ 数据库ping测试成功")

        # 查询表数量
        tables = db.get_tables()
        print(f"✅ 数据库中有 {len(tables)} 个表: {', '.join(tables)}")

        # 查询患者数量
        patient_count = db.count("patients")
        print(f"✅ 患者表中有 {patient_count} 条记录")

        # 查询前5个患者
        print("\n📋 前5个患者:")
        patients = db.select("patients", limit=5)
        for patient in patients:
            print(f"  {patient['patient_id']}: {patient['name']} ({patient['gender']}, {patient['blood_type']}型)")

        # 使用事务
        print("\n💾 事务示例:")
        try:
            with db.transaction():
                # 插入新患者
                new_patient = {
                    "name": "测试患者",
                    "gender": "男",
                    "birth_date": date(1990, 1, 1),
                    "phone": "13800138000",
                    "id_card": "110101199001011234",
                    "address": "测试地址",
                    "blood_type": "A",
                    "allergies": "无",
                    "created_at": datetime.now()
                }

                patient_id = db.insert("patients", new_patient)
                print(f"  ✅ 插入患者成功，ID: {patient_id}")

                # 模拟错误，测试回滚
                # raise Exception("模拟错误")

                # 更新患者
                update_data = {
                    "address": "更新后的地址",
                    "updated_at": datetime.now()
                }
                db.update("patients", update_data, "patient_id = %s", (patient_id,))
                print("  ✅ 更新患者成功")

            print("  ✅ 事务提交成功")

        except Exception as e:
            print(f"  ❌ 事务执行失败: {e}")

        # 执行复杂查询
        print("\n🔍 复杂查询示例:")
        sql = """
        SELECT 
            p.name as patient_name,
            COUNT(mv.visit_id) as visit_count,
            AVG(mv.fee_amount) as avg_fee
        FROM patients p
        LEFT JOIN medical_visits mv ON p.patient_id = mv.patient_id
        GROUP BY p.patient_id, p.name
        HAVING visit_count > 0
        ORDER BY visit_count DESC
        LIMIT 5
        """

        with db.get_cursor() as cursor:
            cursor.execute(sql)
            results = cursor.fetchall()
            for row in results:
                print(f"  {row['patient_name']}: 就诊{row['visit_count']}次，平均费用¥{row['avg_fee']:.2f}")

        # 备份表
        print("\n💾 备份表示例:")
        backup_table = db.backup_table("patients")
        print(f"  ✅ 患者表已备份到: {backup_table}")

        # 获取表结构
        print("\n📊 患者表结构:")
        columns = db.table_info("patients")
        for col in columns:
            print(f"  {col['Field']}: {col['Type']} ({col['Null']})")

    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        # 关闭连接
        db.close()
        print("\n✅ 数据库连接已关闭")


def example_medical_dao():
    """医疗DAO使用示例"""
    print("\n" + "=" * 60)
    print("医疗DAO使用示例")
    print("=" * 60)

    dao = MedicalDAO()

    try:
        # 连接数据库
        dao.connect()

        # 搜索患者
        print("🔍 搜索患者:")
        patients, total = dao.search_patients(keyword="张", page=1, page_size=5)
        print(f"  找到 {total} 个患者，显示前 {len(patients)} 个:")
        for patient in patients:
            print(f"  {patient['patient_id']}: {patient['name']} ({patient['phone']})")

        # 获取医生信息
        print("\n👨‍⚕️ 医生信息:")
        doctor = dao.get_doctor_by_id(1)
        if doctor:
            print(f"  {doctor['name']} - {doctor['title']}")
            print(f"  科室: {doctor.get('department_name', '未知')}")
            print(f"  医院: {doctor.get('hospital_name', '未知')}")

        # 获取医生就诊记录
        print("\n📅 医生今日就诊记录:")
        visits, total = dao.get_doctor_visits(doctor_id=1, visit_date=date.today())
        print(f"  今日共有 {total} 个就诊:")
        for visit in visits[:3]:  # 只显示前3个
            print(f"  {visit['visit_time']}: {visit['patient_name']} - {visit.get('diagnosis', '未诊断')}")

        # 获取患者就诊历史
        print("\n📋 患者就诊历史:")
        patient_id = 1
        visits, total = dao.get_patient_visits(patient_id, page=1, page_size=3)
        print(f"  患者共有 {total} 次就诊，最近 {len(visits)} 次:")
        for visit in visits:
            print(
                f"  {visit['visit_date']}: {visit.get('doctor_name', '未知医生')} - {visit.get('diagnosis', '未诊断')}")

        # 获取检查记录
        print("\n🔬 患者检查记录:")
        exams, total = dao.get_patient_examinations(patient_id, page=1, page_size=3)
        print(f"  患者共有 {total} 次检查，最近 {len(exams)} 次:")
        for exam in exams:
            status = "异常" if exam.get('abnormal_flag') else "正常"
            print(
                f"  {exam['exam_date']}: {exam.get('item_name', '未知项目')} - {exam.get('result_value', '无结果')} ({status})")

        # 获取统计信息
        print("\n📊 今日统计:")
        today_stats = dao.get_daily_statistics()
        print(f"  就诊统计: {json.dumps(today_stats.get('visit_statistics', {}), default=str, indent=2)}")

        # 患者统计
        print("\n📈 患者统计:")
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
        patient_stats = dao.get_patient_statistics(start_date, end_date)
        print(f"  性别分布: {json.dumps(patient_stats.get('gender_distribution', []), default=str, indent=2)}")

        # 收入统计
        print("\n💰 收入统计:")
        revenue_stats = dao.get_revenue_statistics(start_date, end_date)
        total = revenue_stats.get('total_statistics', {})
        print(f"  总收入: ¥{total.get('total_revenue', 0):.2f}")
        print(f"  总就诊: {total.get('total_visits', 0)} 次")
        print(f"  平均费用: ¥{total.get('overall_avg_fee', 0):.2f}")

    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        dao.close()


def example_connection_pool():
    """连接池使用示例"""
    print("\n" + "=" * 60)
    print("连接池使用示例")
    print("=" * 60)

    # 获取连接池
    pool = get_connection_pool(max_size=5)

    # 使用连接池
    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM patients")
            result = cursor.fetchone()
            print(f"✅ 使用连接池查询患者数量: {result['count']}")

    # 获取连接池统计
    stats = pool.stats()
    print(f"📊 连接池统计:")
    print(f"  连接池大小: {stats['pool_size']}/{stats['max_size']}")
    print(f"  活跃连接: {stats['active_connections']}")
    print(f"  使用率: {stats['used_percentage']:.1f}%")

    # 多线程示例
    import threading

    def query_patient(thread_id, pool):
        """多线程查询函数"""
        with pool.connection(timeout=10) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT SLEEP(0.1) as wait, COUNT(*) as count FROM patients")
                result = cursor.fetchone()
                print(f"线程{thread_id}: 查询完成，患者数: {result['count']}")

    print("\n🧵 多线程连接池测试:")
    threads = []
    for i in range(3):
        thread = threading.Thread(target=query_patient, args=(i, pool))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("✅ 所有线程完成")

    # 关闭连接池
    pool.close_all()
    print("✅ 连接池已关闭")


def example_crud_operations():
    """CRUD操作示例"""
    print("\n" + "=" * 60)
    print("完整CRUD操作示例")
    print("=" * 60)

    dao = MedicalDAO()

    try:
        dao.connect()

        # 1. 创建新患者
        print("1. 创建新患者:")
        new_patient = {
            "name": "王小明",
            "gender": "男",
            "birth_date": date(1985, 5, 15),
            "phone": "13912345678",
            "id_card": "110101198505151234",
            "address": "北京市朝阳区",
            "blood_type": "O",
            "allergies": "青霉素过敏",
            "created_at": datetime.now()
        }

        patient_id = dao.create_patient(new_patient)
        print(f"  创建患者成功，ID: {patient_id}")

        # 2. 查询患者
        print("\n2. 查询患者:")
        patient = dao.get_patient_by_id(patient_id)
        if patient:
            print(f"  患者信息: {patient['name']}, 电话: {patient['phone']}")

        # 3. 更新患者
        print("\n3. 更新患者信息:")
        update_success = dao.update_patient(patient_id, {
            "address": "北京市海淀区",
            "updated_at": datetime.now()
        })
        print(f"  更新{'成功' if update_success else '失败'}")

        # 4. 创建就诊记录
        print("\n4. 创建就诊记录:")
        visit_data = {
            "patient_id": patient_id,
            "doctor_id": 1,
            "visit_type": "门诊",
            "symptoms": "头痛、发热",
            "fee_amount": 50.00
        }

        visit_id = dao.create_visit(visit_data)
        print(f"  创建就诊记录成功，ID: {visit_id}")

        # 5. 更新诊断
        print("\n5. 更新诊断:")
        diagnosis_success = dao.update_visit_diagnosis(
            visit_id,
            "上呼吸道感染",
            "多喝水，按时服药"
        )
        print(f"  更新诊断{'成功' if diagnosis_success else '失败'}")

        # 6. 查询就诊记录
        print("\n6. 查询就诊记录:")
        visit = dao.get_visit_by_id(visit_id)
        if visit:
            print(f"  就诊信息: {visit['patient_name']} -> {visit['doctor_name']}")
            print(f"  诊断: {visit.get('diagnosis', '未诊断')}")
            print(f"  费用: ¥{visit.get('fee_amount', 0):.2f}")

        # 7. 创建检查记录
        print("\n7. 创建检查记录:")
        exam_data = {
            "visit_id": visit_id,
            "item_id": 1,  # 假设是血常规检查
            "result_value": "12.5",
            "result_summary": "白细胞计数偏高",
            "abnormal_flag": True
        }

        exam_id = dao.create_examination(exam_data)
        print(f"  创建检查记录成功，ID: {exam_id}")

        # 8. 查询检查记录
        print("\n8. 查询检查记录:")
        exam = dao.get_examination_by_id(exam_id)
        if exam:
            print(f"  检查项目: {exam.get('item_name', '未知')}")
            print(f"  结果: {exam.get('result_value', '无结果')}")
            print(f"  摘要: {exam.get('result_summary', '无')}")
            print(f"  状态: {'异常' if exam.get('abnormal_flag') else '正常'}")

        # 9. 查询患者所有信息
        print("\n9. 患者完整就诊历史:")
        visits, total = dao.get_patient_visits(patient_id)
        print(f"  患者共有 {total} 次就诊记录")

        for i, visit in enumerate(visits[:2], 1):  # 显示前2次
            print(f"\n  第{i}次就诊:")
            print(f"    时间: {visit['visit_date']} {visit.get('visit_time', '')}")
            print(f"    医生: {visit.get('doctor_name', '未知')}")
            print(f"    诊断: {visit.get('diagnosis', '未诊断')}")
            print(f"    科室: {visit.get('department_name', '未知')}")

            # 获取该次就诊的检查记录
            exams = dao.get_visit_examinations(visit['visit_id'])
            if exams:
                print(f"    检查项目:")
                for exam in exams:
                    print(f"      - {exam.get('item_name', '未知')}: {exam.get('result_value', '无结果')}")

        # 10. 删除测试数据
        print("\n10. 清理测试数据:")

        # 先删除检查记录
        dao.delete("examination_records", "visit_id = %s", (visit_id,))
        print("  ✓ 删除检查记录")

        # 删除就诊记录
        dao.delete("medical_visits", "patient_id = %s", (patient_id,))
        print("  ✓ 删除就诊记录")

        # 删除患者
        dao.delete("patients", "patient_id = %s", (patient_id,))
        print(f"  ✓ 删除患者 ID: {patient_id}")

        print("\n✅ CRUD操作示例完成")

    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        dao.close()


def main():
    """主函数"""
    print("医疗数据库连接程序示例")
    print("=" * 60)

    # 运行示例
    example_base_connection()
    example_medical_dao()
    example_connection_pool()
    example_crud_operations()

    print("\n" + "=" * 60)
    print("✅ 所有示例完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()