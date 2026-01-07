"""
医疗数据可视化模块 - 修正中文字符显示问题
使用Matplotlib创建各种图表
"""

import matplotlib.pyplot as plt
import matplotlib
from matplotlib import font_manager
import numpy as np
from datetime import datetime
import os
import platform
from typing import List, Dict, Tuple
import warnings

# 忽略警告
warnings.filterwarnings('ignore')


class FontManager:
    """字体管理器类"""

    @staticmethod
    def setup_chinese_font():
        """
        设置中文字体支持
        根据操作系统自动配置
        """
        system = platform.system()

        if system == "Windows":
            # Windows系统
            font_names = [
                "Microsoft YaHei",  # 微软雅黑
                "SimHei",  # 黑体
                "SimSun",  # 宋体
                "FangSong",  # 仿宋
                "KaiTi",  # 楷体
                "DengXian",  # 等线
                "Arial"
            ]
        elif system == "Darwin":  # macOS
            font_names = [
                "PingFang SC",  # 苹方
                "STHeiti",  # 华文黑体
                "STSong",  # 华文宋体
                "AppleGothic",  # Apple Gothic
                "Arial Unicode MS"  # Arial Unicode
            ]
        else:  # Linux
            font_names = [
                "DejaVu Sans",  # 开源字体
                "WenQuanYi Micro Hei",  # 文泉驿微米黑
                "Noto Sans CJK SC",  # Noto Sans CJK
                "Arial"
            ]

        # 尝试找到可用的中文字体
        available_fonts = []
        for font_name in font_names:
            try:
                # 检查字体是否可用
                font_path = font_manager.findfont(font_name)
                if font_path and font_path.lower() != 'none':
                    available_fonts.append(font_name)
            except:
                continue

        if available_fonts:
            # 使用找到的第一个可用字体
            selected_font = available_fonts[0]
            plt.rcParams['font.sans-serif'] = [selected_font]
            plt.rcParams['axes.unicode_minus'] = False
            print(f"✅ 使用字体: {selected_font}")
            return selected_font
        else:
            # 如果找不到中文字体，使用系统默认字体
            print("⚠️  未找到中文字体，使用默认字体")
            plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
            return None

    @staticmethod
    def get_chinese_font_path():
        """获取中文字体路径"""
        system = platform.system()

        if system == "Windows":
            # Windows系统常见中文字体路径
            font_paths = [
                r"C:\Windows\Fonts\msyh.ttc",  # 微软雅黑
                r"C:\Windows\Fonts\msyh.ttf",  # 微软雅黑
                r"C:\Windows\Fonts\simhei.ttf",  # 黑体
                r"C:\Windows\Fonts\simsun.ttc",  # 宋体
                r"C:\Windows\Fonts\Deng.ttf",  # 等线
            ]
        elif system == "Darwin":
            font_paths = [
                "/System/Library/Fonts/PingFang.ttc",
                "/System/Library/Fonts/STHeiti Light.ttc",
                "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
            ]
        else:
            font_paths = [
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
            ]

        for font_path in font_paths:
            if os.path.exists(font_path):
                return font_path

        return None


# 初始化字体设置
selected_font = FontManager.setup_chinese_font()

# 设置图表样式
plt.style.use('seaborn-v0_8-darkgrid')


class MedicalVisualizer:
    """医疗数据可视化类"""

    def __init__(self, output_dir: str = "visualizations"):
        """
        初始化可视化工具

        Args:
            output_dir: 图表保存目录
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # 设置字体
        if selected_font:
            self.font_properties = {'family': selected_font, 'size': 12}
        else:
            self.font_properties = {'family': 'sans-serif', 'size': 12}

    def _set_chinese_font(self, ax=None):
        """设置中文字体"""
        if ax:
            for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
                         ax.get_xticklabels() + ax.get_yticklabels()):
                item.set_fontname(self.font_properties['family'])
        else:
            plt.rcParams['font.sans-serif'] = [self.font_properties['family']]
            plt.rcParams['axes.unicode_minus'] = False

    def save_chart(self, filename: str) -> str:
        """保存图表到文件"""
        filepath = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"✅ 图表已保存: {filepath}")
        return filepath

    def show_chart(self):
        """显示图表"""
        plt.show()

    def create_bar_chart(self,
                         title: str,
                         categories: List[str],
                         values: List[float],
                         xlabel: str = "",
                         ylabel: str = "数量",
                         figsize: Tuple[int, int] = (12, 6),
                         color: str = "skyblue",
                         show_values: bool = True,
                         rotation: int = 45,
                         filename: str = None) -> str:
        """
        创建基础柱状图

        Args:
            title: 图表标题
            categories: 类别列表
            values: 值列表
            xlabel: X轴标签
            ylabel: Y轴标签
            figsize: 图表尺寸
            color: 柱状图颜色
            show_values: 是否在柱子上显示数值
            rotation: X轴标签旋转角度
            filename: 保存文件名

        Returns:
            保存的文件路径
        """
        fig, ax = plt.subplots(figsize=figsize)

        # 设置中文字体
        self._set_chinese_font(ax)

        # 创建柱状图
        bars = ax.bar(categories, values, color=color, edgecolor='black', linewidth=0.5, alpha=0.8)

        # 设置标题和标签
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20, fontproperties=self.font_properties)
        ax.set_xlabel(xlabel, fontproperties=self.font_properties)
        ax.set_ylabel(ylabel, fontproperties=self.font_properties)

        # 显示数值 - 修改这里：使用整数格式
        if show_values:
            for bar in bars:
                height = bar.get_height()
                # 修改：使用整数格式，而不是小数格式
                ax.text(bar.get_x() + bar.get_width() / 2., height + 0.01 * max(values),
                        f'{int(height)}',  # 使用int()转换为整数
                        ha='center', va='bottom', fontsize=9,
                        fontproperties=self.font_properties)

        # 设置X轴标签旋转
        plt.setp(ax.get_xticklabels(), rotation=rotation, ha='right', fontproperties=self.font_properties)

        # 自动调整Y轴范围
        ax.set_ylim(0, max(values) * 1.15)

        # 添加网格
        ax.grid(True, axis='y', alpha=0.3)

        if filename:
            return self.save_chart(filename)
        return ""

    def create_grouped_bar_chart(self,
                                 title: str,
                                 data: Dict[str, Dict[str, float]],
                                 figsize: Tuple[int, int] = (14, 7),
                                 filename: str = None) -> str:
        """
        创建分组柱状图

        Args:
            title: 图表标题
            data: 数据字典 {分组1: {类别1: 值1, ...}, 分组2: {...}, ...}
            figsize: 图表尺寸
            filename: 保存文件名

        Returns:
            保存的文件路径
        """
        fig, ax = plt.subplots(figsize=figsize)

        # 设置中文字体
        self._set_chinese_font(ax)

        # 提取分组和类别
        groups = list(data.keys())
        categories = list(next(iter(data.values())).keys())

        # 设置柱状图位置
        x = np.arange(len(categories))
        width = 0.8 / len(groups)  # 柱状图宽度

        # 颜色方案
        colors = plt.cm.Set3(np.linspace(0, 1, len(groups)))

        # 创建每个分组的柱状图
        for i, (group_name, group_data) in enumerate(data.items()):
            values = [group_data.get(cat, 0) for cat in categories]
            ax.bar(x + i * width - width * (len(groups) - 1) / 2,
                   values,
                   width,
                   label=group_name,
                   color=colors[i],
                   edgecolor='black',
                   linewidth=0.5,
                   alpha=0.8)

        # 设置图表属性
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20, fontproperties=self.font_properties)
        ax.set_xlabel('类别', fontproperties=self.font_properties)
        ax.set_ylabel('数量', fontproperties=self.font_properties)

        plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontproperties=self.font_properties)
        ax.legend(title='分组', prop=self.font_properties)

        # 添加网格
        ax.grid(True, axis='y', alpha=0.3)

        if filename:
            return self.save_chart(filename)
        return ""

    def create_stacked_bar_chart(self,
                                 title: str,
                                 categories: List[str],
                                 data_layers: Dict[str, List[float]],
                                 figsize: Tuple[int, int] = (14, 7),
                                 filename: str = None) -> str:
        """
        创建堆叠柱状图

        Args:
            title: 图表标题
            categories: 类别列表
            data_layers: 数据层字典 {层名: [值列表], ...}
            figsize: 图表尺寸
            filename: 保存文件名

        Returns:
            保存的文件路径
        """
        fig, ax = plt.subplots(figsize=figsize)

        # 设置中文字体
        self._set_chinese_font(ax)

        x = np.arange(len(categories))
        width = 0.8

        # 颜色方案
        colors = plt.cm.Paired(np.linspace(0, 1, len(data_layers)))

        # 创建堆叠柱状图
        bottom = np.zeros(len(categories))

        for i, (layer_name, values) in enumerate(data_layers.items()):
            ax.bar(x, values, width, bottom=bottom,
                   label=layer_name, color=colors[i],
                   edgecolor='black', linewidth=0.5, alpha=0.8)
            bottom += values

        # 设置图表属性
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20, fontproperties=self.font_properties)
        ax.set_xlabel('类别', fontproperties=self.font_properties)
        ax.set_ylabel('数量', fontproperties=self.font_properties)

        plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontproperties=self.font_properties)
        ax.legend(title='组成部分', prop=self.font_properties)

        # 添加网格
        ax.grid(True, axis='y', alpha=0.3)

        if filename:
            return self.save_chart(filename)
        return ""

    def create_horizontal_bar_chart(self,
                                    title: str,
                                    categories: List[str],
                                    values: List[float],
                                    ylabel: str = "",
                                    xlabel: str = "数量",
                                    figsize: Tuple[int, int] = (12, 8),
                                    color: str = "lightcoral",
                                    show_values: bool = True,
                                    filename: str = None) -> str:
        """
        创建横向柱状图

        Args:
            title: 图表标题
            categories: 类别列表
            values: 值列表
            ylabel: Y轴标签
            xlabel: X轴标签
            figsize: 图表尺寸
            color: 柱状图颜色
            show_values: 是否显示数值
            filename: 保存文件名

        Returns:
            保存的文件路径
        """
        fig, ax = plt.subplots(figsize=figsize)

        # 设置中文字体
        self._set_chinese_font(ax)

        # 创建横向柱状图
        bars = ax.barh(categories, values, color=color, edgecolor='black', linewidth=0.5, alpha=0.8)

        # 设置标题和标签
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20, fontproperties=self.font_properties)
        ax.set_xlabel(xlabel, fontproperties=self.font_properties)
        ax.set_ylabel(ylabel, fontproperties=self.font_properties)

        # 显示数值
        if show_values:
            for bar in bars:
                width = bar.get_width()
                ax.text(width + 0.01 * max(values), bar.get_y() + bar.get_height() / 2.,
                        f'{width:.1f}', ha='left', va='center', fontsize=9,
                        fontproperties=self.font_properties)

        # 自动调整X轴范围
        ax.set_xlim(0, max(values) * 1.1)

        # 添加网格
        ax.grid(True, axis='x', alpha=0.3)

        if filename:
            return self.save_chart(filename)
        return ""


class MedicalQueryVisualizer(MedicalVisualizer):
    """专门用于医疗查询结果的可视化类"""

    def __init__(self, output_dir: str = "visualizations"):
        """初始化"""
        super().__init__(output_dir)
        # 额外设置，确保所有文本使用中文字体
        matplotlib.rcParams.update({
            'font.size': 12,
            'axes.titlesize': 16,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 10
        })

    def visualize_doctor_ranking(self,
                                 ranking_data: List[Dict],
                                 title: str = "医生就诊量排名",
                                 top_n: int = 10,
                                 save: bool = True) -> str:
        """
        可视化医生排名

        Args:
            ranking_data: 排名数据 [{医生信息}, ...]
            title: 图表标题
            top_n: 显示前N名
            save: 是否保存图表

        Returns:
            图表文件路径
        """
        # 提取前N名数据
        top_data = ranking_data[:top_n]

        # 准备数据
        doctor_names = []
        for row in top_data:
            doctor_name = row.get('doctor_name', '未知')
            dept_name = row.get('dept_name', '未知')
            # 缩短名称以防止显示问题
            if len(doctor_name) > 4:
                doctor_name = doctor_name[:4] + '..'
            if len(dept_name) > 4:
                dept_name = dept_name[:4] + '..'
            doctor_names.append(f"{doctor_name}\n({dept_name})")

        visit_counts = [row.get('visit_count', 0) for row in top_data]
        revenues = [row.get('total_revenue', 0) for row in top_data]

        # 创建图表
        fig, ax1 = plt.subplots(figsize=(14, 8))

        # 设置中文字体
        self._set_chinese_font(ax1)

        x = np.arange(len(doctor_names))
        width = 0.35

        # 就诊次数柱状图
        bars1 = ax1.bar(x - width / 2, visit_counts, width,
                        label='就诊次数', color='skyblue', edgecolor='black', alpha=0.8)

        ax1.set_xlabel('医生', fontproperties=self.font_properties)
        ax1.set_ylabel('就诊次数', fontproperties=self.font_properties, color='skyblue')
        ax1.tick_params(axis='y', labelcolor='skyblue')

        # 创建第二个Y轴用于收入
        ax2 = ax1.twinx()
        bars2 = ax2.bar(x + width / 2, revenues, width,
                        label='总收入(元)', color='lightcoral', edgecolor='black', alpha=0.8)

        ax2.set_ylabel('总收入(元)', fontproperties=self.font_properties, color='lightcoral')
        ax2.tick_params(axis='y', labelcolor='lightcoral')

        # 设置标题
        ax1.set_title(title, fontsize=16, fontweight='bold', pad=20, fontproperties=self.font_properties)

        # 设置X轴标签
        ax1.set_xticks(x)
        ax1.set_xticklabels(doctor_names, rotation=45, ha='right', fontproperties=self.font_properties)

        # 添加图例
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', prop=self.font_properties)

        # 添加数值标签
        for bars, ax in [(bars1, ax1), (bars2, ax2)]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2., height + 0.01 * max(height, 1),
                        f'{height:.0f}', ha='center', va='bottom', fontsize=8,
                        fontproperties=self.font_properties)

        plt.tight_layout()

        if save:
            filename = f"doctor_ranking_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            return self.save_chart(filename)
        return ""

    def visualize_department_statistics(self,
                                        dept_stats: List[Dict],
                                        title: str = "科室就诊统计",
                                        save: bool = True) -> str:
        """
        可视化科室统计

        Args:
            dept_stats: 科室统计数据
            title: 图表总标题
            save: 是否保存图表

        Returns:
            图表文件路径
        """
        # 准备数据
        categories = []
        for row in dept_stats:
            dept_name = row.get('dept_name', '未知科室')
            # 缩短科室名称
            if len(dept_name) > 6:
                dept_name = dept_name[:6] + '..'
            categories.append(dept_name)

        visit_counts = [row.get('visit_count', 0) for row in dept_stats]
        revenues = [row.get('total_revenue', 0) for row in dept_stats]

        # 创建子图
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

        # 设置中文字体
        self._set_chinese_font(ax1)
        self._set_chinese_font(ax2)

        x = np.arange(len(categories))
        width = 0.8

        # 就诊次数柱状图
        bars1 = ax1.bar(x, visit_counts, width, color='lightgreen',
                        edgecolor='black', label='就诊次数', alpha=0.8)
        ax1.set_title('各科室就诊次数对比', fontsize=14, fontweight='bold', fontproperties=self.font_properties, pad=10)
        ax1.set_ylabel('就诊次数', fontproperties=self.font_properties)
        ax1.set_xticks(x)
        ax1.set_xticklabels(categories, rotation=45, ha='right', fontproperties=self.font_properties)
        ax1.grid(True, axis='y', alpha=0.3)

        # 添加就诊次数数值（整数格式）
        for bar in bars1:
            height = bar.get_height()
            if height > 0:  # 只显示大于0的值
                ax1.text(bar.get_x() + bar.get_width() / 2., height + 0.01 * max(visit_counts),
                         f'{int(height)}',  # 整数格式
                         ha='center', va='bottom', fontsize=9,
                         fontproperties=self.font_properties)

        # 收入柱状图
        bars2 = ax2.bar(x, revenues, width, color='gold',
                        edgecolor='black', label='总收入', alpha=0.8)
        ax2.set_title('各科室收入对比', fontsize=14, fontweight='bold', fontproperties=self.font_properties, pad=10)
        ax2.set_ylabel('收入(元)', fontproperties=self.font_properties)  # 保留"(元)"
        ax2.set_xticks(x)
        ax2.set_xticklabels(categories, rotation=45, ha='right', fontproperties=self.font_properties)
        ax2.grid(True, axis='y', alpha=0.3)

        # 修改这里：移除收入数值前的"¥"符号
        for bar in bars2:
            height = bar.get_height()
            if height > 0:  # 只显示大于0的值
                # 移除¥符号，只显示数字
                ax2.text(bar.get_x() + bar.get_width() / 2., height + 0.01 * max(revenues),
                         f'{height:.0f}',  # 修改：移除¥符号
                         ha='center', va='bottom', fontsize=9,
                         fontproperties=self.font_properties)

        # 设置总标题
        if title:
            plt.suptitle(title, fontsize=16, fontweight='bold', y=0.98, fontproperties=self.font_properties)
            plt.tight_layout(rect=[0, 0, 1, 0.96])  # 调整布局，为总标题留出空间
        else:
            plt.tight_layout()

        if save:
            filename = f"department_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            return self.save_chart(filename)
        return ""

    def visualize_monthly_growth(self,
                                 growth_data: List[Dict],
                                 title: str = "月度就诊增长趋势",
                                 save: bool = True) -> str:
        """
        可视化月度增长趋势

        Args:
            growth_data: 增长数据
            title: 图表总标题
            save: 是否保存图表

        Returns:
            图表文件路径
        """
        # 准备数据
        months = []
        for row in growth_data:
            month = row.get('month', '未知')
            # 格式化月份显示
            if '-' in month:
                year, mon = month.split('-')
                months.append(f"{year}年{mon}月")
            else:
                months.append(month)

        visit_counts = [row.get('visit_count', 0) for row in growth_data]
        revenues = [row.get('monthly_revenue', 0) for row in growth_data]
        growth_rates = [row.get('visit_growth_percent', 0) for row in growth_data]

        # 创建图表
        fig, (ax1, ax3) = plt.subplots(2, 1, figsize=(14, 10))

        # 设置中文字体
        self._set_chinese_font(ax1)
        self._set_chinese_font(ax3)

        # 就诊次数柱状图
        bars1 = ax1.bar(months, visit_counts, color='cornflowerblue',
                        edgecolor='black', alpha=0.7, label='就诊次数')

        # 修改：移除子图标题，避免与总标题重叠
        # ax1.set_title('月度就诊次数', fontsize=14, fontweight='bold', fontproperties=self.font_properties)
        ax1.set_ylabel('就诊次数', fontproperties=self.font_properties)
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(True, axis='y', alpha=0.3)

        # 添加就诊次数数值
        for bar in bars1:
            height = bar.get_height()
            if height > 0:  # 只显示大于0的值
                ax1.text(bar.get_x() + bar.get_width() / 2., height + 0.01 * max(visit_counts),
                         f'{height:.0f}', ha='center', va='bottom', fontsize=9,
                         fontproperties=self.font_properties)

        # 创建第二个Y轴用于增长率
        ax2 = ax1.twinx()
        line1 = ax2.plot(months, growth_rates, 'r-o', linewidth=2,
                         markersize=8, label='增长率(%)')
        ax2.set_ylabel('增长率(%)', fontproperties=self.font_properties, color='red')
        ax2.tick_params(axis='y', labelcolor='red')
        ax2.grid(True, axis='y', alpha=0.3, linestyle='--')

        # 合并图例
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', prop=self.font_properties)

        # 收入柱状图
        bars2 = ax3.bar(months, revenues, color='salmon',
                        edgecolor='black', alpha=0.7, label='收入')

        # 修改：移除子图标题，避免与总标题重叠
        # ax3.set_title('月度收入', fontsize=14, fontweight='bold', fontproperties=self.font_properties)
        ax3.set_ylabel('收入(元)', fontproperties=self.font_properties)
        ax3.tick_params(axis='x', rotation=45)
        ax3.grid(True, axis='y', alpha=0.3)

        # 修改：移除收入数值前的"¥"符号
        for bar in bars2:
            height = bar.get_height()
            if height > 0:  # 只显示大于0的值
                # 修改这里：移除¥符号
                ax3.text(bar.get_x() + bar.get_width() / 2., height + 0.01 * max(revenues),
                         f'{height:.0f}', ha='center', va='bottom', fontsize=9,
                         fontproperties=self.font_properties)

        # 设置总标题
        if title:
            # 调整总标题位置，避免与子图标题重叠
            plt.suptitle(title, fontsize=16, fontweight='bold', y=0.95, fontproperties=self.font_properties)
            plt.tight_layout(rect=[0, 0, 1, 0.95])  # 调整布局，为总标题留出空间
        else:
            plt.tight_layout()

        if save:
            filename = f"monthly_growth_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            return self.save_chart(filename)
        return ""

    def visualize_patient_demographics(self,
                                       patient_data: List[Dict],
                                       title: str = "患者人口统计",
                                       save: bool = True) -> str:
        """
        可视化患者人口统计数据

        Args:
            patient_data: 患者数据
            title: 图表标题
            save: 是否保存图表

        Returns:
            图表文件路径
        """
        # 创建子图
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))

        # 设置中文字体
        for ax in [ax1, ax2, ax3, ax4]:
            self._set_chinese_font(ax)

        # 1. 性别分布
        gender_data = {}
        for row in patient_data:
            gender = row.get('gender', '未知')
            if gender == 'M':
                gender_label = '男'
            elif gender == 'F':
                gender_label = '女'
            else:
                gender_label = '未知'
            gender_data[gender_label] = gender_data.get(gender_label, 0) + 1

        gender_labels = list(gender_data.keys())
        gender_values = list(gender_data.values())

        colors1 = ['lightblue', 'lightpink', 'lightgray']
        wedges, texts, autotexts = ax1.pie(gender_values, labels=gender_labels,
                                           autopct='%1.1f%%', startangle=90,
                                           colors=colors1[:len(gender_values)])

        # 设置饼图文本字体
        for text in texts + autotexts:
            text.set_fontproperties(self.font_properties)

        ax1.set_title('性别分布', fontsize=14, fontweight='bold', fontproperties=self.font_properties)

        # 2. 血型分布
        blood_data = {}
        for row in patient_data:
            blood = row.get('blood_type', '未知')
            blood_data[blood] = blood_data.get(blood, 0) + 1

        blood_types = list(blood_data.keys())
        blood_counts = list(blood_data.values())

        bars = ax2.bar(blood_types, blood_counts, color='lightcoral', edgecolor='black', alpha=0.8)
        ax2.set_title('血型分布', fontsize=14, fontweight='bold', fontproperties=self.font_properties)
        ax2.set_xlabel('血型', fontproperties=self.font_properties)
        ax2.set_ylabel('人数', fontproperties=self.font_properties)
        ax2.grid(True, axis='y', alpha=0.3)

        # 3. 年龄分布
        ages = [row.get('age', 0) for row in patient_data if row.get('age')]
        if ages:
            ax3.hist(ages, bins=20, color='lightgreen', edgecolor='black', alpha=0.7)
            ax3.set_title('年龄分布', fontsize=14, fontweight='bold', fontproperties=self.font_properties)
            ax3.set_xlabel('年龄', fontproperties=self.font_properties)
            ax3.set_ylabel('人数', fontproperties=self.font_properties)
            ax3.grid(True, axis='y', alpha=0.3)
        else:
            ax3.text(0.5, 0.5, '无年龄数据', ha='center', va='center',
                     fontsize=12, transform=ax3.transAxes, fontproperties=self.font_properties)
            ax3.set_title('年龄分布', fontsize=14, fontweight='bold', fontproperties=self.font_properties)

        # 4. 就诊次数分布
        visit_counts = [row.get('visit_count', 0) for row in patient_data]
        unique, counts = np.unique(visit_counts, return_counts=True)

        bars4 = ax4.bar(unique[:10], counts[:10], color='gold', edgecolor='black', alpha=0.8)
        ax4.set_title('就诊次数分布(前10)', fontsize=14, fontweight='bold', fontproperties=self.font_properties)
        ax4.set_xlabel('就诊次数', fontproperties=self.font_properties)
        ax4.set_ylabel('患者人数', fontproperties=self.font_properties)
        ax4.grid(True, axis='y', alpha=0.3)

        plt.suptitle(title, fontsize=16, fontweight='bold', y=0.95, fontproperties=self.font_properties)
        plt.tight_layout()

        if save:
            filename = f"patient_demographics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            return self.save_chart(filename)
        return ""