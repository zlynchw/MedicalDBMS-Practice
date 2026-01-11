"""
图片上传问题综合测试脚本
"""

import os
from database.db_connection import BaseConnection


def test_directory_permissions():
    """测试目录权限"""
    print("🔍 测试目录权限...")

    test_dirs = [
        'medical_images',
        'medical_images/originals',
        'medical_images/thumbnails',
        'medical_images/temp'
    ]

    for dir_path in test_dirs:
        try:
            # 创建目录（如果不存在）
            os.makedirs(dir_path, exist_ok=True)

            # 测试写入
            test_file = os.path.join(dir_path, '.write_test')
            with open(test_file, 'w') as f:
                f.write('test')

            os.remove(test_file)
            print(f"  ✅ {dir_path}: 可写入")

        except PermissionError:
            print(f"  ❌ {dir_path}: 无写入权限")
        except Exception as e:
            print(f"  ❌ {dir_path}: 错误 - {e}")


def test_patient_exists(patient_id=1):
    """测试患者是否存在"""
    print(f"\n🔍 测试患者ID {patient_id} 是否存在...")

    db = BaseConnection()
    try:
        db.connect()

        sql = "SELECT patient_id, name FROM patients WHERE patient_id = %s"
        result = db.execute(sql, (patient_id,), fetch_one=True)

        if result:
            print(f"  ✅ 患者存在: {result['name']} (ID: {result['patient_id']})")
            return True
        else:
            print(f"  ❌ 患者ID {patient_id} 不存在")

            # 显示所有患者
            sql_all = "SELECT patient_id, name FROM patients ORDER BY patient_id LIMIT 5"
            results = db.execute(sql_all, fetch_all=True)
            if results:
                print(f"  📋 可用患者列表:")
                for row in results:
                    print(f"    {row['patient_id']}: {row['name']}")
            else:
                print(f"  📭 数据库中无患者记录")

            return False

    except Exception as e:
        print(f"  ❌ 查询失败: {e}")
        return False
    finally:
        db.close()


def test_file_size_limits(file_path):
    """测试文件大小限制"""
    print(f"\n🔍 测试文件大小: {file_path}")

    try:
        if not os.path.exists(file_path):
            print(f"  ❌ 文件不存在")
            return False

        size = os.path.getsize(file_path)
        size_mb = size / (1024 * 1024)

        print(f"  📊 文件大小: {size:,} 字节 ({size_mb:.2f} MB)")

        # 检查限制
        max_size_mb = 10  # 假设10MB限制
        if size_mb > max_size_mb:
            print(f"  ❌ 文件过大: {size_mb:.2f} MB > {max_size_mb} MB")
            return False
        else:
            print(f"  ✅ 文件大小在限制内")
            return True

    except Exception as e:
        print(f"  ❌ 检查失败: {e}")
        return False


def test_mysql_settings():
    """测试MySQL配置"""
    print(f"\n🔍 测试MySQL配置...")

    db = BaseConnection()
    try:
        db.connect()

        # 检查最大包大小
        sql = "SHOW VARIABLES LIKE 'max_allowed_packet'"
        result = db.execute(sql, fetch_one=True)

        if result:
            value = int(result['Value'])
            value_mb = value / (1024 * 1024)
            print(f"  📊 max_allowed_packet: {value:,} 字节 ({value_mb:.2f} MB)")

            if value_mb < 10:
                print(f"  ⚠️  建议设置: SET GLOBAL max_allowed_packet = 10485760;")

    except Exception as e:
        print(f"  ❌ 查询失败: {e}")
    finally:
        db.close()


def create_test_image():
    """创建测试图片"""
    print(f"\n🔧 创建测试图片...")

    test_dir = 'temp_images'
    os.makedirs(test_dir, exist_ok=True)

    test_path = os.path.join(test_dir, 'test_upload.jpg')

    try:
        from PIL import Image, ImageDraw

        # 创建测试图片
        img = Image.new('RGB', (800, 600), color='blue')
        draw = ImageDraw.Draw(img)
        draw.text((100, 300), '医疗图片测试', fill='white', size=50)
        draw.text((100, 350), '测试文件上传功能', fill='white', size=30)

        img.save(test_path, quality=85)
        print(f"  ✅ 创建测试图片: {test_path}")
        return test_path

    except ImportError:
        print("  ⚠️  Pillow未安装，跳过创建测试图片")
        print("    运行: pip install pillow")
        return None
    except Exception as e:
        print(f"  ❌ 创建失败: {e}")
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("📸 图片上传问题综合测试")
    print("=" * 60)

    # 测试目录权限
    test_directory_permissions()

    # 测试患者存在
    test_patient_exists(1)  # 测试ID为1的患者

    # 创建并测试图片
    test_image = create_test_image()
    if test_image:
        test_file_size_limits(test_image)

    # 测试MySQL设置
    test_mysql_settings()

    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)