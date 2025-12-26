-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: optimisation_edt
-- ------------------------------------------------------
-- Server version	8.0.19

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
USE optimisation_edt;
--
-- Table structure for table `batiment`
--

DROP TABLE IF EXISTS `batiment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `batiment` (
  `id_batiment` int NOT NULL,
  `nom` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_batiment`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `batiment`
--

LOCK TABLES `batiment` WRITE;
/*!40000 ALTER TABLE `batiment` DISABLE KEYS */;
INSERT INTO `batiment` VALUES (1,'Bâtiment A'),(2,'Bâtiment B'),(3,'Bâtiment C');
/*!40000 ALTER TABLE `batiment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cache_capacite_examens`
--

DROP TABLE IF EXISTS `cache_capacite_examens`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cache_capacite_examens` (
  `id_examen` int NOT NULL,
  `nb_etudiants_inscrits` int NOT NULL,
  `capacite_salle` int NOT NULL,
  `date_mise_a_jour` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_examen`),
  CONSTRAINT `cache_capacite_examens_ibfk_1` FOREIGN KEY (`id_examen`) REFERENCES `examen` (`id_examen`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cache_capacite_examens`
--

LOCK TABLES `cache_capacite_examens` WRITE;
/*!40000 ALTER TABLE `cache_capacite_examens` DISABLE KEYS */;
INSERT INTO `cache_capacite_examens` VALUES (1,4,50,'2025-12-26 17:52:42'),(2,4,25,'2025-12-26 17:55:04');
/*!40000 ALTER TABLE `cache_capacite_examens` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `configuration_contraintes`
--

DROP TABLE IF EXISTS `configuration_contraintes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `configuration_contraintes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) DEFAULT NULL,
  `valeur` int DEFAULT NULL,
  `description` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nom` (`nom`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `configuration_contraintes`
--

LOCK TABLES `configuration_contraintes` WRITE;
/*!40000 ALTER TABLE `configuration_contraintes` DISABLE KEYS */;
INSERT INTO `configuration_contraintes` VALUES (1,'max_examens_etudiant_par_jour',1,'Maximum 1 examen par jour par étudiant'),(2,'max_surveillances_prof_par_jour',3,'Maximum 3 surveillances par jour par professeur'),(3,'pourcentage_surveillances_departement',80,'Pourcentage min de surveillances dans son département');
/*!40000 ALTER TABLE `configuration_contraintes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `departement`
--

DROP TABLE IF EXISTS `departement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `departement` (
  `id_dep` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) NOT NULL,
  PRIMARY KEY (`id_dep`),
  UNIQUE KEY `nom` (`nom`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `departement`
--

LOCK TABLES `departement` WRITE;
/*!40000 ALTER TABLE `departement` DISABLE KEYS */;
INSERT INTO `departement` VALUES (5,'Biologie'),(4,'Chimie'),(1,'Informatique'),(2,'Mathématiques'),(3,'Physique');
/*!40000 ALTER TABLE `departement` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `etudiant`
--

DROP TABLE IF EXISTS `etudiant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `etudiant` (
  `id_etudiant` int NOT NULL AUTO_INCREMENT,
  `matricule` varchar(30) NOT NULL,
  `nom` varchar(100) NOT NULL,
  `prenom` varchar(100) NOT NULL,
  `promo` varchar(10) DEFAULT NULL,
  `id_formation` int NOT NULL,
  PRIMARY KEY (`id_etudiant`),
  UNIQUE KEY `matricule` (`matricule`),
  KEY `fk_etudiant_formation` (`id_formation`),
  CONSTRAINT `fk_etudiant_formation` FOREIGN KEY (`id_formation`) REFERENCES `formation` (`id_formation`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `etudiant`
--

LOCK TABLES `etudiant` WRITE;
/*!40000 ALTER TABLE `etudiant` DISABLE KEYS */;
INSERT INTO `etudiant` VALUES (1,'ETU001','Durand','Paul','2024',1),(2,'ETU002','Moreau','Julie','2024',1),(3,'ETU003','Lefevre','Marc','2024',1),(4,'ETU004','Rousseau','Anna','2024',1),(5,'ETU005','Girard','Luc','2024',1);
/*!40000 ALTER TABLE `etudiant` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `etudiant_examens_jour`
--

DROP TABLE IF EXISTS `etudiant_examens_jour`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `etudiant_examens_jour` (
  `id_etudiant` int NOT NULL,
  `date_examen` date NOT NULL,
  `nb_examens` int DEFAULT '0',
  `liste_examens` text,
  PRIMARY KEY (`id_etudiant`,`date_examen`),
  KEY `idx_date_nb` (`date_examen`,`nb_examens`),
  CONSTRAINT `etudiant_examens_jour_ibfk_1` FOREIGN KEY (`id_etudiant`) REFERENCES `etudiant` (`id_etudiant`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `etudiant_examens_jour`
--

LOCK TABLES `etudiant_examens_jour` WRITE;
/*!40000 ALTER TABLE `etudiant_examens_jour` DISABLE KEYS */;
INSERT INTO `etudiant_examens_jour` VALUES (1,'2024-12-28',1,'1'),(1,'2024-12-29',1,'2'),(2,'2024-12-28',1,'1'),(2,'2024-12-29',1,'2'),(3,'2024-12-28',1,'1'),(3,'2024-12-29',1,'2'),(5,'2024-12-28',1,'1'),(5,'2024-12-29',1,'2');
/*!40000 ALTER TABLE `etudiant_examens_jour` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `examen`
--

DROP TABLE IF EXISTS `examen`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `examen` (
  `id_examen` int NOT NULL AUTO_INCREMENT,
  `id_module` int NOT NULL,
  `id_professeur` int NOT NULL,
  `id_salle` int NOT NULL,
  `date_examen` date NOT NULL,
  `heure_debut` time NOT NULL,
  `duree_minutes` int NOT NULL,
  `annee_univ` varchar(9) NOT NULL,
  `type_session` enum('normal','rattrapage') DEFAULT 'normal',
  `heure_fin` time GENERATED ALWAYS AS (addtime(`heure_debut`,sec_to_time((`duree_minutes` * 60)))) STORED,
  PRIMARY KEY (`id_examen`),
  KEY `fk_examen_module` (`id_module`),
  KEY `fk_examen_professeur` (`id_professeur`),
  KEY `fk_examen_salle` (`id_salle`),
  KEY `idx_examen_date_salle` (`date_examen`,`id_salle`,`heure_debut`),
  KEY `idx_examen_date_prof` (`date_examen`,`id_professeur`),
  CONSTRAINT `fk_examen_module` FOREIGN KEY (`id_module`) REFERENCES `module` (`id_module`) ON DELETE CASCADE,
  CONSTRAINT `fk_examen_professeur` FOREIGN KEY (`id_professeur`) REFERENCES `professeur` (`id_professeur`) ON DELETE RESTRICT,
  CONSTRAINT `fk_examen_salle` FOREIGN KEY (`id_salle`) REFERENCES `salle` (`id_salle`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `examen`
--

LOCK TABLES `examen` WRITE;
/*!40000 ALTER TABLE `examen` DISABLE KEYS */;
INSERT INTO `examen` (`id_examen`, `id_module`, `id_professeur`, `id_salle`, `date_examen`, `heure_debut`, `duree_minutes`, `annee_univ`, `type_session`) VALUES (1,1,1,2,'2024-12-28','09:00:00',120,'2024-2025','normal'),(2,1,1,6,'2024-12-29','09:00:00',120,'2024-2025','normal');
/*!40000 ALTER TABLE `examen` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `formation`
--

DROP TABLE IF EXISTS `formation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `formation` (
  `id_formation` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(150) NOT NULL,
  `niveau` enum('L1','L2','L3','M1','M2') NOT NULL,
  `id_departement` int NOT NULL,
  `nb_modules` int NOT NULL,
  PRIMARY KEY (`id_formation`),
  KEY `fk_formation_departement` (`id_departement`),
  CONSTRAINT `fk_formation_departement` FOREIGN KEY (`id_departement`) REFERENCES `departement` (`id_dep`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `formation`
--

LOCK TABLES `formation` WRITE;
/*!40000 ALTER TABLE `formation` DISABLE KEYS */;
INSERT INTO `formation` VALUES (1,'Licence Informatique','L1',1,8),(2,'Licence Informatique','L2',1,8),(3,'Licence Informatique','L3',1,8),(4,'Master Informatique','M1',1,10),(5,'Master Informatique','M2',1,10),(6,'Licence Mathématiques','L1',2,8),(7,'Licence Physique','L1',3,8);
/*!40000 ALTER TABLE `formation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inscription`
--

DROP TABLE IF EXISTS `inscription`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inscription` (
  `id_etudiant` int NOT NULL,
  `id_module` int NOT NULL,
  `note` decimal(4,2) DEFAULT NULL,
  PRIMARY KEY (`id_etudiant`,`id_module`),
  KEY `idx_inscription_module` (`id_module`),
  KEY `idx_inscription_etudiant` (`id_etudiant`),
  CONSTRAINT `fk_inscription_etudiant` FOREIGN KEY (`id_etudiant`) REFERENCES `etudiant` (`id_etudiant`) ON DELETE CASCADE,
  CONSTRAINT `fk_inscription_module` FOREIGN KEY (`id_module`) REFERENCES `module` (`id_module`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inscription`
--

LOCK TABLES `inscription` WRITE;
/*!40000 ALTER TABLE `inscription` DISABLE KEYS */;
INSERT INTO `inscription` VALUES (1,1,NULL),(1,2,NULL),(1,3,NULL),(2,1,NULL),(2,2,NULL),(3,1,NULL),(3,3,NULL),(3,4,NULL),(4,2,NULL),(4,3,NULL),(5,1,NULL),(5,4,NULL);
/*!40000 ALTER TABLE `inscription` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `module`
--

DROP TABLE IF EXISTS `module`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `module` (
  `id_module` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(150) NOT NULL,
  `code_module` varchar(20) NOT NULL,
  `credits` int NOT NULL,
  `semestre` int NOT NULL,
  `id_formation` int NOT NULL,
  `id_module_prerequis` int DEFAULT NULL,
  PRIMARY KEY (`id_module`),
  UNIQUE KEY `code_module` (`code_module`),
  KEY `fk_module_formation` (`id_formation`),
  KEY `fk_module_prerequis` (`id_module_prerequis`),
  CONSTRAINT `fk_module_formation` FOREIGN KEY (`id_formation`) REFERENCES `formation` (`id_formation`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_module_prerequis` FOREIGN KEY (`id_module_prerequis`) REFERENCES `module` (`id_module`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `module`
--

LOCK TABLES `module` WRITE;
/*!40000 ALTER TABLE `module` DISABLE KEYS */;
INSERT INTO `module` VALUES (1,'Algorithmique','INF101',6,1,1,NULL),(2,'Programmation','INF102',6,1,1,NULL),(3,'Bases de données','INF103',6,2,1,NULL),(4,'Réseaux','INF104',6,2,1,NULL),(5,'Maths pour informatique','INF105',3,1,1,NULL),(6,'Systèmes d\'exploitation','INF106',6,2,1,NULL);
/*!40000 ALTER TABLE `module` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `professeur`
--

DROP TABLE IF EXISTS `professeur`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `professeur` (
  `id_professeur` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) NOT NULL,
  `prenom` varchar(100) NOT NULL,
  `specialite` varchar(100) DEFAULT NULL,
  `grade` varchar(50) DEFAULT NULL,
  `id_departement` int NOT NULL,
  `total_surveillances` int DEFAULT '0',
  PRIMARY KEY (`id_professeur`),
  KEY `fk_prof_departement` (`id_departement`),
  CONSTRAINT `fk_prof_departement` FOREIGN KEY (`id_departement`) REFERENCES `departement` (`id_dep`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `professeur`
--

LOCK TABLES `professeur` WRITE;
/*!40000 ALTER TABLE `professeur` DISABLE KEYS */;
INSERT INTO `professeur` VALUES (1,'Bouchenak','Fatima','Base de données','Professeur',1,0),(2,'Khelifi','Ahmed','Algorithmique','Maître de conférences',1,0),(3,'Bensaid','Karim','Réseaux','Professeur',1,0),(4,'Benali','Nadia','Programmation','Maître de conférences',1,0),(5,'Mansouri','Yacine','Mathématiques','Professeur',2,0),(6,'Chaouch','Leïla','Systèmes d\'exploitation','Professeur',1,0),(7,'Zerrouki','Mohamed','Intelligence Artificielle','Professeur',1,0),(8,'Saadi','Samira','Sécurité informatique','Maître de conférences',1,0),(9,'Taleb','Omar','Cloud Computing','Professeur',1,0),(10,'Abbas','Rym','Big Data','Maître de conférences',1,0);
/*!40000 ALTER TABLE `professeur` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `salle`
--

DROP TABLE IF EXISTS `salle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `salle` (
  `id_salle` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(50) NOT NULL,
  `capacite` int NOT NULL,
  `type` enum('salle','amphi','labo') NOT NULL,
  `id_batiment` int NOT NULL,
  PRIMARY KEY (`id_salle`),
  KEY `fk_salle_batiment` (`id_batiment`),
  CONSTRAINT `fk_salle_batiment` FOREIGN KEY (`id_batiment`) REFERENCES `batiment` (`id_batiment`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `salle`
--

LOCK TABLES `salle` WRITE;
/*!40000 ALTER TABLE `salle` DISABLE KEYS */;
INSERT INTO `salle` VALUES (1,'Amphi 100',300,'amphi',1),(2,'Salle 101',50,'salle',1),(3,'Salle 102',50,'salle',1),(4,'Salle 201',30,'salle',2),(5,'Salle 202',30,'salle',2),(6,'Labo Info 1',25,'labo',3),(7,'Labo Info 2',25,'labo',3);
/*!40000 ALTER TABLE `salle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `suivi_surveillances_jour`
--

DROP TABLE IF EXISTS `suivi_surveillances_jour`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `suivi_surveillances_jour` (
  `id_professeur` int NOT NULL,
  `date_surveillance` date NOT NULL,
  `nombre_surveillances` int DEFAULT '0',
  PRIMARY KEY (`id_professeur`,`date_surveillance`),
  CONSTRAINT `suivi_surveillances_jour_ibfk_1` FOREIGN KEY (`id_professeur`) REFERENCES `professeur` (`id_professeur`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `suivi_surveillances_jour`
--

LOCK TABLES `suivi_surveillances_jour` WRITE;
/*!40000 ALTER TABLE `suivi_surveillances_jour` DISABLE KEYS */;
/*!40000 ALTER TABLE `suivi_surveillances_jour` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `surveillance`
--

DROP TABLE IF EXISTS `surveillance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `surveillance` (
  `id_examen` int NOT NULL,
  `id_professeur` int NOT NULL,
  `role` enum('principal','assistant') DEFAULT 'assistant',
  PRIMARY KEY (`id_examen`,`id_professeur`),
  KEY `idx_surveillance_prof` (`id_professeur`),
  CONSTRAINT `fk_surveillance_examen` FOREIGN KEY (`id_examen`) REFERENCES `examen` (`id_examen`) ON DELETE CASCADE,
  CONSTRAINT `fk_surveillance_professeur` FOREIGN KEY (`id_professeur`) REFERENCES `professeur` (`id_professeur`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `surveillance`
--

LOCK TABLES `surveillance` WRITE;
/*!40000 ALTER TABLE `surveillance` DISABLE KEYS */;
/*!40000 ALTER TABLE `surveillance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `utilisateur`
--

DROP TABLE IF EXISTS `utilisateur`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `utilisateur` (
  `id_compte` int NOT NULL AUTO_INCREMENT,
  `email` varchar(100) NOT NULL,
  `mot_de_passe_hash` varchar(255) NOT NULL,
  `type_utilisateur` enum('vice_doyen','admin_examens','chef_departement','professeur','etudiant') NOT NULL,
  `id_professeur` int DEFAULT NULL,
  `id_etudiant` int DEFAULT NULL,
  `actif` tinyint(1) DEFAULT '1',
  `date_creation` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_compte`),
  UNIQUE KEY `email` (`email`),
  KEY `fk_compte_professeur` (`id_professeur`),
  KEY `fk_compte_etudiant` (`id_etudiant`),
  CONSTRAINT `fk_compte_etudiant` FOREIGN KEY (`id_etudiant`) REFERENCES `etudiant` (`id_etudiant`) ON DELETE CASCADE,
  CONSTRAINT `fk_compte_professeur` FOREIGN KEY (`id_professeur`) REFERENCES `professeur` (`id_professeur`) ON DELETE CASCADE,
  CONSTRAINT `chk_type_reference` CHECK ((((`type_utilisateur` in (_cp850'vice_doyen',_cp850'admin_examens',_cp850'chef_departement',_cp850'professeur')) and (`id_professeur` is not null) and (`id_etudiant` is null)) or ((`type_utilisateur` = _cp850'etudiant') and (`id_etudiant` is not null) and (`id_professeur` is null)) or ((`type_utilisateur` = _cp850'admin_examens') and (`id_professeur` is null) and (`id_etudiant` is null))))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `utilisateur`
--

LOCK TABLES `utilisateur` WRITE;
/*!40000 ALTER TABLE `utilisateur` DISABLE KEYS */;
/*!40000 ALTER TABLE `utilisateur` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `vue_etudiants_conflits`
--

DROP TABLE IF EXISTS `vue_etudiants_conflits`;
/*!50001 DROP VIEW IF EXISTS `vue_etudiants_conflits`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vue_etudiants_conflits` AS SELECT 
 1 AS `id_etudiant`,
 1 AS `date_examen`,
 1 AS `nb_examens`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vue_profs_surcharges`
--

DROP TABLE IF EXISTS `vue_profs_surcharges`;
/*!50001 DROP VIEW IF EXISTS `vue_profs_surcharges`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vue_profs_surcharges` AS SELECT 
 1 AS `id_professeur`,
 1 AS `date_surveillance`,
 1 AS `nombre_surveillances`*/;
SET character_set_client = @saved_cs_client;

--
-- Final view structure for view `vue_etudiants_conflits`
--

/*!50001 DROP VIEW IF EXISTS `vue_etudiants_conflits`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = cp850 */;
/*!50001 SET character_set_results     = cp850 */;
/*!50001 SET collation_connection      = cp850_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vue_etudiants_conflits` AS select `i`.`id_etudiant` AS `id_etudiant`,`ex`.`date_examen` AS `date_examen`,count(distinct `ex`.`id_examen`) AS `nb_examens` from ((`inscription` `i` join `examen` `ex` on((`i`.`id_module` = `ex`.`id_module`))) join `etudiant` `et` on((`i`.`id_etudiant` = `et`.`id_etudiant`))) group by `i`.`id_etudiant`,`ex`.`date_examen` having (`nb_examens` > 1) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vue_profs_surcharges`
--

/*!50001 DROP VIEW IF EXISTS `vue_profs_surcharges`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = cp850 */;
/*!50001 SET character_set_results     = cp850 */;
/*!50001 SET collation_connection      = cp850_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vue_profs_surcharges` AS select `p`.`id_professeur` AS `id_professeur`,`s`.`date_surveillance` AS `date_surveillance`,`s`.`nombre_surveillances` AS `nombre_surveillances` from (`suivi_surveillances_jour` `s` join `professeur` `p` on((`s`.`id_professeur` = `p`.`id_professeur`))) where (`s`.`nombre_surveillances` > (select `configuration_contraintes`.`valeur` from `configuration_contraintes` where (`configuration_contraintes`.`nom` = 'max_surveillances_prof_par_jour'))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-26 18:59:57
