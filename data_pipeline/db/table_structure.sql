-- MySQL dump 10.13  Distrib 8.4.11, for Linux (x86_64)
--
-- Host: localhost    Database: touraqi
-- ------------------------------------------------------
-- Server version	8.4.11

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `aqi_records`
--

DROP TABLE IF EXISTS `aqi_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `aqi_records` (
  `record_id` int NOT NULL AUTO_INCREMENT,
  `siteid` int DEFAULT NULL,
  `sitename` varchar(50) DEFAULT NULL,
  `county` varchar(50) DEFAULT NULL,
  `aqi` varchar(20) DEFAULT NULL,
  `pollutant` varchar(100) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `so2` varchar(20) DEFAULT NULL,
  `co` varchar(20) DEFAULT NULL,
  `o3` varchar(20) DEFAULT NULL,
  `o3_8hr` varchar(20) DEFAULT NULL,
  `pm10` varchar(20) DEFAULT NULL,
  `wind_speed` varchar(20) DEFAULT NULL,
  `wind_direc` varchar(20) DEFAULT NULL,
  `publishtime` datetime DEFAULT NULL,
  `co_8hr` varchar(20) DEFAULT NULL,
  `pm25_avg` varchar(20) DEFAULT NULL,
  `pm10_avg` varchar(20) DEFAULT NULL,
  `so2_avg` varchar(20) DEFAULT NULL,
  `longitude` double DEFAULT NULL,
  `latitude` double DEFAULT NULL,
  `pm25` varchar(20) DEFAULT NULL,
  `no2` varchar(20) DEFAULT NULL,
  `nox` varchar(20) DEFAULT NULL,
  `no` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`record_id`)
) ENGINE=InnoDB AUTO_INCREMENT=85 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `aqi_stations`
--

DROP TABLE IF EXISTS `aqi_stations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `aqi_stations` (
  `siteid` int NOT NULL,
  `sitename` varchar(50) DEFAULT NULL,
  `siteengname` varchar(100) DEFAULT NULL,
  `areaname` varchar(50) DEFAULT NULL,
  `county` varchar(50) DEFAULT NULL,
  `township` varchar(50) DEFAULT NULL,
  `siteaddress` varchar(255) DEFAULT NULL,
  `twd97lon` double DEFAULT NULL,
  `twd97lat` double DEFAULT NULL,
  `sitetype` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`siteid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `attraction_images`
--

DROP TABLE IF EXISTS `attraction_images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attraction_images` (
  `ImageID` int NOT NULL AUTO_INCREMENT,
  `AttractionID` varchar(50) DEFAULT NULL,
  `Name` varchar(255) DEFAULT NULL,
  `Description` text,
  `URL` text,
  PRIMARY KEY (`ImageID`),
  KEY `AttractionID` (`AttractionID`),
  CONSTRAINT `attraction_images_ibfk_1` FOREIGN KEY (`AttractionID`) REFERENCES `attractions` (`AttractionID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5167 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `attractions`
--

DROP TABLE IF EXISTS `attractions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attractions` (
  `AttractionID` varchar(50) NOT NULL,
  `AttractionName` varchar(255) DEFAULT NULL,
  `Description` text,
  `PositionLat` double DEFAULT NULL,
  `PositionLon` double DEFAULT NULL,
  `AttractionClasses` json DEFAULT NULL,
  `Telephones` json DEFAULT NULL,
  `TrafficInfo` text,
  `ParkingInfo` text,
  `IsAccessibleForFree` tinyint DEFAULT NULL,
  `LocatedCities` json DEFAULT NULL,
  `PostalAddress_City` varchar(50) DEFAULT NULL,
  `PostalAddress_CityCode` varchar(20) DEFAULT NULL,
  `PostalAddress_Town` varchar(50) DEFAULT NULL,
  `PostalAddress_TownCode` varchar(20) DEFAULT NULL,
  `PostalAddress_StreetAddress` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`AttractionID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `town_boundaries`
--

DROP TABLE IF EXISTS `town_boundaries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `town_boundaries` (
  `TOWNID` varchar(20) NOT NULL,
  `TOWNCODE` varchar(20) DEFAULT NULL,
  `COUNTYNAME` varchar(50) DEFAULT NULL,
  `TOWNNAME` varchar(50) DEFAULT NULL,
  `TOWNENG` varchar(100) DEFAULT NULL,
  `COUNTYID` varchar(20) DEFAULT NULL,
  `COUNTYCODE` varchar(20) DEFAULT NULL,
  `geometry_geojson` longtext,
  PRIMARY KEY (`TOWNID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-24 22:43:43
