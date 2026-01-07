# image_dao.py
"""
图片数据访问对象
处理图片的CRUD操作
"""

import uuid
from typing import List, Dict, Any, Optional, Tuple, BinaryIO
from pathlib import Path
from PIL import Image as PILImage

from database.db_connection import BaseConnection


class ImageDAO:
    """图片数据访问对象"""

    def __init__(self, base_storage_path: str = "medical_images"):
        """
        初始化ImageDAO

        Args:
            base_storage_path: 图片存储基础路径
        """
        self.db = BaseConnection()
        self.base_storage_path = Path(base_storage_path)

        # 创建存储目录
        self.original_dir = self.base_storage_path / "originals"
        self.thumbnails_dir = self.base_storage_path / "thumbnails"
        self.temp_dir = self.base_storage_path / "temp"

        for directory in [self.original_dir, self.thumbnails_dir, self.temp_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def _generate_filename(self, original_filename: str) -> Tuple[str, str]:
        """
        生成存储文件名

        Args:
            original_filename: 原始文件名

        Returns:
            (stored_filename, file_extension)
        """
        # 生成唯一文件名
        file_extension = Path(original_filename).suffix.lower()
        unique_id = uuid.uuid4().hex
        stored_filename = f"{unique_id}{file_extension}"

        return stored_filename, file_extension

    def save_image_file(self, file_stream: BinaryIO, original_filename: str) -> Tuple[str, int]:
        """
        保存图片文件到磁盘

        Args:
            file_stream: 文件流
            original_filename: 原始文件名

        Returns:
            (stored_filename, file_size)
        """
        # 生成存储文件名
        stored_filename, file_extension = self._generate_filename(original_filename)

        # 构建保存路径
        save_path = self.original_dir / stored_filename

        # 保存文件
        file_stream.seek(0)
        file_content = file_stream.read()
        file_size = len(file_content)

        with open(save_path, 'wb') as f:
            f.write(file_content)

        return stored_filename, file_size

    def create_thumbnail(self, image_path: Path, size: Tuple[int, int],
                         quality: int = 85) -> Tuple[Path, Tuple[int, int], int]:
        """
        创建缩略图

        Args:
            image_path: 原始图片路径
            size: 缩略图尺寸 (width, height)
            quality: 图片质量 (1-100)

        Returns:
            (thumbnail_path, (width, height), file_size)
        """
        try:
            # 打开原始图片
            with PILImage.open(image_path) as img:
                # 转换为RGB模式（如果是RGBA）
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')

                # 计算缩略图尺寸
                img.thumbnail(size, PILImage.Resampling.LANCZOS)

                # 生成缩略图文件名
                thumbnail_filename = f"{image_path.stem}_{size[0]}x{size[1]}.jpg"
                thumbnail_path = self.thumbnails_dir / thumbnail_filename

                # 保存缩略图
                img.save(thumbnail_path, 'JPEG', quality=quality, optimize=True)

                # 获取文件大小
                file_size = thumbnail_path.stat().st_size

                return thumbnail_path, img.size, file_size

        except Exception as e:
            raise Exception(f"创建缩略图失败: {e}")

    def get_cursor(self):
        """获取数据库游标"""
        return self.db.connection.cursor()

    def add_image(self, image_data: Dict[str, Any], file_stream: BinaryIO = None) -> int:
        """
        添加新图片

        Args:
            image_data: 图片信息字典
            file_stream: 文件流（可选，如果已保存文件）

        Returns:
            图片ID
        """
        try:
            self.db.connect()

            # 临时禁用外键检查
            cursor = self.get_cursor()
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

            # 获取文件信息
            original_filename = image_data.get('original_filename', '')
            mime_type = image_data.get('mime_type', '')

            if not original_filename or not mime_type:
                raise ValueError("文件名和文件类型是必填项")

            # 保存文件到磁盘
            if file_stream:
                stored_filename, file_size = self.save_image_file(file_stream, original_filename)
                file_path = str(self.original_dir / stored_filename)
            else:
                # 如果文件已保存，从image_data中获取
                stored_filename = image_data.get('stored_filename')
                file_path = image_data.get('file_path')
                file_size = image_data.get('file_size', 0)

                if not stored_filename or not file_path:
                    raise ValueError("文件信息不完整")

            # 获取图片尺寸
            image_width = image_data.get('image_width')
            image_height = image_data.get('image_height')

            if not image_width or not image_height:
                try:
                    with PILImage.open(file_path) as img:
                        image_width, image_height = img.size
                except:
                    image_width = image_height = 0

            # 构建SQL
            sql = """
            INSERT INTO medical_images (
                original_filename, stored_filename, file_path, file_size, mime_type,
                image_width, image_height, category_id, patient_id, visit_id, doctor_id,
                title, description, tags, is_public, uploaded_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            params = (
                original_filename,
                stored_filename,
                file_path,
                file_size,
                mime_type,
                image_width,
                image_height,
                image_data.get('category_id'),
                image_data.get('patient_id'),
                image_data.get('visit_id'),
                image_data.get('doctor_id'),
                image_data.get('title', ''),
                image_data.get('description', ''),
                image_data.get('tags', ''),
                image_data.get('is_public', False),
                image_data.get('uploaded_by')
            )

            # 执行插入
            cursor = self.get_cursor()
            cursor.execute(sql, params)
            image_id = cursor.lastrowid

            # 创建缩略图
            if image_id and file_path:
                self.create_image_thumbnails(image_id, Path(file_path))

            # 在提交前重新启用外键
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            self.db.connection.commit()  # 修正：通过db.connection访问
            return image_id

        except Exception as e:
            if hasattr(self.db, 'connection') and self.db.connection:
                try:
                    cursor = self.get_cursor()
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                    self.db.connection.rollback()
                except:
                    pass
            raise Exception(f"添加图片失败: {e}")
        finally:
            self.db.close()

    def create_image_thumbnails(self, image_id: int, image_path: Path):
        """为图片创建缩略图"""
        try:
            # 缩略图尺寸配置
            thumbnail_sizes = {
                'small': (150, 150),
                'medium': (300, 300),
                'large': (600, 600)
            }

            for size_name, size in thumbnail_sizes.items():
                thumbnail_path, (width, height), file_size = self.create_thumbnail(
                    image_path, size
                )

                # 保存缩略图信息到数据库
                sql = """
                INSERT INTO image_thumbnails 
                (image_id, thumbnail_size, thumbnail_path, width, height, file_size)
                VALUES (%s, %s, %s, %s, %s, %s)
                """

                params = (
                    image_id,
                    size_name,
                    str(thumbnail_path),
                    width,
                    height,
                    file_size
                )

                cursor = self.get_cursor()
                cursor.execute(sql, params)

        except Exception as e:
            print(f"创建缩略图失败: {e}")

    def get_image_by_id(self, image_id: int) -> Optional[Dict]:
        """根据ID获取图片信息"""
        try:
            self.db.connect()

            sql = """
            SELECT 
                mi.*,
                ic.category_name,
                p.name as patient_name,
                d.name as doctor_name,
                u.username as uploader_name
            FROM medical_images mi
            LEFT JOIN image_categories ic ON mi.category_id = ic.category_id
            LEFT JOIN patients p ON mi.patient_id = p.patient_id
            LEFT JOIN doctors d ON mi.doctor_id = d.doctor_id
            LEFT JOIN users u ON mi.uploaded_by = u.user_id
            WHERE mi.image_id = %s AND mi.is_deleted = 0
            """

            result = self.db.execute(sql, (image_id,), fetch_one=True)
            return result

        except Exception as e:
            raise Exception(f"获取图片失败: {e}")
        finally:
            self.db.close()

    def get_patient_images(self, patient_id: int, page: int = 1,
                           page_size: int = 20) -> Tuple[List[Dict], int]:
        """获取患者的图片"""
        try:
            self.db.connect()

            # 计算偏移量
            offset = (page - 1) * page_size

            # 查询图片列表
            sql = """
            SELECT 
                mi.*,
                ic.category_name,
                d.name as doctor_name
            FROM medical_images mi
            LEFT JOIN image_categories ic ON mi.category_id = ic.category_id
            LEFT JOIN doctors d ON mi.doctor_id = d.doctor_id
            WHERE mi.patient_id = %s AND mi.is_deleted = 0
            ORDER BY mi.upload_time DESC
            LIMIT %s OFFSET %s
            """

            results = self.db.execute(sql, (patient_id, page_size, offset), fetch_all=True)

            # 查询总数
            count_sql = """
            SELECT COUNT(*) as total 
            FROM medical_images 
            WHERE patient_id = %s AND is_deleted = 0
            """
            count_result = self.db.execute(count_sql, (patient_id,), fetch_one=True)
            total = count_result.get('total', 0) if count_result else 0

            return results, total

        except Exception as e:
            raise Exception(f"获取患者图片失败: {e}")
        finally:
            self.db.close()

    def get_visit_images(self, visit_id: int) -> List[Dict]:
        """获取就诊记录的图片"""
        try:
            self.db.connect()

            sql = """
            SELECT 
                mi.*,
                ic.category_name
            FROM medical_images mi
            LEFT JOIN image_categories ic ON mi.category_id = ic.category_id
            WHERE mi.visit_id = %s AND mi.is_deleted = 0
            ORDER BY mi.upload_time DESC
            """

            results = self.db.execute(sql, (visit_id,), fetch_all=True)
            return results

        except Exception as e:
            raise Exception(f"获取就诊图片失败: {e}")
        finally:
            self.db.close()

    def update_image_info(self, image_id: int, update_data: Dict[str, Any]) -> bool:
        """更新图片信息"""
        try:
            self.db.connect()

            # 构建更新语句
            set_clauses = []
            params = []

            for field, value in update_data.items():
                if field in ['title', 'description', 'tags', 'category_id',
                             'is_public', 'patient_id', 'visit_id', 'doctor_id']:
                    set_clauses.append(f"{field} = %s")
                    params.append(value)

            if not set_clauses:
                return False

            params.append(image_id)

            sql = f"""
            UPDATE medical_images 
            SET {', '.join(set_clauses)}
            WHERE image_id = %s AND is_deleted = 0
            """

            cursor = self.get_cursor()
            affected_rows = cursor.execute(sql, params)

            self.db.connection.commit()  # 修正：通过db.connection访问
            return affected_rows > 0

        except Exception as e:
            if hasattr(self.db, 'connection') and self.db.connection:
                self.db.connection.rollback()
            raise Exception(f"更新图片信息失败: {e}")
        finally:
            self.db.close()

    def delete_image(self, image_id: int, soft_delete: bool = True) -> bool:
        """删除图片"""
        try:
            self.db.connect()

            if soft_delete:
                # 软删除：标记为已删除
                sql = "UPDATE medical_images SET is_deleted = 1 WHERE image_id = %s"
                cursor = self.get_cursor()
                affected_rows = cursor.execute(sql, (image_id,))
            else:
                # 硬删除：从数据库和文件系统中删除
                # 先获取图片信息
                image_info = self.get_image_by_id(image_id)
                if not image_info:
                    return False

                # 删除数据库记录
                sql = "DELETE FROM medical_images WHERE image_id = %s"
                cursor = self.get_cursor()
                affected_rows = cursor.execute(sql, (image_id,))

                # 删除文件
                if affected_rows > 0:
                    self._delete_image_files(image_info)

            self.db.connection.commit()  # 修正：通过db.connection访问
            return affected_rows > 0

        except Exception as e:
            if hasattr(self.db, 'connection') and self.db.connection:
                self.db.connection.rollback()
            raise Exception(f"删除图片失败: {e}")
        finally:
            self.db.close()

    def _delete_image_files(self, image_info: Dict):
        """删除图片文件"""
        try:
            # 删除原始文件
            original_path = Path(image_info.get('file_path', ''))
            if original_path.exists():
                original_path.unlink()

            # 删除缩略图
            sql = "SELECT thumbnail_path FROM image_thumbnails WHERE image_id = %s"
            thumbnails = self.db.execute(sql, (image_info['image_id'],), fetch_all=True)

            for thumb in thumbnails:
                thumb_path = Path(thumb.get('thumbnail_path', ''))
                if thumb_path.exists():
                    thumb_path.unlink()

            # 删除缩略图记录
            delete_sql = "DELETE FROM image_thumbnails WHERE image_id = %s"
            self.db.execute(delete_sql, (image_info['image_id'],))

        except Exception as e:
            print(f"删除文件失败: {e}")

    def get_categories(self) -> List[Dict]:
        """获取所有图片分类"""
        try:
            self.db.connect()

            sql = "SELECT * FROM image_categories ORDER BY category_name"
            results = self.db.execute(sql, fetch_all=True)
            return results

        except Exception as e:
            raise Exception(f"获取分类失败: {e}")
        finally:
            self.db.close()

    def search_images(self, search_criteria: Dict, page: int = 1,
                      page_size: int = 20) -> Tuple[List[Dict], int]:
        """搜索图片"""
        try:
            self.db.connect()

            # 构建查询条件
            conditions = ["mi.is_deleted = 0"]
            params = []

            if search_criteria.get('patient_id'):
                conditions.append("mi.patient_id = %s")
                params.append(search_criteria['patient_id'])

            if search_criteria.get('category_id'):
                conditions.append("mi.category_id = %s")
                params.append(search_criteria['category_id'])

            if search_criteria.get('doctor_id'):
                conditions.append("mi.doctor_id = %s")
                params.append(search_criteria['doctor_id'])

            if search_criteria.get('visit_id'):
                conditions.append("mi.visit_id = %s")
                params.append(search_criteria['visit_id'])

            if search_criteria.get('keyword'):
                keyword = f"%{search_criteria['keyword']}%"
                conditions.append("""
                (mi.title LIKE %s OR mi.description LIKE %s OR mi.tags LIKE %s 
                 OR mi.original_filename LIKE %s)
                """)
                params.extend([keyword, keyword, keyword, keyword])

            if search_criteria.get('start_date'):
                conditions.append("mi.upload_time >= %s")
                params.append(search_criteria['start_date'])

            if search_criteria.get('end_date'):
                conditions.append("mi.upload_time <= %s")
                params.append(search_criteria['end_date'])

            if search_criteria.get('is_public') is not None:
                conditions.append("mi.is_public = %s")
                params.append(search_criteria['is_public'])

            # 计算偏移量
            offset = (page - 1) * page_size

            # 查询数据
            where_clause = " AND ".join(conditions) if conditions else "1=1"

            sql = f"""
            SELECT 
                mi.*,
                ic.category_name,
                p.name as patient_name,
                d.name as doctor_name
            FROM medical_images mi
            LEFT JOIN image_categories ic ON mi.category_id = ic.category_id
            LEFT JOIN patients p ON mi.patient_id = p.patient_id
            LEFT JOIN doctors d ON mi.doctor_id = d.doctor_id
            WHERE {where_clause}
            ORDER BY mi.upload_time DESC
            LIMIT %s OFFSET %s
            """

            params.extend([page_size, offset])
            results = self.db.execute(sql, params, fetch_all=True)

            # 查询总数
            count_sql = f"""
            SELECT COUNT(*) as total 
            FROM medical_images mi
            WHERE {where_clause}
            """
            count_params = params[:-2]  # 移除LIMIT和OFFSET参数
            count_result = self.db.execute(count_sql, count_params, fetch_one=True)
            total = count_result.get('total', 0) if count_result else 0

            return results, total

        except Exception as e:
            raise Exception(f"搜索图片失败: {e}")
        finally:
            self.db.close()