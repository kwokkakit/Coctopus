/*
Navicat MySQL Data Transfer

Source Server         : localhost
Source Server Version : 100121
Source Host           : localhost:3306
Source Database       : youxin

Target Server Type    : MYSQL
Target Server Version : 100121
File Encoding         : 65001

Date: 2017-03-20 18:06:26
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for carsummer
-- ----------------------------
DROP TABLE IF EXISTS `carsummer`;
CREATE TABLE `carsummer` (
  `car_id` int(11) NOT NULL COMMENT '车编号',
  `car_title` varchar(255) DEFAULT NULL COMMENT '车辆标题',
  `license_date` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '上牌时间',
  `sale_date` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '上架时间',
  `displacement` varchar(255) DEFAULT NULL COMMENT '排量',
  `is_FYB` binary(10) DEFAULT NULL COMMENT '是否付一般',
  `effluent` varchar(255) DEFAULT NULL COMMENT '排放标准',
  `meters` int(255) DEFAULT NULL COMMENT '里程',
  `full_price` float(255,2) DEFAULT NULL COMMENT '车辆价格',
  `city_id` int(11) DEFAULT NULL COMMENT '城市ID',
  `is_onsale` binary(10) DEFAULT NULL COMMENT '是否在售',
  PRIMARY KEY (`car_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
SET FOREIGN_KEY_CHECKS=1;
