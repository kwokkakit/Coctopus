/*
Navicat MySQL Data Transfer

Source Server         : localhost
Source Server Version : 100121
Source Host           : localhost:3306
Source Database       : youxin

Target Server Type    : MYSQL
Target Server Version : 100121
File Encoding         : 65001

Date: 2017-03-20 18:06:34
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for cityinfo
-- ----------------------------
DROP TABLE IF EXISTS `cityinfo`;
CREATE TABLE `cityinfo` (
  `CITY_ID` int(11) NOT NULL,
  `CITY_NAME` varchar(255) DEFAULT NULL,
  `CITY_URL` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`CITY_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=COMPACT;
SET FOREIGN_KEY_CHECKS=1;
