"""
中文字符显示测试工具
用于诊断和解决医疗数据库可视化中的中文乱码问题
"""

import os
import platform
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pymysql
from database.db_connection import BaseConnection
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')


def test_system_info():
    """测试系统信息"""
    print("=" * 60)
    print("🖥️  系统信息检测")
    print("=" * 60)

    system = platform.system()
    version = platform.version()
    release = platform.release()

    print(f"操作系统: {system} {release} ({version})")
    print(f"Python版本: {platform.python_version()}")
    print(f"Matplotlib版本: {matplotlib.__version__}")
    print(f"PyMySQL版本: {pymysql.__version__}")

    return system


def test_matplotlib_fonts():
    """测试Matplotlib字体支持"""
    print("\n" + "=" * 60)
    print("🔤 Matplotlib字体检测")
    print("=" * 60)

    font_list = fm.fontManager.ttflist
    print(f"系统可用字体总数: {len(font_list)}")

    chinese_fonts = []
    for font in font_list:
        font_name = font.name
        font_path = font.fname

        if any(keyword in font_name.lower() for keyword in
               ['yahei', 'heiti', 'songti', 'kaiti', 'fang', 'pingfang', 'simsun', 'simhei', 'microsoft', 'msyh',
                'deng', 'st', '华文', '文泉驿']):
            chinese_fonts.append((font_name, font_path))

    print(f"✅ 中文字体数量: {len(chinese_fonts)}")

    if chinese_fonts:
        print(f"\n📋 中文字体列表 (前10个):")
        for i, (font_name, font_path) in enumerate(chinese_fonts[:10], 1):
            print(f"  {i:2d}. {font_name}")
    else:
        print("❌ 未检测到中文字体")

    return chinese_fonts


def test_specific_chinese_fonts():
    """测试特定中文字体"""
    print("\n" + "=" * 60)
    print("🔍 常用中文字体检测")
    print("=" * 60)

    common_chinese_fonts = {
        'Windows': [
            'Microsoft YaHei',
            'SimHei',
            'SimSun',
            'FangSong',
            'KaiTi',
            'DengXian',
            'NSimSun',
            'YouYuan',
        ],
        'Darwin': [
            'PingFang SC',
            'STHeiti',
            'STSong',
            'STKaiti',
            'STFangsong',
            'AppleGothic',
            'Arial Unicode MS',
        ],
        'Linux': [
            'WenQuanYi Micro Hei',
            'Noto Sans CJK SC',
            'DejaVu Sans',
            'AR PL UMing CN',
            'AR PL UKai CN',
        ]
    }

    system = platform.system()
    fonts_to_check = common_chinese_fonts.get(system, [])

    if not fonts_to_check:
        print(f"❌ 未找到 {system} 系统的字体配置")
        return []

    available_fonts = []
    for font_name in fonts_to_check:
        try:
            font_path = fm.findfont(font_name, fallback_to_default=False)
            if font_path and 'none' not in font_path.lower():
                print(f"✅ {font_name}: 可用")
                available_fonts.append((font_name, font_path))
            else:
                print(f"❌ {font_name}: 不可用")
        except Exception as e:
            print(f"❌ {font_name}: 检测失败")

    if not available_fonts:
        print("⚠️  未找到可用的中文字体")

    return available_fonts


def test_database_charset():
    """测试数据库字符集"""
    print("\n" + "=" * 60)
    print("🗃️  数据库字符集检测")
    print("=" * 60)

    try:
        db = BaseConnection()
        db.connect()

        charset_sql = """
        SELECT 
            @@character_set_database as db_charset,
            @@collation_database as db_collation,
            @@character_set_server as server_charset,
            @@character_set_client as client_charset
        """

        result = db.execute(charset_sql, fetch_one=True)

        if result:
            print("数据库字符集配置:")
            print(f"  数据库字符集: {result.get('db_charset', '未知')}")
            print(f"  数据库排序规则: {result.get('db_collation', '未知')}")
            print(f"  服务器字符集: {result.get('server_charset', '未知')}")
            print(f"  客户端字符集: {result.get('client_charset', '未知')}")

            if 'utf8mb4' in result.get('db_charset', '').lower():
                print("✅ 数据库字符集支持中文 (utf8mb4)")
            else:
                print("⚠️  数据库字符集可能不支持完整的中文字符")
        else:
            print("❌ 无法获取数据库字符集信息")

        db.close()

    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")


def test_chinese_in_database():
    """测试数据库中的中文数据"""
    print("\n" + "=" * 60)
    print("🔤 数据库中文数据测试")
    print("=" * 60)

    try:
        db = BaseConnection()
        db.connect()

        test_queries = [
            ("患者姓名", "SELECT name FROM patients LIMIT 5"),
            ("医生姓名", "SELECT name FROM doctors LIMIT 5"),
            ("科室名称", "SELECT dept_name FROM departments LIMIT 5"),
        ]

        for label, sql in test_queries:
            print(f"\n{label}:")
            try:
                results = db.execute(sql, fetch_all=True)
                if results:
                    for i, row in enumerate(results, 1):
                        value = list(row.values())[0] if row else "无数据"
                        print(f"  {i}. {value}")
                else:
                    print("  📭 无数据")
            except Exception as e:
                print(f"  ❌ 查询失败")

        db.close()

    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")


def test_matplotlib_rendering():
    """测试Matplotlib中文渲染"""
    print("\n" + "=" * 60)
    print("🎨 Matplotlib中文渲染测试")
    print("=" * 60)

    chinese_fonts = test_specific_chinese_fonts()

    if not chinese_fonts:
        print("⚠️  无可用中文字体，使用默认字体测试")
        chinese_fonts = [('DejaVu Sans', '')]

    test_texts = [
        "这是一段测试文本",
        "医疗数据库系统",
        "患者管理 医生管理 科室管理",
        "图表可视化 数据统计 系统监控",
        "中文显示测试: 〇一二三四五六七八九十"
    ]

    os.makedirs('font_tests', exist_ok=True)

    for font_name, font_path in chinese_fonts[:3]:
        print(f"\n📊 测试字体: {font_name}")

        try:
            matplotlib.rcParams['font.sans-serif'] = [font_name]
            matplotlib.rcParams['axes.unicode_minus'] = False

            fig, ax = plt.subplots(figsize=(10, 6))

            for i, text in enumerate(test_texts):
                ax.text(0.1, 0.9 - i * 0.15, text, fontsize=14, transform=ax.transAxes)

            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_title(f'中文字体测试: {font_name}', fontsize=16, fontweight='bold')
            ax.axis('off')

            filename = f'font_test_{font_name.replace(" ", "_")}.png'
            plt.tight_layout()
            plt.savefig(f'font_tests/{filename}', dpi=150, bbox_inches='tight')
            plt.close()

            print(f"  ✅ 图表已保存: font_tests/{filename}")

        except Exception as e:
            print(f"  ❌ 渲染失败")

    print("\n📁 测试图表已保存到 font_tests/ 目录")


def test_visualization_pipeline():
    """测试完整的可视化流程"""
    print("\n" + "=" * 60)
    print("🔧 完整可视化流程测试")
    print("=" * 60)

    try:
        from visualization import MedicalVisualizer

        visualizer = MedicalVisualizer(output_dir='font_tests')

        categories = ['内科', '外科', '儿科', '妇产科', '中医科']
        values = [150, 120, 180, 90, 60]

        print("测试基础柱状图...")
        try:
            visualizer.create_bar_chart(
                title='各科室就诊量统计',
                categories=categories,
                values=values,
                xlabel='科室',
                ylabel='就诊次数',
                filename='pipeline_test_barchart.png'
            )
            print("✅ 基础柱状图测试通过")
        except Exception as e:
            print(f"❌ 基础柱状图测试失败")

        print("测试横向柱状图...")
        try:
            visualizer.create_horizontal_bar_chart(
                title='就诊类型统计',
                categories=['普通门诊', '急诊', '专家门诊'],
                values=[350, 120, 280],
                filename='pipeline_test_horizontal.png'
            )
            print("✅ 横向柱状图测试通过")
        except Exception as e:
            print(f"❌ 横向柱状图测试失败")

    except Exception as e:
        print(f"❌ 可视化流程测试失败")


def generate_font_config():
    """生成字体配置文件"""
    print("\n" + "=" * 60)
    print("⚙️  生成字体配置建议")
    print("=" * 60)

    system = platform.system()

    config = f'''# 字体配置文件 - 自动生成
# 系统: {system}
# 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

import matplotlib
matplotlib.rcParams['axes.unicode_minus'] = False
'''

    font_configs = {
        'Windows': {
            'primary': 'Microsoft YaHei',
            'fallbacks': ['SimHei', 'SimSun', 'FangSong', 'KaiTi', 'Arial']
        },
        'Darwin': {
            'primary': 'PingFang SC',
            'fallbacks': ['STHeiti', 'STSong', 'AppleGothic', 'Arial Unicode MS']
        },
        'Linux': {
            'primary': 'WenQuanYi Micro Hei',
            'fallbacks': ['DejaVu Sans', 'Noto Sans CJK SC', 'Arial']
        }
    }

    system_config = font_configs.get(system, font_configs['Linux'])

    config += f'''
# {system} 系统字体配置
font_names = {[system_config['primary']] + system_config['fallbacks']}
available_fonts = []

for font_name in font_names:
    try:
        font_path = matplotlib.font_manager.findfont(font_name)
        if font_path and 'none' not in font_path.lower():
            available_fonts.append(font_name)
    except:
        continue

if available_fonts:
    matplotlib.rcParams['font.sans-serif'] = available_fonts
    print(f"✅ 使用字体: {{available_fonts[0]}}")
else:
    print("⚠️  未找到中文字体，使用默认字体")
    matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans']
'''

    config_file = 'font_tests/font_config.py'

    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config)

    print(f"✅ 配置文件已生成: {config_file}")

    return config_file


def diagnose_common_issues():
    """诊断常见问题"""
    print("\n" + "=" * 60)
    print("🔍 常见问题诊断")
    print("=" * 60)

    issues = []

    current_fonts = matplotlib.rcParams.get('font.sans-serif', [])
    if not current_fonts or 'Microsoft YaHei' not in current_fonts and 'PingFang SC' not in current_fonts:
        issues.append("未配置中文字体")

    if not matplotlib.rcParams.get('axes.unicode_minus', True):
        issues.append("未设置unicode_minus参数")

    if issues:
        print("⚠️  发现以下问题:")
        for issue in issues:
            print(f"  ❌ {issue}")
    else:
        print("✅ 未发现常见问题")

    return issues


def main():
    """主函数"""
    print("🚀 中文字符显示测试工具")
    print("=" * 60)

    os.makedirs('font_tests', exist_ok=True)

    test_system_info()
    test_matplotlib_fonts()
    test_specific_chinese_fonts()
    test_database_charset()
    test_chinese_in_database()
    test_matplotlib_rendering()
    generate_font_config()
    test_visualization_pipeline()
    diagnose_common_issues()

    print("\n" + "=" * 60)
    print("🎉 所有测试完成！")
    print("=" * 60)
    print("📁 测试结果保存在 font_tests/ 目录")
    print("⚙️  使用 font_tests/font_config.py 配置您的项目")
    print("=" * 60)


if __name__ == "__main__":
    main()