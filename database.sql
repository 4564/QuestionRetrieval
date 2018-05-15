CREATE DATABASE  IF NOT EXISTS `question_answer` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;
USE `question_answer`;
-- MySQL dump 10.13  Distrib 5.7.9, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: question_answer
-- ------------------------------------------------------
-- Server version	5.7.9-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `candidate`
--

DROP TABLE IF EXISTS `candidate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `candidate` (
  `query_id` bigint(20) NOT NULL COMMENT '查询id',
  `candidate_id` bigint(20) NOT NULL COMMENT '候选id',
  `relevance` int(11) NOT NULL DEFAULT '0' COMMENT '相关性，0：不相关，1：相关，但不一定找到答案，2：相关，找到答案',
  `flag` int(11) NOT NULL DEFAULT '0' COMMENT '标记\n-1：还没有人标记过，需要标记\n0：默认值，还没人标记过，不需要标记\n1：1号标记过\n2：2号标记过\n3：1，2号都标记过但是两者不一样，用一个两位数来区分：个位1号，十位2号\n4：最终结果',
  PRIMARY KEY (`query_id`,`candidate_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='候选集';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `qa`
--

DROP TABLE IF EXISTS `qa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `qa` (
  `question_id` bigint(20) NOT NULL COMMENT '问题ID',
  `questioner_id` bigint(20) NOT NULL COMMENT '提问者ID',
  `question` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '问题内容',
  `answer_id` bigint(20) NOT NULL COMMENT '回答ID',
  `answerer_id` bigint(20) NOT NULL COMMENT '回答者ID',
  `answer` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '回答内容',
  PRIMARY KEY (`answer_id`),
  KEY `question_id_index` (`question_id`),
  KEY `questioner_id_index` (`questioner_id`),
  KEY `answerer_id_index` (`answerer_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='问答表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `query`
--

DROP TABLE IF EXISTS `query`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `query` (
  `id` bigint(20) NOT NULL COMMENT '查询id （同与问题id）',
  `segmented_query` text COLLATE utf8mb4_unicode_ci COMMENT '查询文本',
  `weight_tf_idf` text COLLATE utf8mb4_unicode_ci COMMENT 'tf_idf词项权重',
  `weight_ie` text COLLATE utf8mb4_unicode_ci COMMENT '信息熵权重',
  `weight_topic` text COLLATE utf8mb4_unicode_ci COMMENT '主题模型权重',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='查询表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `id` bigint(20) NOT NULL COMMENT '用户ID',
  `askCnt` int(11) NOT NULL COMMENT '提问数',
  `ansCnt` int(11) NOT NULL COMMENT '回答数',
  `adopt` float NOT NULL COMMENT '被采纳率',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-05-15 21:45:28
