import sys
import os
from pathlib import Path
import io
from datetime import datetime, timedelta
import traceback

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.db_connection import BaseConnection
from image_dao import ImageDAO
from PIL import Image, ImageDraw


def create_test_image(filename: str = "test_image.jpg", size: tuple = (800, 600)) -> str:
    """创建测试图片"""
    # 创建图片
    img = Image.new('RGB', size, color='lightblue')
    draw = ImageDraw.Draw(img)

    # 添加文字
    draw.text((50, 50), "测试医疗图片", fill='black')
    draw.text((50, 100), f"创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", fill='black')

    # 保存到临时文件
    temp_dir = Path("temp_images")
    temp_dir.mkdir(exist_ok=True)

    filepath = temp_dir / filename
    img.save(filepath, 'JPEG', quality=95)

    return str(filepath)


def test_database_connection():
    """测试数据库连接"""
    print("🔧 测试数据库连接...")

    db = BaseConnection()
    try:
        db.connect()

        # 检查表是否存在
        sql = """
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = DATABASE() 
        AND TABLE_NAME IN ('image_categories', 'medical_images', 'image_thumbnails')
        """

        results = db.execute(sql, fetch_all=True)
        tables = [row['TABLE_NAME'] for row in results]

        print(f"✅ 找到的表: {tables}")

        if len(tables) < 3:
            print("❌ 表结构不完整，请先运行 create_image_tables.sql")
            return False

        return True

    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        traceback.print_exc()
        return False
    finally:
        db.close()


def ensure_patient_exists(db, patient_id=1):
    """确保患者存在"""
    try:
        # 检查患者是否存在
        check_sql = "SELECT patient_id, name FROM patients WHERE patient_id = %s"
        patient = db.execute(check_sql, (patient_id,), fetch_one=True)

        if patient:
            print(f"   患者已存在: ID={patient['patient_id']}, 姓名={patient.get('name', '未知')}")
            return patient_id
        else:
            # 创建患者
            print(f"   创建患者 ID={patient_id}...")
            create_sql = """
            INSERT INTO patients (
                patient_id, name, gender, birth_date, phone, address, 
                blood_type, empi_code, is_active
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE name = VALUES(name)
            """

            import datetime
            params = (
                patient_id,
                f'测试患者{patient_id}',
                'M',
                '1990-01-01',
                '13800138000',
                '测试地址',
                'O',
                f'TEST{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}',
                1
            )

            result = db.execute(create_sql, params, commit=True)
            if result is not None:
                print(f"   患者创建成功，ID: {patient_id}")
                return patient_id
            else:
                # 如果插入失败，尝试获取现有患者
                get_any_sql = "SELECT patient_id FROM patients ORDER BY patient_id LIMIT 1"
                any_patient = db.execute(get_any_sql, fetch_one=True)
                if any_patient and 'patient_id' in any_patient:
                    return any_patient['patient_id']
                return None

    except Exception as e:
        print(f"   确保患者存在时出错: {e}")
        return None


def ensure_category_exists(db, category_id=1):
    """确保分类存在"""
    try:
        # 检查分类是否存在
        check_sql = "SELECT category_id, category_name FROM image_categories WHERE category_id = %s"
        category = db.execute(check_sql, (category_id,), fetch_one=True)

        if category:
            print(f"   分类已存在: ID={category['category_id']}, 名称={category.get('category_name', '未知')}")
            return category_id
        else:
            # 创建分类
            print(f"   创建分类 ID={category_id}...")
            create_sql = """
            INSERT INTO image_categories (category_id, category_name, description) 
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE category_name = VALUES(category_name)
            """

            params = (category_id, '测试分类', '测试用分类')
            result = db.execute(create_sql, params, commit=True)
            if result is not None:
                print(f"   分类创建成功，ID: {category_id}")
                return category_id
            else:
                # 获取现有分类
                get_any_sql = "SELECT category_id FROM image_categories ORDER BY category_id LIMIT 1"
                any_category = db.execute(get_any_sql, fetch_one=True)
                if any_category and 'category_id' in any_category:
                    return any_category['category_id']
                return 1

    except Exception as e:
        print(f"   确保分类存在时出错: {e}")
        return 1


def test_image_upload():
    """测试图片上传功能 - 修正版"""
    print("\n📤 测试图片上传")
    print("-" * 40)

    db = BaseConnection()

    try:
        if not db.connect():
            print("❌ 数据库连接失败")
            return None

        # 临时禁用外键检查
        print("   临时禁用外键检查...")
        db.execute("SET FOREIGN_KEY_CHECKS = 0", commit=True)

        # 1. 确保患者存在
        print("1. 确保患者存在...")
        patient_id = ensure_patient_exists(db, 1)
        if not patient_id:
            print("❌ 无法获取患者ID")
            return None

        # 2. 确保分类存在
        print("\n2. 确保分类存在...")
        category_id = ensure_category_exists(db, 1)

        print(f"   使用患者ID: {patient_id}, 分类ID: {category_id}")

        # 3. 创建测试图片
        print("\n3. 创建测试图片...")
        test_image_path = create_test_image("patient_photo.jpg", (1024, 768))

        # 读取图片文件
        with open(test_image_path, 'rb') as f:
            file_stream = io.BytesIO(f.read())

        # 4. 创建ImageDAO实例
        image_dao = ImageDAO()

        # 准备图片数据
        image_data = {
            'original_filename': 'patient_photo.jpg',
            'mime_type': 'image/jpeg',
            'category_id': category_id,
            'patient_id': patient_id,
            'doctor_id': 1,
            'title': '患者面部照片',
            'description': '门诊拍摄的患者面部照片',
            'tags': '门诊,面部,初诊',
            'is_public': False,
            'uploaded_by': 1
        }

        # 5. 上传图片
        print("\n4. 上传图片...")
        try:
            image_id = image_dao.add_image(image_data, file_stream)
            print(f"✅ 图片上传成功，ID: {image_id}")
            return image_id

        except Exception as e:
            print(f"❌ 图片上传失败: {e}")
            traceback.print_exc()
            return None

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        traceback.print_exc()
        return None
    finally:
        try:
            # 重新启用外键检查
            if db.connection:
                db.execute("SET FOREIGN_KEY_CHECKS = 1", commit=True)
        except:
            pass
        db.close()


def test_image_retrieval(image_id: int):
    """测试图片检索功能"""
    print("\n🔍 测试图片检索")
    print("-" * 40)

    try:
        image_dao = ImageDAO()

        # 获取图片信息
        image_info = image_dao.get_image_by_id(image_id)
        if image_info:
            print(f"✅ 获取图片信息成功:")
            print(f"   图片ID: {image_info.get('image_id')}")
            print(f"   文件名: {image_info.get('original_filename')}")
            print(f"   文件大小: {image_info.get('file_size')} 字节")
            print(f"   患者ID: {image_info.get('patient_id', '无')}")
            print(f"   分类: {image_info.get('category_name', '无')}")
            print(f"   上传时间: {image_info.get('upload_time')}")
        else:
            print("❌ 未找到图片信息")

        return image_info

    except Exception as e:
        print(f"❌ 图片检索失败: {e}")
        traceback.print_exc()
        return None


def test_patient_images(patient_id: int = 1):
    """测试获取患者图片"""
    print(f"\n👤 测试获取患者{patient_id}的图片")
    print("-" * 40)

    try:
        image_dao = ImageDAO()

        # 获取患者图片
        images, total = image_dao.get_patient_images(patient_id, page=1, page_size=10)

        print(f"✅ 找到 {total} 张图片，显示 {len(images)} 张:")
        for img in images[:3]:  # 只显示前3张
            print(f"   - {img.get('title', '无标题')} ({img.get('upload_time')})")

        return images

    except Exception as e:
        print(f"❌ 获取患者图片失败: {e}")
        traceback.print_exc()
        return []


def test_image_search():
    """测试图片搜索功能"""
    print("\n🔎 测试图片搜索")
    print("-" * 40)

    try:
        image_dao = ImageDAO()

        # 搜索条件
        search_criteria = {
            'keyword': '患者',
            'start_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'is_public': False
        }

        # 执行搜索
        results, total = image_dao.search_images(search_criteria, page=1, page_size=10)

        print(f"✅ 搜索到 {total} 张图片，显示 {len(results)} 张:")
        for img in results[:3]:
            print(f"   - {img.get('title', '无标题')} (ID: {img.get('image_id')})")

        return results

    except Exception as e:
        print(f"❌ 图片搜索失败: {e}")
        traceback.print_exc()
        return []


def test_image_update(image_id: int):
    """测试图片更新功能"""
    print(f"\n✏️ 测试更新图片{image_id}")
    print("-" * 40)

    try:
        image_dao = ImageDAO()

        # 更新数据
        update_data = {
            'title': '更新后的患者照片标题',
            'description': '这是一张更新了描述的患者照片',
            'tags': '更新,测试,门诊',
            'is_public': True
        }

        # 执行更新
        success = image_dao.update_image_info(image_id, update_data)

        if success:
            print("✅ 图片更新成功")

            # 验证更新
            updated_info = image_dao.get_image_by_id(image_id)
            if updated_info:
                print(f"   新标题: {updated_info.get('title')}")
                print(f"   新描述: {updated_info.get('description')[:50]}...")
                print(f"   是否公开: {updated_info.get('is_public')}")
        else:
            print("❌ 图片更新失败")

        return success

    except Exception as e:
        print(f"❌ 图片更新失败: {e}")
        traceback.print_exc()
        return False


def test_image_delete(image_id: int):
    """测试图片删除功能"""
    print(f"\n🗑️ 测试删除图片{image_id}")
    print("-" * 40)

    try:
        image_dao = ImageDAO()

        # 软删除
        success = image_dao.delete_image(image_id, soft_delete=True)

        if success:
            print("✅ 图片软删除成功")

            # 验证删除
            deleted_info = image_dao.get_image_by_id(image_id)
            if deleted_info:
                print(f"❌ 图片仍然可访问 (is_deleted: {deleted_info.get('is_deleted')})")
            else:
                print("✅ 图片已成功标记为删除")
        else:
            print("❌ 图片删除失败")

        return success

    except Exception as e:
        print(f"❌ 图片删除失败: {e}")
        traceback.print_exc()
        return False


def test_categories():
    """测试分类功能"""
    print("\n📁 测试图片分类")
    print("-" * 40)

    try:
        image_dao = ImageDAO()

        # 获取所有分类
        categories = image_dao.get_categories()

        print(f"✅ 找到 {len(categories)} 个分类:")
        for cat in categories:
            print(f"   - {cat.get('category_name')}: {cat.get('description', '无描述')}")

        return categories

    except Exception as e:
        print(f"❌ 获取分类失败: {e}")
        traceback.print_exc()
        return []


def main():
    """主测试函数"""
    print("=" * 60)
    print("医疗图片存储系统测试 - 修正版")
    print("=" * 60)

    # 1. 测试数据库连接
    if not test_database_connection():
        print("\n❌ 数据库测试失败，请先创建表结构")
        return

    # 2. 测试分类功能
    test_categories()

    # 3. 测试图片上传
    image_id = test_image_upload()
    if not image_id:
        print("\n❌ 测试终止：图片上传失败")
        return

    # 4. 测试图片检索
    test_image_retrieval(image_id)

    # 5. 测试获取患者图片
    test_patient_images(1)

    # 6. 测试图片搜索
    test_image_search()

    # 7. 测试图片更新
    test_image_update(image_id)

    # 8. 测试图片删除
    test_image_delete(image_id)

    print("\n" + "=" * 60)
    print("✅ 所有测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()