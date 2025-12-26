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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `batiment`
--

LOCK TABLES `batiment` WRITE;
/*!40000 ALTER TABLE `batiment` DISABLE KEYS */;
/*!40000 ALTER TABLE `batiment` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `configuration_contraintes`
--

LOCK TABLES `configuration_contraintes` WRITE;
/*!40000 ALTER TABLE `configuration_contraintes` DISABLE KEYS */;
INSERT INTO `configuration_contraintes` VALUES (1,'max_examens_etudiant_par_jour',1,'Maximum 1 examen par jour par Ã©tudiant'),(2,'max_surveillances_prof_par_jour',3,'Maximum 3 surveillances par jour par professeur'),(3,'pourcentage_surveillances_departement',80,'Pourcentage min de surveillances dans son dÃ©partement');
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `departement`
--

LOCK TABLES `departement` WRITE;
/*!40000 ALTER TABLE `departement` DISABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `etudiant`
--

LOCK TABLES `etudiant` WRITE;
/*!40000 ALTER TABLE `etudiant` DISABLE KEYS */;
/*!40000 ALTER TABLE `etudiant` ENABLE KEYS */;
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
  CONSTRAINT `fk_examen_module` FOREIGN KEY (`id_module`) REFERENCES `module` (`id_module`) ON DELETE CASCADE,
  CONSTRAINT `fk_examen_professeur` FOREIGN KEY (`id_professeur`) REFERENCES `professeur` (`id_professeur`) ON DELETE RESTRICT,
  CONSTRAINT `fk_examen_salle` FOREIGN KEY (`id_salle`) REFERENCES `salle` (`id_salle`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `examen`
--

LOCK TABLES `examen` WRITE;
/*!40000 ALTER TABLE `examen` DISABLE KEYS */;
/*!40000 ALTER TABLE `examen` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = cp850 */ ;
/*!50003 SET character_set_results = cp850 */ ;
/*!50003 SET collation_connection  = cp850_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_salle_occupee` BEFORE INSERT ON `examen` FOR EACH ROW BEGIN
    IF EXISTS (
        SELECT 1 FROM examen e
        WHERE e.id_salle = NEW.id_salle
        AND e.date_examen = NEW.date_examen
        AND (
            (NEW.heure_debut BETWEEN e.heure_debut AND e.heure_fin)
            OR (NEW.heure_fin BETWEEN e.heure_debut AND e.heure_fin)
            OR (e.heure_debut BETWEEN NEW.heure_debut AND NEW.heure_fin)
        )
    ) THEN
 SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Salle d‚j… occup‚e … ce cr‚neau';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = cp850 */ ;
/*!50003 SET character_set_results = cp850 */ ;
/*!50003 SET collation_connection  = cp850_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_capacite_salle` BEFORE INSERT ON `examen` FOR EACH ROW BEGIN
    DECLARE nb_etudiants INT;
    DECLARE capacite_salle INT;
    
    
    SELECT COUNT(*) INTO nb_etudiants
    FROM inscription
    WHERE id_module = NEW.id_module;
 
    SELECT capacite INTO capacite_salle
    FROM salle WHERE id_salle = NEW.id_salle;
    
    IF nb_etudiants > capacite_salle THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'La salle est trop petite pour cet examen';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `formation`
--

LOCK TABLES `formation` WRITE;
/*!40000 ALTER TABLE `formation` DISABLE KEYS */;
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
  KEY `fk_inscription_module` (`id_module`),
  CONSTRAINT `fk_inscription_etudiant` FOREIGN KEY (`id_etudiant`) REFERENCES `etudiant` (`id_etudiant`) ON DELETE CASCADE,
  CONSTRAINT `fk_inscription_module` FOREIGN KEY (`id_module`) REFERENCES `module` (`id_module`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inscription`
--

LOCK TABLES `inscription` WRITE;
/*!40000 ALTER TABLE `inscription` DISABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `module`
--

LOCK TABLES `module` WRITE;
/*!40000 ALTER TABLE `module` DISABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `professeur`
--

LOCK TABLES `professeur` WRITE;
/*!40000 ALTER TABLE `professeur` DISABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `salle`
--

LOCK TABLES `salle` WRITE;
/*!40000 ALTER TABLE `salle` DISABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
  KEY `fk_surveillance_professeur` (`id_professeur`),
  CONSTRAINT `fk_surveillance_examen` FOREIGN KEY (`id_examen`) REFERENCES `examen` (`id_examen`) ON DELETE CASCADE,
  CONSTRAINT `fk_surveillance_professeur` FOREIGN KEY (`id_professeur`) REFERENCES `professeur` (`id_professeur`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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

-- Dump completed on 2025-12-25 13:21:58
