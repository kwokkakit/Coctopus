/*
Navicat MySQL Data Transfer

Source Server         : localhost
Source Server Version : 100121
Source Host           : localhost:3306
Source Database       : youxin

Target Server Type    : MYSQL
Target Server Version : 100121
File Encoding         : 65001

Date: 2017-03-23 19:26:32
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for modelinfo
-- ----------------------------
DROP TABLE IF EXISTS `modelinfo`;
CREATE TABLE `modelinfo` (
  `model_id` int(11) NOT NULL,
  `model_name` varchar(255) DEFAULT NULL,
  `model_url` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`model_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
SET FOREIGN_KEY_CHECKS=1;
