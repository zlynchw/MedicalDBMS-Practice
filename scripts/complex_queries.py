# complex_queries.py
"""
医疗数据库复杂查询示例
包含嵌套查询、分组聚集函数等高级SQL操作
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.db_connection import BaseConnection


class ComplexQueries:
    """复杂查询示例类"""

    def __init__(self):
        self.db = BaseConnection()

    def run_all_queries(self):
        """运行所有复杂查询"""
        try:
            self.db.connect()

            print("=" * 70)
            print("医疗数据库复杂查询示例 (嵌套查询 + 分组聚集函数)")
            print("=" * 70)

            # 1. 嵌套查询
            self.demo_nested_queries()

            # 2. 分组聚集函数
            self.demo_group_by_aggregation()

            # 3. 窗口函数
            self.demo_window_functions()

            # 4. CASE WHEN 条件查询
            self.demo_case_when()

            # 5. 多表连接复杂查询
            self.demo_complex_joins()

            print("\n" + "=" * 70)
            print("✅ 所有复杂查询示例完成")
            print("=" * 70)

        finally:
            self.db.close()

    def demo_nested_queries(self):
        """嵌套查询示例"""
        print("\n" + "-" * 40)
        print("1. 嵌套查询示例")
        print("-" * 40)

        # 示例1: 查找就诊次数超过平均值的患者
        sql1 = """
        -- 嵌套查询: 查找就诊次数超过平均值的患者
        SELECT 
            p.patient_id,
            p.name as patient_name,
            p.gender,
            COUNT(mv.visit_id) as visit_count
        FROM patients p
        JOIN medical_visits mv ON p.patient_id = mv.patient_id
        GROUP BY p.patient_id, p.name, p.gender
        HAVING COUNT(mv.visit_id) > (
            -- 子查询: 计算平均就诊次数
            SELECT AVG(visit_count) 
            FROM (
                SELECT COUNT(visit_id) as visit_count
                FROM medical_visits
                GROUP BY patient_id
            ) as subquery
        )
        ORDER BY visit_count DESC
        LIMIT 10
        """

        print("📊 查询1: 查找就诊次数超过平均值的患者")
        results1 = self.db.execute(sql1, fetch_all=True)
        for row in results1[:5]:
            print(f"  {row['patient_name']}: {row['visit_count']}次就诊")

        # 示例2: 查找每个科室工资最高的医生
        sql2 = """
        -- 嵌套查询: 查找每个科室就诊量最高的医生
        SELECT 
            d.doctor_id,
            d.name as doctor_name,
            d.title,
            dept.dept_name,
            doc_stats.visit_count
        FROM (
            -- 子查询: 计算每个医生的就诊量
            SELECT 
                doctor_id,
                COUNT(visit_id) as visit_count
            FROM medical_visits
            WHERE visit_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY doctor_id
        ) as doc_stats
        JOIN doctors d ON doc_stats.doctor_id = d.doctor_id
        JOIN departments dept ON d.department_id = dept.department_id
        WHERE (d.department_id, doc_stats.visit_count) IN (
            -- 子查询: 查找每个科室的最高就诊量
            SELECT 
                d2.department_id,
                MAX(doc_stats2.visit_count)
            FROM (
                SELECT 
                    doctor_id,
                    COUNT(visit_id) as visit_count
                FROM medical_visits
                WHERE visit_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                GROUP BY doctor_id
            ) as doc_stats2
            JOIN doctors d2 ON doc_stats2.doctor_id = d2.doctor_id
            GROUP BY d2.department_id
        )
        ORDER BY dept.dept_name
        """

        print("\n📊 查询2: 查找每个科室最近30天就诊量最高的医生")
        try:
            results2 = self.db.execute(sql2, fetch_all=True)
            for row in results2:
                print(f"  {row['dept_name']}: {row['doctor_name']} ({row['visit_count']}次)")
        except Exception as e:
            print(f"  注意: 查询可能需要调整表结构: {e}")

    def demo_group_by_aggregation(self):
        """分组聚集函数示例"""
        print("\n" + "-" * 40)
        print("2. 分组聚集函数示例")
        print("-" * 40)

        # 示例1: 按月统计就诊量和收入
        sql1 = """
        SELECT 
            -- 使用DATE_FORMAT进行日期分组，注意使用双百分号
            DATE_FORMAT(visit_date, '%%Y-%%m') as month,
            -- 聚集函数: COUNT, SUM, AVG
            COUNT(*) as total_visits,
            COUNT(DISTINCT patient_id) as unique_patients,
            COUNT(DISTINCT doctor_id) as unique_doctors,
            SUM(total_fee) as total_revenue,
            AVG(total_fee) as avg_fee_per_visit,
            -- 使用MAX, MIN查找极值
            MAX(total_fee) as max_fee,
            MIN(total_fee) as min_fee
        FROM medical_visits
        WHERE visit_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
        GROUP BY DATE_FORMAT(visit_date, '%%Y-%%m')
        ORDER BY month DESC
        """

        print("📊 查询1: 按月统计就诊量和收入")
        results1 = self.db.execute(sql1, fetch_all=True)
        for row in results1:
            print(f"  {row['month']}: {row['total_visits']}次就诊, 收入¥{row.get('total_revenue', 0):.2f}")

        # 示例2: 按年龄段和性别分组统计
        sql2 = """
        SELECT 
            -- 使用CASE WHEN进行分组
            CASE
                WHEN TIMESTAMPDIFF(YEAR, birth_date, CURDATE()) < 18 THEN '<18岁'
                WHEN TIMESTAMPDIFF(YEAR, birth_date, CURDATE()) BETWEEN 18 AND 30 THEN '18-30岁'
                WHEN TIMESTAMPDIFF(YEAR, birth_date, CURDATE()) BETWEEN 31 AND 45 THEN '31-45岁'
                WHEN TIMESTAMPDIFF(YEAR, birth_date, CURDATE()) BETWEEN 46 AND 60 THEN '46-60岁'
                ELSE '>60岁'
            END as age_group,
            gender,
            -- 分组统计
            COUNT(*) as patient_count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM patients), 2) as percentage,
            AVG(TIMESTAMPDIFF(YEAR, birth_date, CURDATE())) as avg_age,
            -- 使用GROUP_CONCAT展示
            GROUP_CONCAT(DISTINCT blood_type) as blood_types
        FROM patients
        WHERE birth_date IS NOT NULL AND gender IN ('M', 'F')
        GROUP BY age_group, gender
        ORDER BY 
            CASE age_group
                WHEN '<18岁' THEN 1
                WHEN '18-30岁' THEN 2
                WHEN '31-45岁' THEN 3
                WHEN '46-60岁' THEN 4
                ELSE 5
            END, gender
        """

        print("\n📊 查询2: 按年龄段和性别分组统计")
        results2 = self.db.execute(sql2, fetch_all=True)
        for row in results2:
            gender_map = {'M': '男', 'F': '女'}
            gender = gender_map.get(row['gender'], row['gender'])
            print(f"  {row['age_group']} ({gender}): {row['patient_count']}人 ({row.get('percentage', 0)}%)")

        # 示例3: 多级分组统计
        sql3 = """
        SELECT 
            h.name as hospital_name,
            d.dept_name as department_name,
            mv.visit_type,
            COUNT(mv.visit_id) as visit_count,
            COALESCE(SUM(mv.total_fee), 0) as total_revenue,
            COALESCE(AVG(mv.total_fee), 0) as avg_fee
        FROM medical_visits mv
        JOIN hospitals h ON mv.hospital_id = h.hospital_id
        JOIN departments d ON mv.department_id = d.department_id
        WHERE mv.visit_date >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
            AND mv.total_fee IS NOT NULL
        GROUP BY h.hospital_id, h.name, d.department_id, d.dept_name, mv.visit_type
        HAVING COUNT(*) >= 2  -- 降低门槛，更容易看到结果
        ORDER BY h.name, d.dept_name, total_revenue DESC
        LIMIT 15
        """

        print("\n📊 查询3: 多级分组统计（医院-科室-就诊类型）")
        try:
            results3 = self.db.execute(sql3, fetch_all=True)
            if results3:
                print(f"找到 {len(results3)} 条记录:")
                for row in results3[:8]:  # 只显示前8条
                    hospital = row.get('hospital_name', '未知医院')
                    dept = row.get('department_name', row.get('dept_name', '未知科室'))
                    visit_type = row.get('visit_type', '未知')
                    count = row.get('visit_count', 0)
                    revenue = row.get('total_revenue', 0)
                    avg_fee = row.get('avg_fee', 0)

                    print(f"  {hospital} - {dept}")
                    print(f"    类型: {visit_type}, 次数: {count}次")
                    print(f"    收入: ¥{revenue:.2f}, 平均: ¥{avg_fee:.2f}")
            else:
                print("  📭 暂无满足条件的数据（就诊次数>=2）")
        except Exception as e:
            print(f"  注意: 查询可能需要调整: {e}")

    def demo_window_functions(self):
        """窗口函数示例"""
        print("\n" + "-" * 40)
        print("3. 窗口函数示例")
        print("-" * 40)

        # 示例1: 使用ROW_NUMBER()排名
        base_sql = """
        SELECT 
            dept.dept_name,
            d.name as doctor_name,
            d.title,
            COUNT(mv.visit_id) as visit_count,
            COALESCE(SUM(mv.total_fee), 0) as total_revenue
        FROM doctors d
        JOIN departments dept ON d.department_id = dept.department_id
        LEFT JOIN medical_visits mv ON d.doctor_id = mv.doctor_id
        GROUP BY d.department_id, dept.dept_name, d.doctor_id, d.name, d.title
        ORDER BY d.department_id, visit_count DESC, total_revenue DESC
        """

        print("📊 查询1: 医生排名示例（Python计算排名）")
        try:
            # 获取基础数据
            all_doctors = self.db.execute(base_sql, fetch_all=True)

            if all_doctors:
                # 在Python中计算排名
                from collections import defaultdict

                # 按科室分组
                doctors_by_dept = defaultdict(list)
                for doctor in all_doctors:
                    dept_name = doctor.get('dept_name', '未知科室')
                    doctors_by_dept[dept_name].append(doctor)

                # 为每个科室的医生计算排名
                ranked_doctors = []
                for dept_name, doctors in doctors_by_dept.items():
                    # 按就诊次数和收入排序
                    doctors_sorted = sorted(doctors,
                                            key=lambda x: (x.get('visit_count', 0), x.get('total_revenue', 0)),
                                            reverse=True)

                    # 分配排名
                    for i, doctor in enumerate(doctors_sorted[:3]):  # 只取前3名
                        doctor['dept_rank'] = i + 1
                        ranked_doctors.append(doctor)

                # 按科室和排名排序输出
                ranked_doctors.sort(key=lambda x: (x.get('dept_name', ''), x.get('dept_rank', 0)))

                print(f"✅ 找到 {len(ranked_doctors)} 条记录")

                current_dept = None
                for row in ranked_doctors:
                    dept_name = row.get('dept_name', '未知科室')
                    if dept_name != current_dept:
                        print(f"\n🏥 科室: {dept_name}")
                        current_dept = dept_name

                    rank = row.get('dept_rank', 0)
                    print(f"  第{rank}名: {row.get('doctor_name', '未知医生')}")
                    print(f"    就诊: {row.get('visit_count', 0)}次")
                    print(f"    收入: ¥{row.get('total_revenue', 0):.2f}")
            else:
                print("  📭 暂无数据")
        except Exception as e:
            print(f"  注意: 查询可能需要调整: {e}")

        # 示例2: 使用LAG/LEAD计算变化
        sql2 = """
        -- 窗口函数: 计算月度增长率
        WITH monthly_stats AS (
            SELECT 
                DATE_FORMAT(visit_date, '%%Y-%%m') as month,  -- 修正：使用双百分号
                COUNT(*) as visit_count,
                SUM(total_fee) as monthly_revenue
            FROM medical_visits
            WHERE visit_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
            GROUP BY DATE_FORMAT(visit_date, '%%Y-%%m')
        )
        SELECT 
            month,
            visit_count,
            monthly_revenue,
            -- 窗口函数: LAG() 获取上个月数据
            LAG(visit_count) OVER (ORDER BY month) as prev_visit_count,
            LAG(monthly_revenue) OVER (ORDER BY month) as prev_monthly_revenue,
            -- 计算增长率
            ROUND((visit_count - LAG(visit_count) OVER (ORDER BY month)) * 100.0 
                  / NULLIF(LAG(visit_count) OVER (ORDER BY month), 0), 2) as visit_growth_percent,
            ROUND((monthly_revenue - LAG(monthly_revenue) OVER (ORDER BY month)) * 100.0 
                  / NULLIF(LAG(monthly_revenue) OVER (ORDER BY month), 0), 2) as revenue_growth_percent
        FROM monthly_stats
        ORDER BY month DESC
        """

        print("\n📊 查询2: 使用LAG/LEAD计算月度增长率")
        try:
            results2 = self.db.execute(sql2, fetch_all=True)
            for row in results2[:6]:
                growth = row.get('visit_growth_percent', 0)
                growth_sign = "+" if growth > 0 else ""
                print(f"  {row.get('month', '未知')}: {row.get('visit_count', 0)}次就诊 ({growth_sign}{growth}%)")
                print(f"    收入: ¥{row.get('monthly_revenue', 0):.2f} ({row.get('revenue_growth_percent', 0):+.1f}%)")
        except Exception as e:
            print(f"  注意: 可能需要CTE支持: {e}")

    def demo_case_when(self):
        """CASE WHEN条件查询示例"""
        print("\n" + "-" * 40)
        print("4. CASE WHEN条件查询示例")
        print("-" * 40)

        sql = """
        SELECT 
            p.patient_id,
            p.name as patient_name,
            p.gender,
            TIMESTAMPDIFF(YEAR, p.birth_date, CURDATE()) as age,
            -- CASE WHEN示例1: 患者年龄分类
            CASE
                WHEN TIMESTAMPDIFF(YEAR, p.birth_date, CURDATE()) < 18 THEN '未成年人'
                WHEN TIMESTAMPDIFF(YEAR, p.birth_date, CURDATE()) BETWEEN 18 AND 45 THEN '青壮年'
                WHEN TIMESTAMPDIFF(YEAR, p.birth_date, CURDATE()) BETWEEN 46 AND 60 THEN '中年'
                ELSE '老年'
            END as age_category,
            -- CASE WHEN示例2: 消费水平分类
            CASE
                WHEN p.total_spent IS NULL OR p.total_spent = 0 THEN '无消费记录'
                WHEN p.total_spent < 1000 THEN '低消费'
                WHEN p.total_spent BETWEEN 1000 AND 5000 THEN '中等消费'
                WHEN p.total_spent BETWEEN 5001 AND 20000 THEN '高消费'
                ELSE 'VIP客户'
            END as consumption_level,
            -- CASE WHEN示例3: 就诊频率分类
            CASE
                WHEN p.visit_count = 0 THEN '新患者'
                WHEN p.visit_count = 1 THEN '单次就诊'
                WHEN p.visit_count BETWEEN 2 AND 5 THEN '多次就诊'
                WHEN p.visit_count BETWEEN 6 AND 10 THEN '频繁就诊'
                ELSE '高频就诊'
            END as visit_frequency,
            p.visit_count,
            p.total_spent
        FROM (
            SELECT 
                p.patient_id,
                p.name,
                p.gender,
                p.birth_date,
                COUNT(mv.visit_id) as visit_count,
                COALESCE(SUM(mv.total_fee), 0) as total_spent
            FROM patients p
            LEFT JOIN medical_visits mv ON p.patient_id = mv.patient_id
            GROUP BY p.patient_id, p.name, p.gender, p.birth_date
        ) as p
        WHERE p.birth_date IS NOT NULL
        ORDER BY p.total_spent DESC, p.visit_count DESC
        LIMIT 15
        """

        print("📊 CASE WHEN多条件分类示例")
        results = self.db.execute(sql, fetch_all=True)
        for row in results[:8]:
            gender_map = {'M': '男', 'F': '女'}
            gender = gender_map.get(row['gender'], row['gender'])
            print(f"  {row['patient_name']}({gender}, {row.get('age', '?')}岁)")
            print(f"    分类: {row.get('age_category', '未知')}, {row.get('consumption_level', '未知')}")
            print(f"    就诊: {row.get('visit_frequency', '未知')} ({row.get('visit_count', 0)}次)")
            print(f"    消费: ¥{row.get('total_spent', 0):.2f}")

    def demo_complex_joins(self):
        """多表连接复杂查询"""
        print("\n" + "-" * 40)
        print("5. 多表连接复杂查询")
        print("-" * 40)

        sql_simple = """
        -- 简化版本：多表连接基础信息
        SELECT 
            p.name as patient_name,
            p.gender,
            p.blood_type,
            mv.visit_date,
            mv.diagnosis,
            mv.total_fee as visit_fee,
            d.name as doctor_name,
            d.title as doctor_title,
            dept.dept_name as department_name,
            h.name as hospital_name
        FROM medical_visits mv
        JOIN patients p ON mv.patient_id = p.patient_id
        JOIN doctors d ON mv.doctor_id = d.doctor_id
        JOIN departments dept ON d.department_id = dept.department_id
        JOIN hospitals h ON dept.hospital_id = h.hospital_id
        WHERE mv.visit_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            AND mv.total_fee IS NOT NULL
        ORDER BY mv.visit_date DESC
        LIMIT 10
        """

        print("📊 多表连接基础分析")
        try:
            results = self.db.execute(sql_simple, fetch_all=True)
            if results:
                print(f"找到 {len(results)} 条记录:")
                for i, row in enumerate(results, 1):
                    gender_map = {'M': '男', 'F': '女', 'O': '其他'}
                    gender = gender_map.get(row.get('gender'), row.get('gender', '未知'))

                    print(f"\n{i}. {row.get('patient_name', '未知')}({gender})")
                    print(f"  就诊: {row.get('visit_date', '未知')}")
                    print(f"  医院: {row.get('hospital_name', '未知')}")
                    print(f"  科室: {row.get('department_name', '未知')}")
                    print(f"  医生: {row.get('doctor_name', '未知')} ({row.get('doctor_title', '')})")
                    print(f"  诊断: {row.get('diagnosis', '无')}")
                    print(f"  费用: ¥{row.get('visit_fee', 0):.2f}")
            else:
                print("📭 最近7天无就诊记录")
        except Exception as e:
            print(f"  注意: 查询可能需要调整字段名: {e}")


# 主程序
if __name__ == "__main__":
    queries = ComplexQueries()
    queries.run_all_queries()