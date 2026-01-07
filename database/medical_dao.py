"""
医疗系统数据访问对象
封装业务相关的数据库操作
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date
import logging
from .db_connection import BaseConnection
from .db_config import DatabaseConfig, DEFAULT_CONFIG

logger = logging.getLogger(__name__)


class MedicalDAO(BaseConnection):
    """医疗系统数据访问对象"""

    def __init__(self, config: DatabaseConfig = None):
        """
        初始化医疗DAO

        Args:
            config: 数据库配置
        """
        super().__init__(config or DEFAULT_CONFIG)

    # ==================== 患者管理 ====================

    def get_patient_by_id(self, patient_id: int) -> Optional[Dict]:
        """根据ID获取患者信息"""
        return self.select_one(
            "patients",
            condition="patient_id = %s",
            params=(patient_id,)
        )

    def get_patient_by_empi(self, empi_code: str) -> Optional[Dict]:
        """根据EMPI编码获取患者信息"""
        return self.select_one(
            "patients",
            condition="empi_code = %s",
            params=(empi_code,)
        )

    def search_patients(self, keyword: str = None,
                        gender: str = None,
                        blood_type: str = None,
                        page: int = 1,
                        page_size: int = 20) -> Tuple[List[Dict], int]:
        """
        搜索患者

        Args:
            keyword: 搜索关键词（姓名、手机、身份证）
            gender: 性别
            blood_type: 血型
            page: 页码
            page_size: 每页数量

        Returns:
            (患者列表, 总数量)
        """
        conditions = []
        params = []

        if keyword:
            conditions.append("(name LIKE %s OR phone LIKE %s OR id_card LIKE %s)")
            like_keyword = f"%{keyword}%"
            params.extend([like_keyword, like_keyword, like_keyword])

        if gender:
            conditions.append("gender = %s")
            params.append(gender)

        if blood_type:
            conditions.append("blood_type = %s")
            params.append(blood_type)

        where_clause = " AND ".join(conditions) if conditions else None

        # 计算总数
        total = self.count("patients", where_clause, tuple(params))

        # 分页查询
        offset = (page - 1) * page_size
        order_by = "created_at DESC"

        patients = self.select(
            "patients",
            condition=where_clause,
            params=tuple(params),
            order_by=order_by,
            limit=page_size,
            offset=offset
        )

        return patients, total

    def create_patient(self, patient_data: Dict[str, Any]) -> int:
        """
        创建患者

        Args:
            patient_data: 患者数据

        Returns:
            患者ID
        """
        # 设置默认值
        now = datetime.now()
        patient_data.setdefault("created_at", now)
        patient_data.setdefault("updated_at", now)

        return self.insert("patients", patient_data)

    def update_patient(self, patient_id: int, patient_data: Dict[str, Any]) -> bool:
        """
        更新患者信息

        Args:
            patient_id: 患者ID
            patient_data: 更新数据

        Returns:
            是否成功
        """
        patient_data["updated_at"] = datetime.now()

        affected = self.update(
            "patients",
            patient_data,
            condition="patient_id = %s",
            params=(patient_id,)
        )

        return affected > 0

    # ==================== 医生管理 ====================

    def get_doctor_by_id(self, doctor_id: int) -> Optional[Dict]:
        """根据ID获取医生信息"""
        sql = """
        SELECT d.*, dep.department_name, h.hospital_name
        FROM doctors d
        LEFT JOIN departments dep ON d.department_id = dep.department_id
        LEFT JOIN hospitals h ON d.hospital_id = h.hospital_id
        WHERE d.doctor_id = %s
        """

        return self.execute(sql, (doctor_id,), fetch_one=True)

    def get_doctors_by_department(self, department_id: int) -> List[Dict]:
        """获取科室下的医生列表"""
        return self.select(
            "doctors",
            condition="department_id = %s",
            params=(department_id,),
            order_by="title DESC, name ASC"
        )

    def search_doctors(self, keyword: str = None,
                       department_id: int = None,
                       title: str = None,
                       page: int = 1,
                       page_size: int = 20) -> Tuple[List[Dict], int]:
        """
        搜索医生

        Args:
            keyword: 搜索关键词（姓名、工号）
            department_id: 科室ID
            title: 职称
            page: 页码
            page_size: 每页数量

        Returns:
            (医生列表, 总数量)
        """
        conditions = []
        params = []

        if keyword:
            conditions.append("(d.name LIKE %s OR d.doctor_number LIKE %s)")
            like_keyword = f"%{keyword}%"
            params.extend([like_keyword, like_keyword])

        if department_id:
            conditions.append("d.department_id = %s")
            params.append(department_id)

        if title:
            conditions.append("d.title = %s")
            params.append(title)

        where_clause = " AND ".join(conditions) if conditions else None

        # 基础查询
        base_sql = """
        FROM doctors d
        LEFT JOIN departments dep ON d.department_id = dep.department_id
        LEFT JOIN hospitals h ON d.hospital_id = h.hospital_id
        """

        if where_clause:
            base_sql += f" WHERE {where_clause}"

        # 计算总数
        count_sql = f"SELECT COUNT(*) as count {base_sql}"
        result = self.execute(count_sql, tuple(params), fetch_one=True)
        total = result.get("count", 0) if result else 0

        # 分页查询
        select_sql = f"""
        SELECT d.*, dep.department_name, h.hospital_name 
        {base_sql}
        ORDER BY d.title DESC, d.name ASC
        LIMIT %s OFFSET %s
        """

        offset = (page - 1) * page_size
        params_with_paging = tuple(list(params) + [page_size, offset])

        doctors = self.execute(select_sql, params_with_paging, fetch_all=True)

        return doctors, total

    # ==================== 就诊管理 ====================

    def get_visit_by_id(self, visit_id: int) -> Optional[Dict]:
        """根据ID获取就诊记录"""
        sql = """
        SELECT 
            mv.*, 
            p.name as patient_name, p.gender as patient_gender, p.birth_date as patient_birth_date,
            d.name as doctor_name, d.title as doctor_title,
            dep.department_name
        FROM medical_visits mv
        JOIN patients p ON mv.patient_id = p.patient_id
        JOIN doctors d ON mv.doctor_id = d.doctor_id
        LEFT JOIN departments dep ON d.department_id = dep.department_id
        WHERE mv.visit_id = %s
        """

        return self.execute(sql, (visit_id,), fetch_one=True)

    def get_patient_visits(self, patient_id: int,
                           start_date: date = None,
                           end_date: date = None,
                           page: int = 1,
                           page_size: int = 20) -> Tuple[List[Dict], int]:
        """
        获取患者的就诊记录

        Args:
            patient_id: 患者ID
            start_date: 开始日期
            end_date: 结束日期
            page: 页码
            page_size: 每页数量

        Returns:
            (就诊记录列表, 总数量)
        """
        conditions = ["mv.patient_id = %s"]
        params = [patient_id]

        if start_date:
            conditions.append("mv.visit_date >= %s")
            params.append(start_date)

        if end_date:
            conditions.append("mv.visit_date <= %s")
            params.append(end_date)

        where_clause = " AND ".join(conditions)

        # 计算总数
        count_sql = f"""
        SELECT COUNT(*) as count
        FROM medical_visits mv
        WHERE {where_clause}
        """

        result = self.execute(count_sql, tuple(params), fetch_one=True)
        total = result.get("count", 0) if result else 0

        # 分页查询
        select_sql = f"""
        SELECT 
            mv.*, 
            d.name as doctor_name, d.title as doctor_title,
            dep.department_name, h.hospital_name
        FROM medical_visits mv
        JOIN doctors d ON mv.doctor_id = d.doctor_id
        LEFT JOIN departments dep ON d.department_id = dep.department_id
        LEFT JOIN hospitals h ON d.hospital_id = h.hospital_id
        WHERE {where_clause}
        ORDER BY mv.visit_date DESC, mv.visit_time DESC
        LIMIT %s OFFSET %s
        """

        offset = (page - 1) * page_size
        params_with_paging = tuple(list(params) + [page_size, offset])

        visits = self.execute(select_sql, params_with_paging, fetch_all=True)

        return visits, total

    def get_doctor_visits(self, doctor_id: int,
                          visit_date: date = None,
                          page: int = 1,
                          page_size: int = 20) -> Tuple[List[Dict], int]:
        """
        获取医生的就诊记录

        Args:
            doctor_id: 医生ID
            visit_date: 就诊日期
            page: 页码
            page_size: 每页数量

        Returns:
            (就诊记录列表, 总数量)
        """
        conditions = ["mv.doctor_id = %s"]
        params = [doctor_id]

        if visit_date:
            conditions.append("mv.visit_date = %s")
            params.append(visit_date)

        where_clause = " AND ".join(conditions)

        # 计算总数
        count_sql = f"""
        SELECT COUNT(*) as count
        FROM medical_visits mv
        WHERE {where_clause}
        """

        result = self.execute(count_sql, tuple(params), fetch_one=True)
        total = result.get("count", 0) if result else 0

        # 分页查询
        select_sql = f"""
        SELECT 
            mv.*, 
            p.name as patient_name, p.gender as patient_gender,
            p.birth_date as patient_birth_date, p.phone as patient_phone
        FROM medical_visits mv
        JOIN patients p ON mv.patient_id = p.patient_id
        WHERE {where_clause}
        ORDER BY mv.visit_time DESC
        LIMIT %s OFFSET %s
        """

        offset = (page - 1) * page_size
        params_with_paging = tuple(list(params) + [page_size, offset])

        visits = self.execute(select_sql, params_with_paging, fetch_all=True)

        return visits, total

    def create_visit(self, visit_data: Dict[str, Any]) -> int:
        """
        创建就诊记录

        Args:
            visit_data: 就诊数据

        Returns:
            就诊记录ID
        """
        # 设置默认值
        now = datetime.now()
        if "visit_date" not in visit_data:
            visit_data["visit_date"] = now.date()
        if "visit_time" not in visit_data:
            visit_data["visit_time"] = now.time()
        if "created_at" not in visit_data:
            visit_data["created_at"] = now

        return self.insert("medical_visits", visit_data)

    def update_visit_diagnosis(self, visit_id: int, diagnosis: str,
                               treatment_plan: str = None) -> bool:
        """
        更新就诊诊断

        Args:
            visit_id: 就诊ID
            diagnosis: 诊断
            treatment_plan: 治疗方案

        Returns:
            是否成功
        """
        update_data = {
            "diagnosis": diagnosis,
            "updated_at": datetime.now()
        }

        if treatment_plan:
            update_data["treatment_plan"] = treatment_plan

        affected = self.update(
            "medical_visits",
            update_data,
            condition="visit_id = %s",
            params=(visit_id,)
        )

        return affected > 0

    # ==================== 检查管理 ====================

    def get_examination_by_id(self, exam_id: int) -> Optional[Dict]:
        """根据ID获取检查记录"""
        sql = """
        SELECT 
            er.*,
            ei.item_name, ei.item_category, ei.normal_range, ei.unit,
            mv.visit_date, mv.diagnosis,
            p.name as patient_name, p.patient_id,
            d.name as doctor_name, d.title as doctor_title
        FROM examination_records er
        JOIN examination_items ei ON er.item_id = ei.item_id
        JOIN medical_visits mv ON er.visit_id = mv.visit_id
        JOIN patients p ON mv.patient_id = p.patient_id
        JOIN doctors d ON mv.doctor_id = d.doctor_id
        WHERE er.exam_id = %s
        """

        return self.execute(sql, (exam_id,), fetch_one=True)

    def get_visit_examinations(self, visit_id: int) -> List[Dict]:
        """获取就诊的检查记录"""
        sql = """
        SELECT 
            er.*,
            ei.item_name, ei.item_category, ei.normal_range, ei.unit
        FROM examination_records er
        JOIN examination_items ei ON er.item_id = ei.item_id
        WHERE er.visit_id = %s
        ORDER BY er.exam_time DESC
        """

        return self.execute(sql, (visit_id,), fetch_all=True)

    def get_patient_examinations(self, patient_id: int,
                                 item_category: str = None,
                                 start_date: date = None,
                                 end_date: date = None,
                                 page: int = 1,
                                 page_size: int = 20) -> Tuple[List[Dict], int]:
        """
        获取患者的检查记录

        Args:
            patient_id: 患者ID
            item_category: 检查类别
            start_date: 开始日期
            end_date: 结束日期
            page: 页码
            page_size: 每页数量

        Returns:
            (检查记录列表, 总数量)
        """
        conditions = ["mv.patient_id = %s"]
        params = [patient_id]

        if item_category:
            conditions.append("ei.item_category = %s")
            params.append(item_category)

        if start_date:
            conditions.append("er.exam_date >= %s")
            params.append(start_date)

        if end_date:
            conditions.append("er.exam_date <= %s")
            params.append(end_date)

        where_clause = " AND ".join(conditions)

        # 计算总数
        count_sql = f"""
        SELECT COUNT(*) as count
        FROM examination_records er
        JOIN examination_items ei ON er.item_id = ei.item_id
        JOIN medical_visits mv ON er.visit_id = mv.visit_id
        WHERE {where_clause}
        """

        result = self.execute(count_sql, tuple(params), fetch_one=True)
        total = result.get("count", 0) if result else 0

        # 分页查询
        select_sql = f"""
        SELECT 
            er.*,
            ei.item_name, ei.item_category, ei.normal_range, ei.unit,
            mv.visit_date, mv.diagnosis,
            d.name as doctor_name, d.title as doctor_title
        FROM examination_records er
        JOIN examination_items ei ON er.item_id = ei.item_id
        JOIN medical_visits mv ON er.visit_id = mv.visit_id
        JOIN doctors d ON mv.doctor_id = d.doctor_id
        WHERE {where_clause}
        ORDER BY er.exam_date DESC, er.exam_time DESC
        LIMIT %s OFFSET %s
        """

        offset = (page - 1) * page_size
        params_with_paging = tuple(list(params) + [page_size, offset])

        exams = self.execute(select_sql, params_with_paging, fetch_all=True)

        return exams, total

    def create_examination(self, exam_data: Dict[str, Any]) -> int:
        """
        创建检查记录

        Args:
            exam_data: 检查数据

        Returns:
            检查记录ID
        """
        # 设置默认值
        now = datetime.now()
        if "exam_date" not in exam_data:
            exam_data["exam_date"] = now.date()
        if "exam_time" not in exam_data:
            exam_data["exam_time"] = now.time()
        if "created_at" not in exam_data:
            exam_data["created_at"] = now

        return self.insert("examination_records", exam_data)

    def update_examination_result(self, exam_id: int,
                                  result_value: str,
                                  result_summary: str = None,
                                  abnormal_flag: bool = None) -> bool:
        """
        更新检查结果

        Args:
            exam_id: 检查ID
            result_value: 结果值
            result_summary: 结果摘要
            abnormal_flag: 是否异常

        Returns:
            是否成功
        """
        update_data = {
            "result_value": result_value,
            "updated_at": datetime.now()
        }

        if result_summary:
            update_data["result_summary"] = result_summary

        if abnormal_flag is not None:
            update_data["abnormal_flag"] = abnormal_flag

        affected = self.update(
            "examination_records",
            update_data,
            condition="exam_id = %s",
            params=(exam_id,)
        )

        return affected > 0

    # ==================== 统计报表 ====================

    def get_daily_statistics(self, date: date = None) -> Dict[str, Any]:
        """
        获取每日统计

        Args:
            date: 日期，默认为今天

        Returns:
            统计信息
        """
        if date is None:
            date = datetime.now().date()

        # 就诊统计
        visit_sql = """
        SELECT 
            COUNT(*) as total_visits,
            COUNT(DISTINCT patient_id) as unique_patients,
            COUNT(DISTINCT doctor_id) as unique_doctors,
            AVG(fee_amount) as avg_fee
        FROM medical_visits
        WHERE visit_date = %s
        """

        visit_stats = self.execute(visit_sql, (date,), fetch_one=True) or {}

        # 检查统计
        exam_sql = """
        SELECT 
            COUNT(*) as total_exams,
            COUNT(DISTINCT ei.item_category) as unique_categories,
            SUM(CASE WHEN abnormal_flag = 1 THEN 1 ELSE 0 END) as abnormal_exams
        FROM examination_records er
        JOIN examination_items ei ON er.item_id = ei.item_id
        WHERE er.exam_date = %s
        """

        exam_stats = self.execute(exam_sql, (date,), fetch_one=True) or {}

        # 科室就诊排名
        dept_ranking_sql = """
        SELECT 
            d.department_name,
            COUNT(mv.visit_id) as visit_count
        FROM medical_visits mv
        JOIN doctors doc ON mv.doctor_id = doc.doctor_id
        JOIN departments d ON doc.department_id = d.department_id
        WHERE mv.visit_date = %s
        GROUP BY d.department_id, d.department_name
        ORDER BY visit_count DESC
        LIMIT 5
        """

        dept_ranking = self.execute(dept_ranking_sql, (date,), fetch_all=True) or []

        return {
            "date": date,
            "visit_statistics": visit_stats,
            "examination_statistics": exam_stats,
            "department_ranking": dept_ranking
        }

    def get_patient_statistics(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        获取患者统计

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            患者统计信息
        """
        # 患者增长统计
        growth_sql = """
        SELECT 
            DATE(created_at) as date,
            COUNT(*) as daily_count,
            SUM(COUNT(*)) OVER (ORDER BY DATE(created_at)) as total_count
        FROM patients
        WHERE DATE(created_at) BETWEEN %s AND %s
        GROUP BY DATE(created_at)
        ORDER BY DATE(created_at)
        """

        growth_stats = self.execute(growth_sql, (start_date, end_date), fetch_all=True) or []

        # 性别统计
        gender_sql = """
        SELECT 
            gender,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM patients), 2) as percentage
        FROM patients
        GROUP BY gender
        ORDER BY count DESC
        """

        gender_stats = self.execute(gender_sql, fetch_all=True) or []

        # 年龄段统计
        age_sql = """
        SELECT 
            CASE
                WHEN TIMESTAMPDIFF(YEAR, birth_date, CURDATE()) < 18 THEN '<18'
                WHEN TIMESTAMPDIFF(YEAR, birth_date, CURDATE()) BETWEEN 18 AND 30 THEN '18-30'
                WHEN TIMESTAMPDIFF(YEAR, birth_date, CURDATE()) BETWEEN 31 AND 45 THEN '31-45'
                WHEN TIMESTAMPDIFF(YEAR, birth_date, CURDATE()) BETWEEN 46 AND 60 THEN '46-60'
                ELSE '>60'
            END as age_group,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM patients), 2) as percentage
        FROM patients
        WHERE birth_date IS NOT NULL
        GROUP BY age_group
        ORDER BY 
            CASE age_group
                WHEN '<18' THEN 1
                WHEN '18-30' THEN 2
                WHEN '31-45' THEN 3
                WHEN '46-60' THEN 4
                ELSE 5
            END
        """

        age_stats = self.execute(age_sql, fetch_all=True) or []

        return {
            "date_range": {"start_date": start_date, "end_date": end_date},
            "growth_statistics": growth_stats,
            "gender_distribution": gender_stats,
            "age_distribution": age_stats
        }

    def get_revenue_statistics(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        获取收入统计

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            收入统计信息
        """
        # 每日收入
        daily_revenue_sql = """
        SELECT 
            visit_date as date,
            SUM(fee_amount) as daily_revenue,
            COUNT(*) as visit_count,
            AVG(fee_amount) as avg_fee
        FROM medical_visits
        WHERE visit_date BETWEEN %s AND %s
        GROUP BY visit_date
        ORDER BY visit_date
        """

        daily_revenue = self.execute(daily_revenue_sql, (start_date, end_date), fetch_all=True) or []

        # 科室收入
        dept_revenue_sql = """
        SELECT 
            d.department_name,
            SUM(mv.fee_amount) as total_revenue,
            COUNT(mv.visit_id) as visit_count,
            AVG(mv.fee_amount) as avg_fee
        FROM medical_visits mv
        JOIN doctors doc ON mv.doctor_id = doc.doctor_id
        JOIN departments d ON doc.department_id = d.department_id
        WHERE mv.visit_date BETWEEN %s AND %s
        GROUP BY d.department_id, d.department_name
        ORDER BY total_revenue DESC
        LIMIT 10
        """

        dept_revenue = self.execute(dept_revenue_sql, (start_date, end_date), fetch_all=True) or []

        # 总计
        total_sql = """
        SELECT 
            SUM(fee_amount) as total_revenue,
            COUNT(*) as total_visits,
            AVG(fee_amount) as overall_avg_fee
        FROM medical_visits
        WHERE visit_date BETWEEN %s AND %s
        """

        total_stats = self.execute(total_sql, (start_date, end_date), fetch_one=True) or {}

        return {
            "date_range": {"start_date": start_date, "end_date": end_date},
            "daily_revenue": daily_revenue,
            "department_revenue": dept_revenue,
            "total_statistics": total_stats
        }