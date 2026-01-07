"""
简化版医疗数据可视化演示
避免使用pandas，解决依赖问题
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.db_connection import BaseConnection
from visualization import MedicalQueryVisualizer


class SimpleMedicalVisualization:
    """简化版医疗数据可视化"""

    def __init__(self):
        self.db = BaseConnection()
        self.visualizer = MedicalQueryVisualizer()

    def run_simple_demos(self):
        """运行简化版可视化演示"""
        try:
            self.db.connect()

            print("=" * 60)
            print("简化版医疗数据库查询可视化演示")
            print("=" * 60)

            # 1. 基础柱状图演示
            self.demo_basic_bar_chart()

            # 2. 医生排名可视化
            self.demo_doctor_ranking_simple()

            # 3. 科室统计可视化
            self.demo_department_statistics_simple()

            # 4. 月度趋势可视化
            self.demo_monthly_trend_simple()

            print("\n" + "=" * 60)
            print("✅ 所有可视化演示完成！")
            print(f"📁 图表已保存到: {self.visualizer.output_dir}")
            print("=" * 60)

        except Exception as e:
            print(f"❌ 演示出错: {e}")
        finally:
            self.db.close()

    def demo_basic_bar_chart(self):
        """基础柱状图演示"""
        print("\n1. 基础柱状图演示")
        print("-" * 40)

        # 模拟数据
        categories = ['内科', '外科', '儿科', '妇产科', '中医科', '口腔科']
        values = [150, 120, 180, 90, 60, 80]

        # 创建柱状图
        self.visualizer.create_bar_chart(
            title='各科室就诊量统计',
            categories=categories,
            values=values,
            xlabel='科室',
            ylabel='就诊次数',
            figsize=(10, 6),
            color='lightblue',
            filename='basic_department_visits.png'
        )

        print("✅ 基础柱状图已生成")

    def demo_doctor_ranking_simple(self):
        """简化版医生排名可视化"""
        print("\n2. 医生排名可视化")
        print("-" * 40)

        sql = """
        SELECT 
            d.name as doctor_name,
            dept.dept_name,
            COUNT(mv.visit_id) as visit_count,
            COALESCE(SUM(mv.total_fee), 0) as total_revenue
        FROM doctors d
        JOIN departments dept ON d.department_id = dept.department_id
        LEFT JOIN medical_visits mv ON d.doctor_id = mv.doctor_id
        GROUP BY d.doctor_id, d.name, dept.dept_name
        HAVING COUNT(mv.visit_id) > 0
        ORDER BY visit_count DESC
        LIMIT 10
        """

        try:
            results = self.db.execute(sql, fetch_all=True)
            if results:
                print(f"✅ 获取到 {len(results)} 位医生的数据")

                # 显示数据
                print("\n📊 医生排名数据:")
                for i, row in enumerate(results, 1):
                    print(f"  {i}. {row.get('doctor_name', '未知')} ({row.get('dept_name', '未知')})")
                    print(f"     就诊: {row.get('visit_count', 0)}次")
                    print(f"     收入: ¥{row.get('total_revenue', 0):.2f}")

                # 生成可视化图表
                self.visualizer.visualize_doctor_ranking(
                    results,
                    title="医生就诊量和收入排名Top 10",
                    top_n=10
                )

                print("✅ 医生排名图表已生成")
            else:
                print("📭 暂无医生数据")

        except Exception as e:
            print(f"❌ 查询失败: {e}")

    def demo_department_statistics_simple(self):
        """简化版科室统计可视化"""
        print("\n3. 科室统计可视化")
        print("-" * 40)

        sql = """
        SELECT 
            dept.dept_name,
            COUNT(mv.visit_id) as visit_count,
            COALESCE(SUM(mv.total_fee), 0) as total_revenue
        FROM departments dept
        LEFT JOIN doctors d ON dept.department_id = d.department_id
        LEFT JOIN medical_visits mv ON d.doctor_id = mv.doctor_id
        WHERE mv.visit_date IS NOT NULL
        GROUP BY dept.department_id, dept.dept_name
        HAVING COUNT(mv.visit_id) > 0
        ORDER BY total_revenue DESC
        LIMIT 8
        """

        try:
            results = self.db.execute(sql, fetch_all=True)
            if results:
                print(f"✅ 获取到 {len(results)} 个科室的数据")

                # 显示数据
                print("\n📊 科室统计数据:")
                for i, row in enumerate(results, 1):
                    dept_name = row.get('dept_name', '未知科室')
                    visit_count = row.get('visit_count', 0)
                    total_revenue = row.get('total_revenue', 0)

                    # 将decimal转换为float用于显示
                    try:
                        revenue_float = float(total_revenue)
                    except (TypeError, ValueError):
                        revenue_float = 0.0

                    print(f"  {i}. {dept_name}")
                    print(f"     就诊: {visit_count}次")
                    print(f"     收入: ¥{revenue_float:.2f}")

                    # 更新row中的revenue为float类型
                    row['total_revenue'] = revenue_float

                # 生成可视化图表
                self.visualizer.visualize_department_statistics(
                    results,
                    title="科室就诊统计"
                )

                print("✅ 科室统计图表已生成")
            else:
                print("📭 暂无科室数据")

        except Exception as e:
            print(f"❌ 查询失败: {e}")

    def demo_monthly_trend_simple(self):
        """简化版月度趋势可视化"""
        print("\n4. 月度趋势可视化")
        print("-" * 40)

        sql = """
        SELECT 
            DATE_FORMAT(visit_date, '%%Y-%%m') as month,
            COUNT(*) as visit_count,
            COALESCE(SUM(total_fee), 0) as monthly_revenue
        FROM medical_visits
        WHERE visit_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
        GROUP BY DATE_FORMAT(visit_date, '%%Y-%%m')
        ORDER BY month
        """

        try:
            results = self.db.execute(sql, fetch_all=True)
            if results:
                print(f"✅ 获取到 {len(results)} 个月的数据")

                # 显示数据
                print("\n📊 月度数据:")

                # 先处理数据类型转换
                processed_results = []
                for row in results:
                    month = row.get('month', '未知')
                    visit_count = int(row.get('visit_count', 0))

                    # 安全转换monthly_revenue为float
                    monthly_revenue = row.get('monthly_revenue', 0)
                    try:
                        if hasattr(monthly_revenue, '__float__'):
                            revenue_float = float(monthly_revenue)
                        else:
                            revenue_float = float(str(monthly_revenue))
                    except (ValueError, TypeError, AttributeError):
                        revenue_float = 0.0

                    print(f"  {month}:")
                    print(f"     就诊: {visit_count}次")
                    print(f"     收入: ¥{revenue_float:.2f}")

                    # 创建处理后的数据
                    processed_row = {
                        'month': month,
                        'visit_count': visit_count,
                        'monthly_revenue': revenue_float
                    }
                    processed_results.append(processed_row)

                # 计算增长率
                growth_data = []
                for i, row in enumerate(processed_results):
                    if i > 0:  # 从第二个月开始计算增长率
                        prev = processed_results[i - 1]
                        prev_count = prev.get('visit_count', 0)
                        current_count = row.get('visit_count', 0)

                        # 计算就诊增长率
                        if prev_count > 0:
                            growth_rate = ((current_count - prev_count) * 100.0 / prev_count)
                        else:
                            growth_rate = 0

                        # 计算收入增长率
                        prev_revenue = prev.get('monthly_revenue', 0)
                        current_revenue = row.get('monthly_revenue', 0)

                        if prev_revenue > 0:
                            revenue_growth = ((current_revenue - prev_revenue) * 100.0 / prev_revenue)
                        else:
                            revenue_growth = 0

                        row['visit_growth_percent'] = round(growth_rate, 2)
                        row['revenue_growth_percent'] = round(revenue_growth, 2)
                    else:
                        row['visit_growth_percent'] = 0
                        row['revenue_growth_percent'] = 0

                    growth_data.append(row)

                # 生成可视化图表
                self.visualizer.visualize_monthly_growth(
                    growth_data,
                    title="月度就诊增长趋势"
                )

                print("✅ 月度趋势图表已生成")
            else:
                print("📭 暂无月度数据")

        except Exception as e:
            print(f"❌ 查询失败: {e}")
            import traceback
            print(f"详细错误: {traceback.format_exc()}")

    def demo_custom_chart(self):
        """自定义图表演示"""
        print("\n5. 自定义图表演示")
        print("-" * 40)

        # 创建横向柱状图
        categories = ['普通门诊', '专家门诊', '急诊', '专科门诊', '体检']
        values = [350, 280, 120, 190, 85]

        self.visualizer.create_horizontal_bar_chart(
            title='各类就诊类型数量统计',
            categories=categories,
            values=values,
            ylabel='就诊类型',
            xlabel='就诊次数',
            figsize=(10, 6),
            color='lightgreen',
            filename='visit_type_horizontal.png'
        )

        print("✅ 自定义图表已生成")


# 主程序
if __name__ == "__main__":
    print("🚀 开始简化版医疗数据库查询可视化演示...")
    print("=" * 60)

    demo = SimpleMedicalVisualization()
    demo.run_simple_demos()