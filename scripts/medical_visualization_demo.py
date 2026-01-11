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
        """简化版月度趋势可视化 - 修复版"""
        print("\n4. 月度趋势可视化")
        print("-" * 40)

        # 修改SQL查询，增加时间范围并确保有数据
        sql = """
        SELECT 
            DATE_FORMAT(visit_date, '%Y-%m') as month,
            COUNT(*) as visit_count,
            COALESCE(SUM(total_fee), 0) as monthly_revenue
        FROM medical_visits
        WHERE visit_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)  # 改为12个月
        GROUP BY DATE_FORMAT(visit_date, '%Y-%m')
        ORDER BY month
        """

        try:
            results = self.db.execute(sql, fetch_all=True)
            if results and len(results) > 0:
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
                        if monthly_revenue is None:
                            revenue_float = 0.0
                        elif isinstance(monthly_revenue, (int, float)):
                            revenue_float = float(monthly_revenue)
                        else:
                            # 尝试转换为字符串再转浮点数
                            revenue_float = float(str(monthly_revenue))
                    except (ValueError, TypeError, AttributeError) as e:
                        print(f"⚠️  转换收入数据失败: {e}, 原始值: {monthly_revenue}")
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

                # 如果数据不足6个月，添加模拟数据补全
                if len(processed_results) < 6:
                    print("⚠️  数据不足6个月，将补充模拟数据...")
                    processed_results = self._add_mock_data(processed_results)

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

                        row['visit_growth_percent'] = round(growth_rate, 2)
                    else:
                        row['visit_growth_percent'] = 0

                    growth_data.append(row)

                # 生成可视化图表
                self.visualizer.visualize_monthly_growth(
                    growth_data,
                    title="月度就诊增长趋势"
                )

                print("✅ 月度趋势图表已生成")
            else:
                print("📭 暂无月度数据，生成模拟数据...")
                self._demo_mock_monthly_data()

        except Exception as e:
            print(f"❌ 查询失败: {e}")
            import traceback
            traceback.print_exc()
            print("\n尝试生成模拟月度数据...")
            self._demo_mock_monthly_data()

    def _add_mock_data(self, real_data):
        """添加模拟数据补全月度数据"""
        from datetime import datetime, timedelta

        if not real_data:
            return real_data

        # 获取最后一个月份
        last_month = real_data[-1]['month']
        year, month = map(int, last_month.split('-'))

        # 生成模拟月份
        mock_data = real_data.copy()
        months_needed = 6 - len(real_data)

        for i in range(1, months_needed + 1):
            # 计算下一个月
            if month == 12:
                year += 1
                month = 1
            else:
                month += 1

            month_str = f"{year:04d}-{month:02d}"

            # 基于最后一个月的数据生成模拟数据
            last_data = mock_data[-1]
            mock_visit_count = int(last_data['visit_count'] * random.uniform(0.9, 1.1))
            mock_revenue = last_data['monthly_revenue'] * random.uniform(0.9, 1.1)

            mock_data.append({
                'month': month_str,
                'visit_count': max(1, mock_visit_count),
                'monthly_revenue': max(10.0, mock_revenue)
            })

        return mock_data

    def _demo_mock_monthly_data(self):
        """演示用模拟月度数据"""
        print("\n📈 生成模拟月度数据用于演示...")

        from datetime import datetime, timedelta

        # 生成过去6个月的模拟数据
        growth_data = []
        current_date = datetime.now()

        for i in range(6, 0, -1):
            month_date = current_date - timedelta(days=30 * i)
            month_str = month_date.strftime('%Y-%m')

            # 模拟数据，有增长趋势
            base_visits = 50
            growth_factor = 1 + (6 - i) * 0.1  # 每月增长10%
            visit_count = int(base_visits * growth_factor)
            monthly_revenue = visit_count * random.uniform(80, 120)

            # 增长率
            if i == 6:  # 第一个月
                growth_rate = 0
            else:
                growth_rate = 10.0  # 模拟10%增长

            growth_data.append({
                'month': month_str,
                'visit_count': visit_count,
                'monthly_revenue': monthly_revenue,
                'visit_growth_percent': growth_rate
            })

        # 显示模拟数据
        print("\n📊 模拟月度数据:")
        for row in growth_data:
            print(
                f"  {row['month']}: 就诊{row['visit_count']}次, 收入¥{row['monthly_revenue']:.2f}, 增长{row['visit_growth_percent']}%")

        # 生成可视化图表
        self.visualizer.visualize_monthly_growth(
            growth_data,
            title="月度就诊增长趋势（模拟数据）"
        )

        print("✅ 模拟月度趋势图表已生成")

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