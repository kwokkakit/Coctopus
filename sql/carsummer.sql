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
  `CAR_ID` int(11) NOT NULL COMMENT '车编号',
  `CAR_TITLE` varchar(255) DEFAULT NULL COMMENT '车辆标题',
  `LICENSE_DATE` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '上牌时间',
  `SALE_DATE` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '上架时间',
  `DISPLACEMENT` varchar(255) DEFAULT NULL COMMENT '排量',
  `IS_FYB` binary(10) DEFAULT NULL COMMENT '是否付一般',
  `EFFLUENT` varchar(255) DEFAULT NULL COMMENT '排放标准',
  `METERS` int(255) DEFAULT NULL COMMENT '里程',
  `FULL_PRICE` float(255,2) DEFAULT NULL COMMENT '车辆价格',
  `CITY_ID` int(11) DEFAULT NULL COMMENT '城市ID',
  `IS_ONSALE` binary(10) DEFAULT NULL COMMENT '是否在售',
  PRIMARY KEY (`CAR_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
SET FOREIGN_KEY_CHECKS=1;
