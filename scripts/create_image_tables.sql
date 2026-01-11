-- create_image_tables.sql
-- 医疗数据库图片存储表结构

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 创建影像分类表
DROP TABLE IF EXISTS `image_categories`;
CREATE TABLE `image_categories` (
  `category_id` int NOT NULL AUTO_INCREMENT,
  `category_name` varchar(50) NOT NULL COMMENT '分类名称',
  `description` text COMMENT '分类描述',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`category_id`),
  UNIQUE KEY `category_name` (`category_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='图片分类表';

-- 创建医疗图片存储表
DROP TABLE IF EXISTS `medical_images`;
CREATE TABLE `medical_images` (
  `image_id` int NOT NULL AUTO_INCREMENT,
  `original_filename` varchar(255) NOT NULL COMMENT '原始文件名',
  `stored_filename` varchar(255) NOT NULL COMMENT '存储文件名',
  `file_path` varchar(500) NOT NULL COMMENT '文件路径',
  `file_size` bigint NOT NULL COMMENT '文件大小(字节)',
  `mime_type` varchar(100) NOT NULL COMMENT '文件类型',
  `image_width` int DEFAULT NULL COMMENT '图片宽度',
  `image_height` int DEFAULT NULL COMMENT '图片高度',
  `category_id` int DEFAULT NULL COMMENT '图片分类ID',
  `patient_id` int DEFAULT NULL COMMENT '关联患者ID',
  `visit_id` int DEFAULT NULL COMMENT '关联就诊记录ID',
  `doctor_id` int DEFAULT NULL COMMENT '关联医生ID',
  `title` varchar(200) DEFAULT NULL COMMENT '图片标题',
  `description` text COMMENT '图片描述',
  `tags` varchar(500) DEFAULT NULL COMMENT '标签，用逗号分隔',
  `is_public` tinyint(1) DEFAULT '0' COMMENT '是否公开',
  `is_deleted` tinyint(1) DEFAULT '0' COMMENT '是否已删除',
  `uploaded_by` int DEFAULT NULL COMMENT '上传者用户ID',
  `upload_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
  `last_viewed` timestamp NULL DEFAULT NULL COMMENT '最后查看时间',
  `view_count` int DEFAULT '0' COMMENT '查看次数',
  PRIMARY KEY (`image_id`),
  UNIQUE KEY `stored_filename` (`stored_filename`),
  KEY `idx_patient_id` (`patient_id`),
  KEY `idx_visit_id` (`visit_id`),
  KEY `idx_doctor_id` (`doctor_id`),
  KEY `idx_category_id` (`category_id`),
  KEY `idx_upload_time` (`upload_time`),
  KEY `idx_is_deleted` (`is_deleted`),
  CONSTRAINT `medical_images_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `image_categories` (`category_id`) ON DELETE SET NULL,
  CONSTRAINT `medical_images_ibfk_2` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`) ON DELETE CASCADE,
  CONSTRAINT `medical_images_ibfk_3` FOREIGN KEY (`visit_id`) REFERENCES `medical_visits` (`visit_id`) ON DELETE CASCADE,
  CONSTRAINT `medical_images_ibfk_4` FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`doctor_id`) ON DELETE SET NULL,
  CONSTRAINT `medical_images_ibfk_5` FOREIGN KEY (`uploaded_by`) REFERENCES `users` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='医疗图片存储表';

-- 创建图片缩略图表
DROP TABLE IF EXISTS `image_thumbnails`;
CREATE TABLE `image_thumbnails` (
  `thumbnail_id` int NOT NULL AUTO_INCREMENT,
  `image_id` int NOT NULL COMMENT '原图ID',
  `thumbnail_size` varchar(50) NOT NULL COMMENT '缩略图尺寸(如: small, medium, large)',
  `thumbnail_path` varchar(500) NOT NULL COMMENT '缩略图路径',
  `width` int NOT NULL COMMENT '缩略图宽度',
  `height` int NOT NULL COMMENT '缩略图高度',
  `file_size` bigint NOT NULL COMMENT '文件大小',
  PRIMARY KEY (`thumbnail_id`),
  UNIQUE KEY `uk_image_size` (`image_id`,`thumbnail_size`),
  KEY `idx_image_id` (`image_id`),
  CONSTRAINT `image_thumbnails_ibfk_1` FOREIGN KEY (`image_id`) REFERENCES `medical_images` (`image_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='图片缩略图表';

-- 插入初始分类数据
INSERT INTO `image_categories` (`category_name`, `description`) VALUES
('患者照片', '患者面部照片、全身照等'),
('身份证件', '身份证、医保卡等证件照片'),
('检查报告', 'CT、X光、B超等检查报告图片'),
('诊断图片', '医生诊断时拍摄的图片'),
('处方单', '手写或电子处方照片'),
('化验单', '血液、尿液等化验结果'),
('心电图', '心电图扫描图片'),
('病历照片', '病历本、病历记录照片'),
('其他', '其他类型的医疗图片');

SET FOREIGN_KEY_CHECKS = 1;