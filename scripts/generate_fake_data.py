# 模拟医疗数据生成脚本

from faker import Faker #version 39.0.0
import pymysql #用于连接数据库、创建游标执行sql
from pymysql import cursors
import hashlib #生成身份证、密码等等的哈希
import random
import json
import sys
import os

# 初始化Faker，使用中文
fake = Faker('zh_CN')


class MedicalDataGenerator:
    def __init__(self, db_config): #初始化
        self.db_config = db_config
        self.connection = None
        self.cursor = None

        # 数据缓存
        self.user_ids = []
        self.patient_ids = []
        self.doctor_ids = []
        self.hospital_ids = []
        self.department_ids = []
        self.exam_item_ids = []

    def connect_db(self):
        """连接数据库"""
        try:
            self.connection = pymysql.connect(
                host=self.db_config['host'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                database=self.db_config['database'],
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            self.cursor = self.connection.cursor()
            print("✅ 数据库连接成功")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            sys.exit(1)

    def disconnect_db(self):
        """断开数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("✅ 数据库连接已关闭")

    def generate_password_hash(self, password):
        """生成密码哈希（加盐）"""
        if not hasattr(self, 'salt'):
            self.salt = os.urandom(16)
        salted = self.salt + password.encode() #拼接盐
        return hashlib.sha256(salted).hexdigest()

    def generate_empi(self, id_card):
        """生成EMPI标识"""
        salt = "MEDICAL_SALT_2024"
        raw_string = f"{id_card}_{salt}"
        hash_obj = hashlib.sha256(raw_string.encode())
        return f"EMP{hash_obj.hexdigest()[:20]}"

    def generate_id_card_hash(self, id_card):
        """生成身份证号哈希"""
        return hashlib.sha256(id_card.encode()).hexdigest()

    # ==================== 用户数据生成 ====================

    def generate_users(self, count=50):
        """生成用户数据"""
        print(f"\n📊 生成 {count} 个用户...")

        roles = ['医生', '护士', '管理员', '患者', '技师', '药师']
        role_weights = [0.2, 0.2, 0.1, 0.3, 0.1, 0.1]  # 角色分布权重

        users = []
        for i in range(1, count + 1):
            role = random.choices(roles, weights=role_weights)[0]

            user = {
                'username': fake.user_name() + str(i).zfill(3),
                'password_hash': self.generate_password_hash('Password123!'),
                'email': fake.email() if i % 3 != 0 else None,  # 1/3用户没有邮箱
                'phone': fake.phone_number() if i % 5 != 0 else None,  # 1/5用户没有电话
                'role': role,
                'is_active': random.choices([True, False], weights=[0.9, 0.1])[0],
                'last_login': fake.date_time_between(start_date='-90d', end_date='now')
                if random.random() > 0.3 else None  # 30%用户从未登录
            }
            users.append(user)

        return users

    def insert_users(self, users):
        """插入用户数据"""
        sql = """
        INSERT INTO users (username, password_hash, email, phone, role, is_active, last_login)
        VALUES (%(username)s, %(password_hash)s, %(email)s, %(phone)s, %(role)s, %(is_active)s, %(last_login)s)
        """

        self.cursor.executemany(sql, users)
        self.connection.commit()

        # 获取生成的user_id
        self.cursor.execute("SELECT user_id FROM users ORDER BY user_id DESC LIMIT %s", len(users))
        self.user_ids = [row['user_id'] for row in self.cursor.fetchall()]

        print(f"✅ 已插入 {len(users)} 个用户，user_id范围: {min(self.user_ids)}-{max(self.user_ids)}")
        return self.user_ids

    # ==================== 患者数据生成 ====================

    def generate_patients(self, count=100):
        """生成患者数据"""
        print(f"\n📊 生成 {count} 个患者...")

        # 分配用户ID给患者角色
        patient_user_ids = random.sample(self.user_ids, min(count, len(self.user_ids)))

        patients = []
        for i in range(count):
            # 生成虚拟身份证号
            id_card = fake.ssn()

            # 随机慢性病史
            chronic_diseases = random.choices([
                [],
                ["高血压"],
                ["糖尿病"],
                ["高血压", "糖尿病"],
                ["冠心病"],
                ["哮喘"],
                ["慢性阻塞性肺病"]
            ], weights=[0.4, 0.2, 0.15, 0.1, 0.08, 0.05, 0.02])[0]

            patient = {
                'empi_code': self.generate_empi(id_card),
                'name': fake.name(),
                'gender': random.choice(['M', 'F']),
                'birth_date': fake.date_of_birth(minimum_age=18, maximum_age=90),
                'id_card_hash': self.generate_id_card_hash(id_card),
                'medical_insurance_id': fake.bothify('MI##########') if random.random() > 0.1 else None,
                'blood_type': random.choice(['A', 'B', 'AB', 'O', '未知']),
                'allergy_history': random.choices([
                    None,
                    "青霉素过敏",
                    "头孢类过敏",
                    "海鲜过敏",
                    "花粉过敏"
                ], weights=[0.7, 0.1, 0.1, 0.05, 0.05])[0],
                'chronic_diseases': json.dumps(chronic_diseases, ensure_ascii=False) if chronic_diseases else None,
                'emergency_contact': fake.name() if random.random() > 0.2 else None,
                'emergency_phone': fake.phone_number() if random.random() > 0.2 else None,
                'phone': fake.phone_number(),
                'email': fake.email() if random.random() > 0.7 else None,
                'address': fake.address(),
                'is_active': random.choices([True, False], weights=[0.95, 0.05])[0],
                'user_id': patient_user_ids[i] if i < len(patient_user_ids) else None
            }
            patients.append(patient)

        return patients

    def insert_patients(self, patients):
        """插入患者数据"""
        sql = """
        INSERT INTO patients (
            empi_code, name, gender, birth_date, id_card_hash, medical_insurance_id,
            blood_type, allergy_history, chronic_diseases, emergency_contact,
            emergency_phone, phone, email, address, is_active, user_id
        ) VALUES (
            %(empi_code)s, %(name)s, %(gender)s, %(birth_date)s, %(id_card_hash)s, %(medical_insurance_id)s,
            %(blood_type)s, %(allergy_history)s, %(chronic_diseases)s, %(emergency_contact)s,
            %(emergency_phone)s, %(phone)s, %(email)s, %(address)s, %(is_active)s, %(user_id)s
        )
        """

        self.cursor.executemany(sql, patients)
        self.connection.commit()

        # 获取生成的patient_id
        self.cursor.execute("SELECT patient_id FROM patients ORDER BY patient_id DESC LIMIT %s", len(patients))
        self.patient_ids = [row['patient_id'] for row in self.cursor.fetchall()]

        print(f"✅ 已插入 {len(patients)} 个患者，patient_id范围: {min(self.patient_ids)}-{max(self.patient_ids)}")
        return self.patient_ids

    # ==================== 医院数据生成 ====================

    def generate_hospitals(self, count=5):
        """生成医院数据"""
        print(f"\n📊 生成 {count} 个医院...")

        hospitals = []
        hospital_levels = ['三甲', '三乙', '二甲', '二乙', '一级', '社区']
        hospital_types = ['综合医院', '专科医院', '社区卫生服务中心']

        for i in range(count):
            hospital = {
                'hospital_code': f'HOSP{str(i + 1).zfill(3)}',
                'name': f'{fake.city()}第{i + 1}医院',
                'level': random.choice(hospital_levels),
                'type': random.choice(hospital_types),
                'address': fake.address(),
                'phone': fake.phone_number(),
                'website': f'www.hospital{i + 1}.com' if random.random() > 0.3 else None,
                'region_code': fake.postcode()[:4],
                'bed_count': random.randint(50, 2000),
                'is_in_network': random.choices([True, False], weights=[0.8, 0.2])[0],
                'is_active': True
            }
            hospitals.append(hospital)

        return hospitals

    def insert_hospitals(self, hospitals):
        """插入医院数据"""
        sql = """
        INSERT INTO hospitals (
            hospital_code, name, level, type, address, phone, website,
            region_code, bed_count, is_in_network, is_active
        ) VALUES (
            %(hospital_code)s, %(name)s, %(level)s, %(type)s, %(address)s, %(phone)s, %(website)s,
            %(region_code)s, %(bed_count)s, %(is_in_network)s, %(is_active)s
        )
        """

        self.cursor.executemany(sql, hospitals)
        self.connection.commit()

        # 获取生成的hospital_id
        self.cursor.execute("SELECT hospital_id FROM hospitals ORDER BY hospital_id DESC LIMIT %s", len(hospitals))
        self.hospital_ids = [row['hospital_id'] for row in self.cursor.fetchall()]

        print(f"✅ 已插入 {len(hospitals)} 个医院，hospital_id范围: {min(self.hospital_ids)}-{max(self.hospital_ids)}")
        return self.hospital_ids

    # ==================== 科室数据生成 ====================

    def generate_departments(self, hospitals_per_hospital=8):
        """生成科室数据"""
        print(f"\n📊 为每个医院生成 {hospitals_per_hospital} 个科室...")

        # 标准科室名称
        standard_depts = {
            '临床科室': ['内科', '外科', '儿科', '妇产科', '眼科', '耳鼻喉科', '口腔科', '皮肤科', '中医科'],
            '医技科室': ['放射科', '检验科', '超声科', '病理科', '药剂科'],
            '行政科室': ['院长办公室', '医务科', '护理部', '财务科'],
            '辅助科室': ['病案室', '设备科', '后勤部']
        }

        departments = []
        dept_counter = {}  # 记录每个医院的科室编码

        for hospital_id in self.hospital_ids:
            dept_counter[hospital_id] = 1

            # 为每种类型选择几个科室
            for dept_type, dept_names in standard_depts.items():
                # 随机选择1-3个该类型的科室
                selected_depts = random.sample(dept_names, min(random.randint(1, 3), len(dept_names)))

                for dept_name in selected_depts:
                    department = {
                        'hospital_id': hospital_id,
                        'dept_code': f'DEPT{str(dept_counter[hospital_id]).zfill(3)}',
                        'dept_name': dept_name,
                        'dept_type': dept_type,
                        'parent_dept_id': None,  # 简化，不设层级
                        'phone': fake.phone_number() if random.random() > 0.3 else None,
                        'location': f'{random.randint(1, 10)}楼{random.randint(1, 20)}号',
                        'description': f'{dept_name}科室描述',
                        'is_active': True
                    }
                    departments.append(department)
                    dept_counter[hospital_id] += 1

        return departments

    def insert_departments(self, departments):
        """插入科室数据"""
        sql = """
        INSERT INTO departments (
            hospital_id, dept_code, dept_name, dept_type, parent_dept_id,
            phone, location, description, is_active
        ) VALUES (
            %(hospital_id)s, %(dept_code)s, %(dept_name)s, %(dept_type)s, %(parent_dept_id)s,
            %(phone)s, %(location)s, %(description)s, %(is_active)s
        )
        """

        self.cursor.executemany(sql, departments)
        self.connection.commit()

        # 获取生成的department_id
        self.cursor.execute("SELECT department_id FROM departments ORDER BY department_id DESC LIMIT %s",
                            len(departments))
        self.department_ids = [row['department_id'] for row in self.cursor.fetchall()]

        print(
            f"✅ 已插入 {len(departments)} 个科室，department_id范围: {min(self.department_ids)}-{max(self.department_ids)}")
        return self.department_ids

    # ==================== 医生数据生成 ====================

    def generate_doctors(self, doctors_per_dept=2):
        """生成医生数据"""
        print(f"\n📊 为每个科室生成 {doctors_per_dept} 个医生...")

        # 获取科室信息
        self.cursor.execute("""
            SELECT d.department_id, d.hospital_id, d.dept_name 
            FROM departments d
            WHERE d.dept_type IN ('临床科室', '医技科室')
        """)
        clinical_departments = self.cursor.fetchall()

        doctors = []
        doctor_user_ids = []  # 记录分配给医生的用户ID

        # 筛选出医生角色的用户
        if self.user_ids:
            self.cursor.execute("SELECT user_id FROM users WHERE role = '医生'")
            doctor_users = [row['user_id'] for row in self.cursor.fetchall()]
            doctor_user_ids = doctor_users if doctor_users else []

        doctor_counter = 1
        for dept in clinical_departments:
            for i in range(doctors_per_dept):
                # 分配用户ID（如果还有可用的）
                user_id = doctor_user_ids.pop(0) if doctor_user_ids else None

                doctor = {
                    'doctor_number': f'DOC{str(doctor_counter).zfill(5)}',
                    'name': fake.name(),
                    'gender': random.choice(['M', 'F']),
                    'title': random.choice(['主任医师', '副主任医师', '主治医师', '住院医师', '医师']),
                    'department_id': dept['department_id'],
                    'specialty': f"{dept['dept_name']}专业",
                    'qualification_number': f'QUAL{str(doctor_counter).zfill(10)}',
                    'license_number': f'LIC{str(doctor_counter).zfill(10)}',
                    'employment_date': fake.date_between(start_date='-20y', end_date='-1y'),
                    'status': random.choices(['在职', '休假', '进修'], weights=[0.85, 0.1, 0.05])[0],
                    'contact_phone': fake.phone_number() if random.random() > 0.1 else None,
                    'email': fake.email() if random.random() > 0.3 else None,
                    'introduction': f"{fake.name()}医生，擅长{dept['dept_name']}相关疾病的诊治。",
                    'avatar_path': f'/avatars/doctor_{doctor_counter}.jpg' if random.random() > 0.5 else None,
                    'user_id': user_id
                }
                doctors.append(doctor)
                doctor_counter += 1

        return doctors

    def insert_doctors(self, doctors):
        """插入医生数据"""
        sql = """
        INSERT INTO doctors (
            doctor_number, name, gender, title, department_id, specialty,
            qualification_number, license_number, employment_date, status,
            contact_phone, email, introduction, avatar_path, user_id
        ) VALUES (
            %(doctor_number)s, %(name)s, %(gender)s, %(title)s, %(department_id)s, %(specialty)s,
            %(qualification_number)s, %(license_number)s, %(employment_date)s, %(status)s,
            %(contact_phone)s, %(email)s, %(introduction)s, %(avatar_path)s, %(user_id)s
        )
        """

        self.cursor.executemany(sql, doctors)
        self.connection.commit()

        # 获取生成的doctor_id
        self.cursor.execute("SELECT doctor_id FROM doctors ORDER BY doctor_id DESC LIMIT %s", len(doctors))
        self.doctor_ids = [row['doctor_id'] for row in self.cursor.fetchall()]

        print(f"✅ 已插入 {len(doctors)} 个医生，doctor_id范围: {min(self.doctor_ids)}-{max(self.doctor_ids)}")
        return self.doctor_ids

    # ==================== 检查项目数据生成 ====================

    def generate_examination_items(self, count=20):
        """生成检查项目数据"""
        print(f"\n📊 生成 {count} 个检查项目...")

        exam_items = [
            # 影像检查
            {'code': 'CT001', 'name': '胸部CT平扫', 'type': '影像检查', 'modality': 'CT', 'category': '放射科',
             'price': 350.00},
            {'code': 'CT002', 'name': '头颅CT增强', 'type': '影像检查', 'modality': 'CT', 'category': '放射科',
             'price': 600.00},
            {'code': 'MRI001', 'name': '头颅MRI平扫', 'type': '影像检查', 'modality': 'MRI', 'category': '放射科',
             'price': 800.00},
            {'code': 'MRI002', 'name': '腰椎MRI', 'type': '影像检查', 'modality': 'MRI', 'category': '放射科',
             'price': 1200.00},
            {'code': 'XR001', 'name': '胸部X光', 'type': '影像检查', 'modality': 'X-Ray', 'category': '放射科',
             'price': 80.00},
            {'code': 'US001', 'name': '腹部超声', 'type': '影像检查', 'modality': '超声', 'category': '超声科',
             'price': 120.00},
            {'code': 'US002', 'name': '心脏超声', 'type': '影像检查', 'modality': '超声', 'category': '超声科',
             'price': 200.00},

            # 实验室检查
            {'code': 'LAB001', 'name': '血常规', 'type': '实验室检查', 'modality': '无', 'category': '检验科',
             'price': 25.00},
            {'code': 'LAB002', 'name': '尿常规', 'type': '实验室检查', 'modality': '无', 'category': '检验科',
             'price': 15.00},
            {'code': 'LAB003', 'name': '肝功能', 'type': '实验室检查', 'modality': '无', 'category': '检验科',
             'price': 60.00},
            {'code': 'LAB004', 'name': '肾功能', 'type': '实验室检查', 'modality': '无', 'category': '检验科',
             'price': 50.00},
            {'code': 'LAB005', 'name': '血糖', 'type': '实验室检查', 'modality': '无', 'category': '检验科',
             'price': 8.00},
            {'code': 'LAB006', 'name': '血脂', 'type': '实验室检查', 'modality': '无', 'category': '检验科',
             'price': 40.00},

            # 功能检查
            {'code': 'FUNC001', 'name': '心电图', 'type': '功能检查', 'modality': '心电图', 'category': '心电图室',
             'price': 30.00},
            {'code': 'FUNC002', 'name': '24小时动态心电图', 'type': '功能检查', 'modality': '心电图',
             'category': '心电图室', 'price': 300.00},
            {'code': 'FUNC003', 'name': '肺功能检查', 'type': '功能检查', 'modality': '无', 'category': '功能检查室',
             'price': 150.00},

            # 病理检查
            {'code': 'PATH001', 'name': '病理切片检查', 'type': '病理检查', 'modality': '无', 'category': '病理科',
             'price': 200.00},
            {'code': 'PATH002', 'name': '细胞学检查', 'type': '病理检查', 'modality': '无', 'category': '病理科',
             'price': 120.00},
        ]

        items = []
        for i, item in enumerate(exam_items[:count]):
            # 根据项目类型生成正常值范围
            if item['name'] == '血常规':
                normal_range = {
                    "WBC": {"min": 4.0, "max": 10.0, "unit": "×10⁹/L"},
                    "RBC": {"min": 4.0, "max": 5.5, "unit": "×10¹²/L"},
                    "HGB": {"min": 120, "max": 160, "unit": "g/L"},
                    "PLT": {"min": 100, "max": 300, "unit": "×10⁹/L"}
                }
            elif item['name'] == '血糖':
                normal_range = {
                    "空腹血糖": {"min": 3.9, "max": 6.1, "unit": "mmol/L"}
                }
            elif '肝功能' in item['name']:
                normal_range = {
                    "ALT": {"min": 0, "max": 40, "unit": "U/L"},
                    "AST": {"min": 0, "max": 40, "unit": "U/L"}
                }
            else:
                normal_range = {"result": "正常范围内"}

            exam_item = {
                'item_code': item['code'],
                'item_name': item['name'],
                'item_type': item['type'],
                'modality': item['modality'],
                'category': item['category'],
                'description': f"{item['name']}检查，用于相关疾病的诊断。",
                'standard_duration': random.randint(10, 120),
                'preparation_instructions': "检查前需空腹8小时" if random.random() > 0.5 else "无需特殊准备",
                'normal_range': json.dumps(normal_range, ensure_ascii=False),
                'unit': '项',
                'reference_price': item['price'],
                'is_active': random.choices([True, False], weights=[0.95, 0.05])[0],
                'created_by': random.choice(self.doctor_ids) if self.doctor_ids else None
            }
            items.append(exam_item)

        return items

    def insert_examination_items(self, items):
        """插入检查项目数据"""
        sql = """
        INSERT INTO examination_items (
            item_code, item_name, item_type, modality, category, description,
            standard_duration, preparation_instructions, normal_range, unit,
            reference_price, is_active, created_by
        ) VALUES (
            %(item_code)s, %(item_name)s, %(item_type)s, %(modality)s, %(category)s, %(description)s,
            %(standard_duration)s, %(preparation_instructions)s, %(normal_range)s, %(unit)s,
            %(reference_price)s, %(is_active)s, %(created_by)s
        )
        """

        self.cursor.executemany(sql, items)
        self.connection.commit()

        # 获取生成的item_id
        self.cursor.execute("SELECT item_id FROM examination_items ORDER BY item_id DESC LIMIT %s", len(items))
        self.exam_item_ids = [row['item_id'] for row in self.cursor.fetchall()]

        print(f"✅ 已插入 {len(items)} 个检查项目，item_id范围: {min(self.exam_item_ids)}-{max(self.exam_item_ids)}")
        return self.exam_item_ids

    # ==================== 就诊记录数据生成 ====================

    def generate_medical_visits(self, visits_per_patient=3):
        """生成就诊记录数据"""
        print(f"\n📊 为每个患者生成 {visits_per_patient} 个就诊记录...")

        # 获取医生和科室信息
        self.cursor.execute("""
            SELECT d.doctor_id, d.department_id, dept.hospital_id
            FROM doctors d
            JOIN departments dept ON d.department_id = dept.department_id
            WHERE d.status = '在职'
        """)
        doctors_info = self.cursor.fetchall()

        visits = []
        visit_counter = 1

        for patient_id in self.patient_ids:
            for i in range(random.randint(1, visits_per_patient)):  # 随机1-3次就诊
                # 随机选择医生
                doctor_info = random.choice(doctors_info)

                # 生成就诊时间（最近2年内）
                visit_date = fake.date_time_between(start_date='-2y', end_date='now')

                # 生成症状和诊断
                chief_complaint = random.choice([
                    "咳嗽、发热3天",
                    "头痛、头晕1周",
                    "腹痛、腹泻2天",
                    "胸闷、气短",
                    "关节疼痛",
                    "体检",
                    "感冒症状"
                ])

                diagnosis = random.choice([
                    "上呼吸道感染",
                    "高血压",
                    "急性胃肠炎",
                    "冠心病",
                    "糖尿病",
                    "健康体检正常",
                    "普通感冒"
                ])

                visit = {
                    'visit_number': f'VIS{str(visit_counter).zfill(8)}',
                    'patient_id': patient_id,
                    'hospital_id': doctor_info['hospital_id'],
                    'department_id': doctor_info['department_id'],
                    'doctor_id': doctor_info['doctor_id'],
                    'visit_date': visit_date,
                    'visit_type': random.choice(['普通门诊', '急诊', '复诊']),
                    'chief_complaint': chief_complaint,
                    'diagnosis': diagnosis,
                    'advice': random.choice([
                        "注意休息，多喝水",
                        "按时服药，定期复查",
                        "低盐低脂饮食",
                        "适当运动，控制体重"
                    ]),
                    'temperature': round(random.uniform(36.0, 39.5), 1) if random.random() > 0.3 else None,
                    'blood_pressure': f"{random.randint(100, 160)}/{random.randint(60, 100)}" if random.random() > 0.4 else None,
                    'heart_rate': random.randint(60, 120) if random.random() > 0.4 else None,
                    'payment_status': random.choice(['已支付', '医保结算', '未支付']),
                    'total_fee': round(random.uniform(50.0, 500.0), 2),
                    'is_emergency': random.choices([True, False], weights=[0.2, 0.8])[0]
                }
                visits.append(visit)
                visit_counter += 1

        return visits

    def insert_medical_visits(self, visits):
        """插入就诊记录数据"""
        sql = """
        INSERT INTO medical_visits (
            visit_number, patient_id, hospital_id, department_id, doctor_id,
            visit_date, visit_type, chief_complaint, diagnosis, advice,
            temperature, blood_pressure, heart_rate, payment_status,
            total_fee, is_emergency
        ) VALUES (
            %(visit_number)s, %(patient_id)s, %(hospital_id)s, %(department_id)s, %(doctor_id)s,
            %(visit_date)s, %(visit_type)s, %(chief_complaint)s, %(diagnosis)s, %(advice)s,
            %(temperature)s, %(blood_pressure)s, %(heart_rate)s, %(payment_status)s,
            %(total_fee)s, %(is_emergency)s
        )
        """

        self.cursor.executemany(sql, visits)
        self.connection.commit()

        print(f"✅ 已插入 {len(visits)} 个就诊记录")

        # 获取visit_id用于后续检查记录生成
        self.cursor.execute("SELECT visit_id FROM medical_visits ORDER BY visit_id DESC LIMIT %s", len(visits))
        return [row['visit_id'] for row in self.cursor.fetchall()]

    # ==================== 检查记录数据生成 ====================

    def generate_examination_records(self, visits, exams_per_visit=2):
        """生成检查记录数据"""
        print(f"\n📊 为就诊记录生成检查记录（平均{exams_per_visit}个/就诊）...")

        records = []
        exam_counter = 1

        for visit_id in visits:
            # 每个就诊随机1-3个检查
            num_exams = random.randint(1, exams_per_visit)

            for _ in range(num_exams):
                # 随机选择检查项目
                item_id = random.choice(self.exam_item_ids)

                # 获取检查项目信息
                self.cursor.execute("SELECT reference_price, item_name FROM examination_items WHERE item_id = %s",
                                    item_id)
                item_info = self.cursor.fetchone()

                # 生成检查结果
                if '血常规' in item_info['item_name']:
                    result_values = {
                        "WBC": round(random.uniform(4.0, 12.0), 1),
                        "RBC": round(random.uniform(3.5, 6.0), 2),
                        "HGB": random.randint(110, 170),
                        "PLT": random.randint(80, 350)
                    }
                    result_summary = "白细胞轻度升高" if result_values["WBC"] > 10.0 else "血常规大致正常"
                elif '血糖' in item_info['item_name']:
                    result_values = {"空腹血糖": round(random.uniform(4.0, 8.0), 1)}
                    result_summary = "血糖正常" if result_values["空腹血糖"] < 6.1 else "空腹血糖升高"
                else:
                    result_values = {"result": "未见明显异常"}
                    result_summary = "检查结果正常"

                # AI分析（模拟）
                ai_analysis = {
                    "confidence": round(random.uniform(0.7, 0.99), 2),
                    "findings": ["未见明显异常", "建议定期复查"][:random.randint(0, 1)],
                    "risk_level": random.choice(["低", "中", "高"])
                } if random.random() > 0.5 else None

                record = {
                    'exam_number': f'EXAM{str(exam_counter).zfill(8)}',
                    'visit_id': visit_id,
                    'item_id': item_id,
                    'exam_date': fake.date_time_between(start_date='-7d', end_date='now'),
                    'result_summary': result_summary,
                    'result_values': json.dumps(result_values, ensure_ascii=False),
                    'data_path': f'/data/exams/{visit_id}_{item_id}.dcm' if random.random() > 0.7 else None,
                    'report_path': f'/reports/{visit_id}_{item_id}.pdf',
                    'ai_analysis': json.dumps(ai_analysis, ensure_ascii=False) if ai_analysis else None,
                    'status': random.choice(['已完成', '已审核']),
                    'reviewed_by': random.choice(self.doctor_ids) if random.random() > 0.5 and self.doctor_ids else None
                }
                records.append(record)
                exam_counter += 1

        return records

    def insert_examination_records(self, records):
        """插入检查记录数据"""
        sql = """
        INSERT INTO examination_records (
            exam_number, visit_id, item_id, exam_date, result_summary,
            result_values, data_path, report_path, ai_analysis, status,
            reviewed_by
        ) VALUES (
            %(exam_number)s, %(visit_id)s, %(item_id)s, %(exam_date)s, %(result_summary)s,
            %(result_values)s, %(data_path)s, %(report_path)s, %(ai_analysis)s, %(status)s,
            %(reviewed_by)s
        )
        """

        self.cursor.executemany(sql, records)
        self.connection.commit()

        print(f"✅ 已插入 {len(records)} 个检查记录")

    # ==================== 主执行函数 ====================

    def generate_all_data(self):
        """生成所有模拟数据"""
        print("🚀 开始生成医疗系统模拟数据...")

        try:
            # 1. 生成用户
            users = self.generate_users(50)
            self.insert_users(users)

            # 2. 生成患者
            patients = self.generate_patients(100)
            self.insert_patients(patients)

            # 3. 生成医院
            hospitals = self.generate_hospitals(5)
            self.insert_hospitals(hospitals)

            # 4. 生成科室
            departments = self.generate_departments(8)
            self.insert_departments(departments)

            # 5. 生成医生
            doctors = self.generate_doctors(2)
            self.insert_doctors(doctors)

            # 6. 生成检查项目
            exam_items = self.generate_examination_items(20)
            self.insert_examination_items(exam_items)

            # 7. 生成就诊记录
            visits = self.generate_medical_visits(3)
            visit_ids = self.insert_medical_visits(visits)

            # 8. 生成检查记录
            exam_records = self.generate_examination_records(visit_ids, 2)
            self.insert_examination_records(exam_records)

            print("\n🎉 所有模拟数据生成完成！")

        except Exception as e:
            print(f"❌ 数据生成失败: {e}")
            self.connection.rollback()
            raise

    def verify_data(self):
        """验证生成的数据（简化版）"""
        print("\n🔍 验证生成的数据...")

        queries = [
            ("用户数量", "SELECT COUNT(*) as count FROM users"),
            ("患者数量", "SELECT COUNT(*) as count FROM patients"),
            ("医院数量", "SELECT COUNT(*) as count FROM hospitals"),
            ("科室数量", "SELECT COUNT(*) as count FROM departments"),
            ("医生数量", "SELECT COUNT(*) as count FROM doctors"),
            ("检查项目数量", "SELECT COUNT(*) as count FROM examination_items"),
            ("就诊记录数量", "SELECT COUNT(*) as count FROM medical_visits"),
            ("检查记录数量", "SELECT COUNT(*) as count FROM examination_records")
        ]

        for label, query in queries:
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            print(f"  {label}: {result['count']}")

        # 检查数据质量
        print("\n📊 数据质量检查:")

        # 检查患者是否有就诊记录
        self.cursor.execute("""
            SELECT COUNT(DISTINCT p.patient_id) as patients_with_visits,
                   (SELECT COUNT(*) FROM patients) as total_patients
            FROM patients p
            JOIN medical_visits mv ON p.patient_id = mv.patient_id
        """)
        result = self.cursor.fetchone()
        coverage = (result['patients_with_visits'] / result['total_patients']) * 100
        print(f"  患者就诊覆盖率: {coverage:.1f}%")

        # 检查医生工作量
        self.cursor.execute("""
            SELECT d.name, COUNT(mv.visit_id) as visit_count
            FROM doctors d
            LEFT JOIN medical_visits mv ON d.doctor_id = mv.doctor_id
            GROUP BY d.doctor_id
            ORDER BY visit_count DESC
            LIMIT 5
        """)
        print(f"  医生工作量Top 5:")
        for row in self.cursor.fetchall():
            print(f"    {row['name']}: {row['visit_count']}次就诊")

        print("\n✅ 数据验证完成")


def main():
    """主函数"""
    # 数据库配置
    db_config = {
        'host': 'localhost',
        'user': 'med_user',
        'password': 'MedsAlpha',
        'database': 'medical_db'
    }

    # 创建数据生成器
    generator = MedicalDataGenerator(db_config)

    try:
        # 连接数据库
        generator.connect_db()

        # 清空现有数据（可选，慎用！）
        clear_data = input("是否清空现有数据？(y/N): ").lower() == 'y'
        if clear_data:
            tables = [
                'examination_records', 'examination_items', 'medical_visits',
                'doctors', 'pharmacists', 'technicians', 'departments',
                'hospitals', 'patients', 'users'
            ]
            generator.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            for table in tables:
                generator.cursor.execute(f"DELETE FROM {table}")
            generator.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            generator.connection.commit()
            print("🗑️  已清空所有表数据")

        # 生成所有数据
        generator.generate_all_data()

        # 验证数据(简单）
        generator.verify_data()

    except Exception as e:
        print(f"❌ 程序执行出错: {e}")

    finally:
        # 断开数据库连接
        generator.disconnect_db()


if __name__ == "__main__":
    main()