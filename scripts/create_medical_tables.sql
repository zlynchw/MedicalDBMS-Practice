-- 医疗系统数据库建表脚本
-- 版本: 1.0.0
-- 创建时间: 2025-01-07

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- 用户表
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT COMMENT '用户ID（主键）',
  `username` varchar(50) NOT NULL COMMENT '用户名',
  `password_hash` varchar(255) NOT NULL COMMENT '密码哈希',
  `email` varchar(100) NOT NULL COMMENT '邮箱',
  `phone` varchar(20) DEFAULT NULL COMMENT '联系电话',
  `role` enum('医生','护士','管理员','患者','技师','药师','研究员') NOT NULL COMMENT '角色',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否激活（1=是，0=否）',
  `last_login` timestamp NULL DEFAULT NULL COMMENT '最后登录时间',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `uk_username` (`username`),
  UNIQUE KEY `uk_email` (`email`),
  KEY `idx_role` (`role`),
  KEY `idx_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ----------------------------
-- 医院/机构表
-- ----------------------------
DROP TABLE IF EXISTS `hospitals`;
CREATE TABLE `hospitals` (
  `hospital_id` int NOT NULL AUTO_INCREMENT COMMENT '医院ID（主键）',
  `hospital_code` varchar(20) NOT NULL COMMENT '机构编码（如：HOSP001）',
  `name` varchar(200) NOT NULL COMMENT '医院名称',
  `level` enum('三甲','三乙','二甲','二乙','一级','社区','其他') DEFAULT NULL COMMENT '医院等级',
  `type` enum('综合医院','专科医院','社区卫生服务中心','诊所','其他') DEFAULT NULL COMMENT '医院类型',
  `address` varchar(500) DEFAULT NULL COMMENT '地址',
  `phone` varchar(20) DEFAULT NULL COMMENT '联系电话',
  `website` varchar(200) DEFAULT NULL COMMENT '网站',
  `region_code` varchar(20) DEFAULT NULL COMMENT '区域编码',
  `bed_count` int DEFAULT '0' COMMENT '床位数量',
  `is_in_network` tinyint(1) DEFAULT '0' COMMENT '是否在医联体网络内（1=是，0=否）',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否有效（1=是，0=否）',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '加入网络时间',
  PRIMARY KEY (`hospital_id`),
  UNIQUE KEY `uk_hospital_code` (`hospital_code`),
  KEY `idx_is_active` (`is_active`),
  KEY `idx_is_in_network` (`is_in_network`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='医院/机构表';

-- ----------------------------
-- 科室表
-- ----------------------------
DROP TABLE IF EXISTS `departments`;
CREATE TABLE `departments` (
  `department_id` int NOT NULL AUTO_INCREMENT COMMENT '科室ID（主键）',
  `hospital_id` int NOT NULL COMMENT '所属医院ID（外键）',
  `dept_code` varchar(20) NOT NULL COMMENT '科室编码（如：DEP001）',
  `dept_name` varchar(100) NOT NULL COMMENT '科室名称',
  `dept_type` enum('临床科室','医技科室','行政科室') NOT NULL COMMENT '科室类型',
  `parent_dept_id` int DEFAULT NULL COMMENT '上级科室ID（用于层级结构）',
  `phone` varchar(20) DEFAULT NULL COMMENT '科室电话',
  `location` varchar(200) DEFAULT NULL COMMENT '位置/楼层',
  `head_doctor_id` int DEFAULT NULL COMMENT '科室主任ID',
  `description` text COMMENT '科室简介',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否有效（1=是，0=否）',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`department_id`),
  UNIQUE KEY `uk_dept_code` (`dept_code`),
  KEY `idx_hospital_id` (`hospital_id`),
  KEY `idx_parent_dept_id` (`parent_dept_id`),
  KEY `idx_is_active` (`is_active`),
  CONSTRAINT `fk_departments_hospital` FOREIGN KEY (`hospital_id`) REFERENCES `hospitals` (`hospital_id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_departments_parent` FOREIGN KEY (`parent_dept_id`) REFERENCES `departments` (`department_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='科室表';

-- ----------------------------
-- 患者表
-- ----------------------------
DROP TABLE IF EXISTS `patients`;
CREATE TABLE `patients` (
  `patient_id` int NOT NULL AUTO_INCREMENT COMMENT '平台统一ID（主键）',
  `empi_code` varchar(50) NOT NULL COMMENT 'EMPI统一标识',
  `name` varchar(100) NOT NULL COMMENT '姓名',
  `gender` enum('男','女','未知') DEFAULT '未知' COMMENT '性别',
  `birth_date` date DEFAULT NULL COMMENT '出生日期',
  `id_card_hash` varchar(128) NOT NULL COMMENT '身份证号哈希',
  `medical_insurance_id` varchar(50) DEFAULT NULL COMMENT '医保号',
  `blood_type` enum('A','B','AB','O','未知') DEFAULT '未知' COMMENT '血型',
  `allergy_history` text COMMENT '过敏史（文本）',
  `chronic_diseases` json DEFAULT NULL COMMENT '慢性病史（JSON格式，如["高血压","糖尿病"]）',
  `emergency_contact` varchar(100) DEFAULT NULL COMMENT '紧急联系人',
  `emergency_phone` varchar(20) DEFAULT NULL COMMENT '紧急联系电话',
  `phone` varchar(20) DEFAULT NULL COMMENT '联系电话',
  `email` varchar(100) DEFAULT NULL COMMENT '邮箱',
  `address` varchar(500) DEFAULT NULL COMMENT '联系地址',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否有效（1=是，0=否）',
  `user_id` int DEFAULT NULL COMMENT '关联用户ID（外键，引用users.user_id）',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`patient_id`),
  UNIQUE KEY `uk_empi_code` (`empi_code`),
  UNIQUE KEY `uk_id_card_hash` (`id_card_hash`),
  UNIQUE KEY `uk_user_id` (`user_id`),
  KEY `idx_name` (`name`),
  KEY `idx_is_active` (`is_active`),
  KEY `idx_phone` (`phone`),
  CONSTRAINT `fk_patients_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='患者表';

-- ----------------------------
-- 医生表
-- ----------------------------
DROP TABLE IF EXISTS `doctors`;
CREATE TABLE `doctors` (
  `doctor_id` int NOT NULL AUTO_INCREMENT COMMENT '医生ID（主键）',
  `doctor_number` varchar(20) NOT NULL COMMENT '工号/医师编号',
  `name` varchar(100) NOT NULL COMMENT '姓名',
  `gender` enum('男','女') DEFAULT NULL COMMENT '性别',
  `title` enum('主任医师','副主任医师','主治医师','住院医师','医师','助理医师') DEFAULT NULL COMMENT '职称',
  `department_id` int DEFAULT NULL COMMENT '所属科室ID（外键）',
  `specialty` varchar(200) DEFAULT NULL COMMENT '专业方向（如：心内科、神经外科、儿科）',
  `qualification_number` varchar(50) NOT NULL COMMENT '医师资格证编号',
  `license_number` varchar(50) NOT NULL COMMENT '执业证书编号',
  `employment_date` date DEFAULT NULL COMMENT '入职日期',
  `status` enum('在职','离职','休假') DEFAULT '在职' COMMENT '状态',
  `contact_phone` varchar(20) DEFAULT NULL COMMENT '联系电话',
  `email` varchar(100) DEFAULT NULL COMMENT '邮箱',
  `introduction` text COMMENT '医生简介（文本）',
  `avatar_path` varchar(500) DEFAULT NULL COMMENT '头像图片路径（可选）',
  `user_id` int DEFAULT NULL COMMENT '关联用户ID（外键，引用users.user_id）',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`doctor_id`),
  UNIQUE KEY `uk_doctor_number` (`doctor_number`),
  UNIQUE KEY `uk_qualification_number` (`qualification_number`),
  UNIQUE KEY `uk_license_number` (`license_number`),
  UNIQUE KEY `uk_user_id` (`user_id`),
  KEY `idx_department_id` (`department_id`),
  KEY `idx_status` (`status`),
  KEY `idx_name` (`name`),
  CONSTRAINT `fk_doctors_department` FOREIGN KEY (`department_id`) REFERENCES `departments` (`department_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_doctors_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='医生表';

-- ----------------------------
-- 技师表
-- ----------------------------
DROP TABLE IF EXISTS `technicians`;
CREATE TABLE `technicians` (
  `tech_id` int NOT NULL AUTO_INCREMENT COMMENT '技师ID（主键）',
  `tech_number` varchar(20) NOT NULL COMMENT '技师编号',
  `name` varchar(100) NOT NULL COMMENT '姓名',
  `department_id` int DEFAULT NULL COMMENT '所属科室ID（外键，引用departments.department_id）',
  `specialty` varchar(200) DEFAULT NULL COMMENT '专长',
  `qualification` varchar(200) DEFAULT NULL COMMENT '资质证书',
  `status` enum('在职','离职','休假') DEFAULT '在职' COMMENT '状态',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`tech_id`),
  UNIQUE KEY `uk_tech_number` (`tech_number`),
  KEY `idx_department_id` (`department_id`),
  KEY `idx_status` (`status`),
  CONSTRAINT `fk_technicians_department` FOREIGN KEY (`department_id`) REFERENCES `departments` (`department_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='技师表';

-- ----------------------------
-- 药剂师表
-- ----------------------------
DROP TABLE IF EXISTS `pharmacists`;
CREATE TABLE `pharmacists` (
  `pharmacist_id` int NOT NULL AUTO_INCREMENT COMMENT '药剂师ID（主键）',
  `pharmacist_number` varchar(20) NOT NULL COMMENT '药剂师编号',
  `name` varchar(100) NOT NULL COMMENT '姓名',
  `department_id` int DEFAULT NULL COMMENT '所属科室ID（外键，引用departments.department_id）',
  `qualification` varchar(200) DEFAULT NULL COMMENT '资质证书',
  `status` enum('在职','离职','休假') DEFAULT '在职' COMMENT '状态',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`pharmacist_id`),
  UNIQUE KEY `uk_pharmacist_number` (`pharmacist_number`),
  KEY `idx_department_id` (`department_id`),
  KEY `idx_status` (`status`),
  CONSTRAINT `fk_pharmacists_department` FOREIGN KEY (`department_id`) REFERENCES `departments` (`department_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='药剂师表';

-- ----------------------------
-- 就诊记录表
-- ----------------------------
DROP TABLE IF EXISTS `medical_visits`;
CREATE TABLE `medical_visits` (
  `visit_id` int NOT NULL AUTO_INCREMENT COMMENT '记录ID（主键）',
  `visit_number` varchar(50) NOT NULL COMMENT '就诊号',
  `patient_id` int NOT NULL COMMENT '患者ID（外键）',
  `hospital_id` int NOT NULL COMMENT '医院ID（外键）',
  `department_id` int NOT NULL COMMENT '科室ID（外键）',
  `doctor_id` int NOT NULL COMMENT '医生ID（外键）',
  `visit_date` datetime NOT NULL COMMENT '就诊时间',
  `visit_type` enum('普通门诊','急诊','住院','转诊','复诊','健康体检','远程会诊') DEFAULT '普通门诊' COMMENT '类型',
  `chief_complaint` varchar(500) DEFAULT NULL COMMENT '主诉',
  `present_illness` text COMMENT '现病史（文本）',
  `past_history` text COMMENT '既往史（文本）',
  `diagnosis` text COMMENT '诊断',
  `advice` text COMMENT '处理意见',
  `temperature` decimal(4,1) DEFAULT NULL COMMENT '体温（℃）',
  `blood_pressure` varchar(20) DEFAULT NULL COMMENT '血压（如：120/80）',
  `heart_rate` int DEFAULT NULL COMMENT '心率（次/分钟）',
  `respiratory_rate` int DEFAULT NULL COMMENT '呼吸频率（次/分钟）',
  `weight` decimal(5,2) DEFAULT NULL COMMENT '体重（kg）',
  `height` decimal(5,2) DEFAULT NULL COMMENT '身高（cm）',
  `bmi` decimal(4,2) DEFAULT NULL COMMENT '身体质量指数',
  `payment_status` enum('未支付','已支付','医保结算','欠费') DEFAULT '未支付' COMMENT '支付状态',
  `total_fee` decimal(10,2) DEFAULT '0.00' COMMENT '总费用（元）',
  `is_emergency` tinyint(1) DEFAULT '0' COMMENT '是否急诊（1=是，0=否）',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`visit_id`),
  UNIQUE KEY `uk_visit_number` (`visit_number`),
  KEY `idx_patient_id` (`patient_id`),
  KEY `idx_hospital_id` (`hospital_id`),
  KEY `idx_department_id` (`department_id`),
  KEY `idx_doctor_id` (`doctor_id`),
  KEY `idx_visit_date` (`visit_date`),
  KEY `idx_visit_type` (`visit_type`),
  KEY `idx_payment_status` (`payment_status`),
  CONSTRAINT `fk_visits_patient` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_visits_hospital` FOREIGN KEY (`hospital_id`) REFERENCES `hospitals` (`hospital_id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_visits_department` FOREIGN KEY (`department_id`) REFERENCES `departments` (`department_id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_visits_doctor` FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`doctor_id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='就诊记录表';

-- ----------------------------
-- 药品目录表
-- ----------------------------
DROP TABLE IF EXISTS `medication_catalog`;
CREATE TABLE `medication_catalog` (
  `med_id` int NOT NULL AUTO_INCREMENT COMMENT '药品ID（主键）',
  `med_code` varchar(50) NOT NULL COMMENT '药品编码',
  `name` varchar(200) NOT NULL COMMENT '药品名称',
  `trade_name` varchar(200) DEFAULT NULL COMMENT '药品商品名',
  `dosage_form` varchar(100) DEFAULT NULL COMMENT '剂型',
  `specification` varchar(200) DEFAULT NULL COMMENT '规格',
  `manufacturer` varchar(200) DEFAULT NULL COMMENT '生产厂家',
  `category` varchar(100) DEFAULT NULL COMMENT '分类',
  `atc_code` varchar(20) DEFAULT NULL COMMENT 'ATC编码',
  `is_prescription` tinyint(1) DEFAULT '0' COMMENT '是否处方药（1=是，0=否）',
  `unit` varchar(20) DEFAULT NULL COMMENT '单位',
  `unit_price` decimal(10,2) DEFAULT '0.00' COMMENT '单价（元）',
  `stock_quantity` int DEFAULT '0' COMMENT '库存数量',
  `min_stock` int DEFAULT '10' COMMENT '最低库存',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否有效（1=是，0=否）',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`med_id`),
  UNIQUE KEY `uk_med_code` (`med_code`),
  KEY `idx_name` (`name`),
  KEY `idx_category` (`category`),
  KEY `idx_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='药品目录表';

-- ----------------------------
-- 检查项目表
-- ----------------------------
DROP TABLE IF EXISTS `examination_items`;
CREATE TABLE `examination_items` (
  `item_id` int NOT NULL AUTO_INCREMENT COMMENT '项目ID（主键）',
  `item_code` varchar(20) NOT NULL COMMENT '项目编码（如：CT001, LAB002）',
  `item_name` varchar(200) NOT NULL COMMENT '项目名称（如：胸部CT平扫、血常规检查）',
  `item_type` enum('影像检查','实验室检查','功能检查','病理检查','其他') NOT NULL COMMENT '项目类型',
  `modality` enum('CT','MRI','X-Ray','超声','内镜','心电图','脑电图','无') DEFAULT '无' COMMENT '检查模态（仅对影像检查）',
  `category` varchar(100) DEFAULT NULL COMMENT '分类（如：放射科、检验科、心电图室）',
  `description` text COMMENT '项目描述',
  `standard_duration` int DEFAULT NULL COMMENT '标准耗时（分钟）',
  `preparation_instructions` text COMMENT '准备说明（文本）',
  `normal_range` json DEFAULT NULL COMMENT '正常值范围（JSON格式，如{"WBC": "4.0-10.0", "RBC": "4.0-5.5"}）',
  `unit` varchar(50) DEFAULT NULL COMMENT '单位（如：mg/dL, U/L, 个/HP）',
  `reference_price` decimal(10,2) DEFAULT '0.00' COMMENT '参考价格（元）',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否启用（1=是，0=否）',
  `created_by` int DEFAULT NULL COMMENT '创建人',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`item_id`),
  UNIQUE KEY `uk_item_code` (`item_code`),
  KEY `idx_item_type` (`item_type`),
  KEY `idx_category` (`category`),
  KEY `idx_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='检查项目表';

-- ----------------------------
-- 检查检验记录表
-- ----------------------------
DROP TABLE IF EXISTS `examination_records`;
CREATE TABLE `examination_records` (
  `exam_id` int NOT NULL AUTO_INCREMENT COMMENT '检查ID（主键）',
  `exam_number` varchar(50) NOT NULL COMMENT '检查单号',
  `visit_id` int NOT NULL COMMENT '关联就诊ID（外键）',
  `item_id` int NOT NULL COMMENT '检查项目ID（外键）',
  `exam_date` datetime NOT NULL COMMENT '检查日期',
  `result_summary` text COMMENT '结果摘要',
  `result_values` json DEFAULT NULL COMMENT '结构化结果（JSON格式）',
  `data_path` varchar(500) DEFAULT NULL COMMENT '原始数据存储路径（如：/images/ct/202312/xxx.dcm）',
  `report_path` varchar(500) DEFAULT NULL COMMENT '报告文件路径（如：/reports/202312/xxx.pdf）',
  `ai_analysis` json DEFAULT NULL COMMENT 'AI辅助分析结果（可选，JSON格式）',
  `status` enum('已预约','进行中','已完成','已取消') DEFAULT '已预约' COMMENT '检查状态',
  `technician_id` int DEFAULT NULL COMMENT '技师ID（外键）',
  `reviewed_by` int DEFAULT NULL COMMENT '审核医生ID（外键，引用doctors.doctor_id）',
  `reviewed_at` datetime DEFAULT NULL COMMENT '审核时间',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`exam_id`),
  UNIQUE KEY `uk_exam_number` (`exam_number`),
  KEY `idx_visit_id` (`visit_id`),
  KEY `idx_item_id` (`item_id`),
  KEY `idx_exam_date` (`exam_date`),
  KEY `idx_status` (`status`),
  KEY `idx_technician_id` (`technician_id`),
  KEY `idx_reviewed_by` (`reviewed_by`),
  CONSTRAINT `fk_exams_visit` FOREIGN KEY (`visit_id`) REFERENCES `medical_visits` (`visit_id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_exams_item` FOREIGN KEY (`item_id`) REFERENCES `examination_items` (`item_id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_exams_technician` FOREIGN KEY (`technician_id`) REFERENCES `technicians` (`tech_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_exams_reviewed_by` FOREIGN KEY (`reviewed_by`) REFERENCES `doctors` (`doctor_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='检查检验记录表';

-- ----------------------------
-- 处方表
-- ----------------------------
DROP TABLE IF EXISTS `prescriptions`;
CREATE TABLE `prescriptions` (
  `prescription_id` int NOT NULL AUTO_INCREMENT COMMENT '处方ID（主键）',
  `prescription_number` varchar(50) NOT NULL COMMENT '处方号',
  `visit_id` int NOT NULL COMMENT '关联就诊ID（外键）',
  `doctor_id` int NOT NULL COMMENT '开方医生ID（外键）',
  `prescription_date` datetime NOT NULL COMMENT '开方日期',
  `diagnosis_for_prescription` text COMMENT '处方诊断',
  `total_amount` decimal(10,2) DEFAULT '0.00' COMMENT '处方总金额（元）',
  `status` enum('未发药','已发药','已退药','已过期') DEFAULT '未发药' COMMENT '状态',
  `is_covered_by_insurance` tinyint(1) DEFAULT '0' COMMENT '是否医保覆盖（1=是，0=否）',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`prescription_id`),
  UNIQUE KEY `uk_prescription_number` (`prescription_number`),
  KEY `idx_visit_id` (`visit_id`),
  KEY `idx_doctor_id` (`doctor_id`),
  KEY `idx_status` (`status`),
  KEY `idx_prescription_date` (`prescription_date`),
  CONSTRAINT `fk_prescriptions_visit` FOREIGN KEY (`visit_id`) REFERENCES `medical_visits` (`visit_id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_prescriptions_doctor` FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`doctor_id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='处方表';

-- ----------------------------
-- 处方明细表
-- ----------------------------
DROP TABLE IF EXISTS `prescription_details`;
CREATE TABLE `prescription_details` (
  `detail_id` int NOT NULL AUTO_INCREMENT COMMENT '明细ID（主键）',
  `prescription_id` int NOT NULL COMMENT '处方ID（外键）',
  `med_id` int NOT NULL COMMENT '药品ID（外键）',
  `quantity` int NOT NULL COMMENT '数量',
  `dosage` varchar(200) DEFAULT NULL COMMENT '用法',
  `duration` int DEFAULT NULL COMMENT '用药天数',
  `frequency` varchar(100) DEFAULT NULL COMMENT '频次',
  `instruction` text COMMENT '用药说明',
  `unit_price` decimal(10,2) DEFAULT '0.00' COMMENT '单价（元）',
  `subtotal` decimal(10,2) DEFAULT '0.00' COMMENT '小计金额（元）',
  `dispensed_by` int DEFAULT NULL COMMENT '发药人ID（外键）',
  `dispensed_at` datetime DEFAULT NULL COMMENT '发药时间',
  PRIMARY KEY (`detail_id`),
  KEY `idx_prescription_id` (`prescription_id`),
  KEY `idx_med_id` (`med_id`),
  KEY `idx_dispensed_by` (`dispensed_by`),
  CONSTRAINT `fk_prescription_details_prescription` FOREIGN KEY (`prescription_id`) REFERENCES `prescriptions` (`prescription_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_prescription_details_med` FOREIGN KEY (`med_id`) REFERENCES `medication_catalog` (`med_id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_prescription_details_dispensed_by` FOREIGN KEY (`dispensed_by`) REFERENCES `pharmacists` (`pharmacist_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='处方明细表';

-- ----------------------------
-- 索引优化
-- ----------------------------
-- 为经常查询的字段添加索引
CREATE INDEX idx_patients_birth_date ON patients(birth_date);
CREATE INDEX idx_doctors_title ON doctors(title);
CREATE INDEX idx_doctors_specialty ON doctors(specialty);
CREATE INDEX idx_medical_visits_payment_status ON medical_visits(payment_status);
CREATE INDEX idx_medical_visits_is_emergency ON medical_visits(is_emergency);
CREATE INDEX idx_examination_records_result_date ON examination_records(exam_date);
CREATE INDEX idx_prescriptions_status_date ON prescriptions(status, prescription_date);

-- ----------------------------
-- 视图
-- ----------------------------
-- 就诊记录视图（包含关联信息）
CREATE OR REPLACE VIEW vw_visit_details AS
SELECT
    mv.visit_id,
    mv.visit_number,
    mv.visit_date,
    mv.visit_type,
    p.patient_id,
    p.name as patient_name,
    p.gender as patient_gender,
    p.birth_date as patient_birth_date,
    d.doctor_id,
    d.name as doctor_name,
    d.title as doctor_title,
    dept.department_id,
    dept.dept_name,
    h.hospital_id,
    h.name as hospital_name,
    mv.diagnosis,
    mv.total_fee,
    mv.payment_status
FROM medical_visits mv
LEFT JOIN patients p ON mv.patient_id = p.patient_id
LEFT JOIN doctors d ON mv.doctor_id = d.doctor_id
LEFT JOIN departments dept ON mv.department_id = dept.department_id
LEFT JOIN hospitals h ON mv.hospital_id = h.hospital_id
WHERE mv.visit_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR);

-- 医生工作量统计视图
CREATE OR REPLACE VIEW vw_doctor_workload AS
SELECT
    d.doctor_id,
    d.name as doctor_name,
    d.title,
    dept.dept_name,
    COUNT(mv.visit_id) as total_visits,
    SUM(mv.total_fee) as total_revenue,
    MIN(mv.visit_date) as first_visit_date,
    MAX(mv.visit_date) as last_visit_date
FROM doctors d
LEFT JOIN medical_visits mv ON d.doctor_id = mv.doctor_id
LEFT JOIN departments dept ON d.department_id = dept.department_id
WHERE mv.visit_date >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
GROUP BY d.doctor_id, d.name, d.title, dept.dept_name
ORDER BY total_visits DESC;

-- 患者就诊历史视图
CREATE OR REPLACE VIEW vw_patient_visits AS
SELECT
    p.patient_id,
    p.name as patient_name,
    p.gender,
    p.birth_date,
    COUNT(DISTINCT mv.visit_id) as total_visits,
    COUNT(DISTINCT mv.hospital_id) as hospitals_visited,
    COUNT(DISTINCT mv.department_id) as departments_visited,
    MIN(mv.visit_date) as first_visit_date,
    MAX(mv.visit_date) as last_visit_date,
    SUM(mv.total_fee) as total_spent
FROM patients p
LEFT JOIN medical_visits mv ON p.patient_id = mv.patient_id
GROUP BY p.patient_id, p.name, p.gender, p.birth_date
HAVING total_visits > 0;

-- ----------------------------
-- 触发器
-- ----------------------------
-- 自动计算BMI
DELIMITER $$
CREATE TRIGGER trg_calculate_bmi BEFORE INSERT ON medical_visits
FOR EACH ROW
BEGIN
    IF NEW.height > 0 AND NEW.weight > 0 THEN
        SET NEW.bmi = NEW.weight / ((NEW.height/100) * (NEW.height/100));
    ELSE
        SET NEW.bmi = NULL;
    END IF;
END
$$
DELIMITER ;

-- 自动更新处方总金额
DELIMITER $$
CREATE TRIGGER trg_update_prescription_total AFTER INSERT ON prescription_details
FOR EACH ROW
BEGIN
    UPDATE prescriptions p
    SET p.total_amount = (
        SELECT SUM(subtotal)
        FROM prescription_details
        WHERE prescription_id = NEW.prescription_id
    )
    WHERE p.prescription_id = NEW.prescription_id;
END
$$
DELIMITER ;

-- 自动更新药品库存
DELIMITER $$
CREATE TRIGGER trg_update_medication_stock AFTER UPDATE ON prescription_details
FOR EACH ROW
BEGIN
    IF NEW.dispensed_by IS NOT NULL AND NEW.dispensed_at IS NOT NULL
       AND (OLD.dispensed_by IS NULL OR OLD.dispensed_at IS NULL) THEN
        UPDATE medication_catalog mc
        SET mc.stock_quantity = mc.stock_quantity - NEW.quantity
        WHERE mc.med_id = NEW.med_id;
    END IF;
END
$$
DELIMITER ;

-- ----------------------------
-- 存储过程
-- ----------------------------
-- 患者注册存储过程
DELIMITER $$
CREATE PROCEDURE sp_register_patient(
    IN p_empi_code VARCHAR(50),
    IN p_name VARCHAR(100),
    IN p_gender ENUM('男','女','未知'),
    IN p_birth_date DATE,
    IN p_id_card_hash VARCHAR(128),
    IN p_phone VARCHAR(20),
    IN p_email VARCHAR(100),
    IN p_address VARCHAR(500),
    IN p_emergency_contact VARCHAR(100),
    IN p_emergency_phone VARCHAR(20)
)
BEGIN
    DECLARE v_patient_id INT;

    -- 检查身份证是否已存在
    IF EXISTS(SELECT 1 FROM patients WHERE id_card_hash = p_id_card_hash) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '身份证号已存在';
    END IF;

    -- 插入患者记录
    INSERT INTO patients (
        empi_code, name, gender, birth_date, id_card_hash,
        phone, email, address, emergency_contact, emergency_phone,
        is_active, created_at, updated_at
    ) VALUES (
        p_empi_code, p_name, p_gender, p_birth_date, p_id_card_hash,
        p_phone, p_email, p_address, p_emergency_contact, p_emergency_phone,
        1, NOW(), NOW()
    );

    SET v_patient_id = LAST_INSERT_ID();

    -- 返回患者ID
    SELECT v_patient_id as patient_id;
END
$$
DELIMITER ;

-- 创建就诊记录存储过程
DELIMITER $$
CREATE PROCEDURE sp_create_medical_visit(
    IN p_patient_id INT,
    IN p_hospital_id INT,
    IN p_department_id INT,
    IN p_doctor_id INT,
    IN p_visit_type ENUM('普通门诊','急诊','住院','转诊','复诊','健康体检','远程会诊'),
    IN p_chief_complaint VARCHAR(500),
    IN p_diagnosis TEXT
)
BEGIN
    DECLARE v_visit_number VARCHAR(50);
    DECLARE v_visit_id INT;

    -- 生成就诊号: 医院代码 + 日期 + 序号
    SET v_visit_number = CONCAT(
        (SELECT hospital_code FROM hospitals WHERE hospital_id = p_hospital_id),
        DATE_FORMAT(NOW(), '%Y%m%d%H%i%s'),
        LPAD(FLOOR(RAND() * 1000), 3, '0')
    );

    -- 插入就诊记录
    INSERT INTO medical_visits (
        visit_number, patient_id, hospital_id, department_id, doctor_id,
        visit_date, visit_type, chief_complaint, diagnosis,
        created_at, updated_at
    ) VALUES (
        v_visit_number, p_patient_id, p_hospital_id, p_department_id, p_doctor_id,
        NOW(), p_visit_type, p_chief_complaint, p_diagnosis,
        NOW(), NOW()
    );

    SET v_visit_id = LAST_INSERT_ID();

    -- 返回就诊信息
    SELECT
        v_visit_id as visit_id,
        v_visit_number as visit_number,
        p.name as patient_name,
        d.name as doctor_name,
        dept.dept_name,
        h.name as hospital_name
    FROM medical_visits mv
    JOIN patients p ON mv.patient_id = p.patient_id
    JOIN doctors d ON mv.doctor_id = d.doctor_id
    JOIN departments dept ON mv.department_id = dept.department_id
    JOIN hospitals h ON mv.hospital_id = h.hospital_id
    WHERE mv.visit_id = v_visit_id;
END
$$
DELIMITER ;

-- 统计医院每日就诊量
DELIMITER $$
CREATE PROCEDURE sp_hospital_daily_stats(
    IN p_hospital_id INT,
    IN p_start_date DATE,
    IN p_end_date DATE
)
BEGIN
    SELECT
        DATE(visit_date) as visit_date,
        COUNT(*) as visit_count,
        SUM(total_fee) as daily_revenue,
        AVG(total_fee) as avg_visit_fee,
        COUNT(DISTINCT doctor_id) as doctors_count,
        COUNT(DISTINCT department_id) as departments_count
    FROM medical_visits
    WHERE hospital_id = p_hospital_id
        AND DATE(visit_date) BETWEEN p_start_date AND p_end_date
    GROUP BY DATE(visit_date)
    ORDER BY visit_date;
END
$$
DELIMITER ;

-- ----------------------------
-- 插入初始数据
-- ----------------------------

-- 插入系统管理员用户
INSERT INTO `users` (`username`, `password_hash`, `email`, `role`, `is_active`) VALUES
('admin', SHA2('admin123', 256), 'admin@hospital.com', '管理员', 1);

-- 插入医院数据
INSERT INTO `hospitals` (`hospital_code`, `name`, `level`, `type`, `address`, `phone`, `is_active`) VALUES
('HOSP001', '中心医院', '三甲', '综合医院', '北京市朝阳区', '010-12345678', 1),
('HOSP002', '人民医院', '三甲', '综合医院', '上海市浦东新区', '021-87654321', 1);

-- 插入科室数据
INSERT INTO `departments` (`hospital_id`, `dept_code`, `dept_name`, `dept_type`, `phone`, `is_active`) VALUES
(1, 'DEP001', '内科', '临床科室', '010-11111111', 1),
(1, 'DEP002', '外科', '临床科室', '010-11111112', 1),
(1, 'DEP003', '放射科', '医技科室', '010-11111113', 1),
(2, 'DEP004', '儿科', '临床科室', '021-22222221', 1);

-- 插入药品数据
INSERT INTO `medication_catalog` (`med_code`, `name`, `dosage_form`, `specification`, `manufacturer`, `category`, `is_prescription`, `unit`, `unit_price`, `stock_quantity`) VALUES
('MED001', '阿司匹林', '片剂', '100mg*20片', '北京制药', '解热镇痛', 1, '盒', 15.50, 100),
('MED002', '头孢克肟', '胶囊', '100mg*12粒', '上海制药', '抗生素', 1, '盒', 45.00, 50);

-- 插入检查项目
INSERT INTO `examination_items` (`item_code`, `item_name`, `item_type`, `modality`, `category`, `reference_price`, `is_active`) VALUES
('CT001', '胸部CT平扫', '影像检查', 'CT', '放射科', 300.00, 1),
('LAB001', '血常规检查', '实验室检查', '无', '检验科', 25.00, 1);

SET FOREIGN_KEY_CHECKS = 1;