CREATE DATABASE  IF NOT EXISTS `atopa` /*!40100 DEFAULT CHARACTER SET utf8 */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `atopa`;
-- MySQL dump 10.13  Distrib 8.0.19, for Win64 (x86_64)
--
-- Host: localhost    Database: atopa
-- ------------------------------------------------------
-- Server version	8.0.19

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alumno`
--

DROP TABLE IF EXISTS `alumno`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alumno` (
  `id` int NOT NULL AUTO_INCREMENT,
  `clase` int DEFAULT NULL,
  `fecha_nacimiento` varchar(10) NOT NULL,
  `sexo` varchar(1) NOT NULL,
  `user` int NOT NULL,
  `year` int NOT NULL,
  `alias` varchar(45) NOT NULL,
  `activo` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `alias_UNIQUE` (`alias`),
  KEY `idClase_idx` (`clase`),
  KEY `idUser_idx` (`user`),
  KEY `idYear_idx` (`year`),
  CONSTRAINT `idClaseAlumno` FOREIGN KEY (`clase`) REFERENCES `clase` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `idUserAlumno` FOREIGN KEY (`user`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `idYearAlumno` FOREIGN KEY (`year`) REFERENCES `year` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alumno`
--

LOCK TABLES `alumno` WRITE;
/*!40000 ALTER TABLE `alumno` DISABLE KEYS */;
INSERT INTO `alumno` VALUES (1,1,'11-11-2004','M',2,1,'aa1',1),(2,1,'22-02-2005','H',3,1,'aa2',1),(3,1,'02-02-2005','M',5,1,'aa3',1),(4,5,'22-03-2004','M',6,1,'aa4',1),(5,4,'22-05-2005','H',7,1,'aaa5',1),(12,NULL,'11-05-2006','M',14,1,'aa6',1),(14,NULL,'11-05-2008','H',16,1,'al7 ap',1),(15,NULL,'11-06-2009','M',17,1,'al8 ap',1);
/*!40000 ALTER TABLE `alumno` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `alumnostest`
--

DROP TABLE IF EXISTS `alumnostest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alumnostest` (
  `id` int NOT NULL AUTO_INCREMENT,
  `test` int NOT NULL,
  `alumno` int NOT NULL,
  `answer` int DEFAULT NULL,
  `code` varchar(255) DEFAULT NULL,
  `activo` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code_UNIQUE` (`code`),
  KEY `idTest_idx` (`test`),
  KEY `idAlumno_idx` (`alumno`),
  CONSTRAINT `idAlumnoTest` FOREIGN KEY (`alumno`) REFERENCES `alumno` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `idTestAlumno` FOREIGN KEY (`test`) REFERENCES `test` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alumnostest`
--

LOCK TABLES `alumnostest` WRITE;
/*!40000 ALTER TABLE `alumnostest` DISABLE KEYS */;
INSERT INTO `alumnostest` VALUES (1,1,1,0,'11',0),(2,1,2,0,'12',0),(3,1,3,0,'13',0);
/*!40000 ALTER TABLE `alumnostest` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clase`
--

DROP TABLE IF EXISTS `clase`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clase` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `grupo_edad` int NOT NULL,
  `modify` int DEFAULT NULL,
  `teacher` int NOT NULL,
  `year` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `nombre_UNIQUE` (`nombre`),
  KEY `idGrupo_idx` (`grupo_edad`),
  KEY `idTeacher_idx` (`teacher`),
  KEY `idYear_idx` (`year`),
  CONSTRAINT `idGrupoClase` FOREIGN KEY (`grupo_edad`) REFERENCES `grupoedad` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `idTeacherClase` FOREIGN KEY (`teacher`) REFERENCES `profesor` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `idYearClase` FOREIGN KEY (`year`) REFERENCES `year` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clase`
--

LOCK TABLES `clase` WRITE;
/*!40000 ALTER TABLE `clase` DISABLE KEYS */;
INSERT INTO `clase` VALUES (1,'Clase 1',3,1,1,1),(4,'Clase 2',3,1,1,1),(5,'Clase 5',3,1,1,1);
/*!40000 ALTER TABLE `clase` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `colegio`
--

DROP TABLE IF EXISTS `colegio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `colegio` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `fecha_inicio` varchar(5) NOT NULL DEFAULT '01-09',
  `localidad` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `email_UNIQUE` (`email`),
  UNIQUE KEY `nombre_UNIQUE` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `colegio`
--

LOCK TABLES `colegio` WRITE;
/*!40000 ALTER TABLE `colegio` DISABLE KEYS */;
INSERT INTO `colegio` VALUES (1,'colePrueba','cole@prueba.es','01-09','Vigo');
/*!40000 ALTER TABLE `colegio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `grupoedad`
--

DROP TABLE IF EXISTS `grupoedad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grupoedad` (
  `id` int NOT NULL AUTO_INCREMENT,
  `grupo_edad` varchar(45) NOT NULL,
  `franja_edad` varchar(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `grupo_edad_UNIQUE` (`grupo_edad`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grupoedad`
--

LOCK TABLES `grupoedad` WRITE;
/*!40000 ALTER TABLE `grupoedad` DISABLE KEYS */;
INSERT INTO `grupoedad` VALUES (1,'Educación Primaria (6-8)','6-8'),(2,'Educación Primaria (9-11)','9-11'),(3,'Educación Secundaria (12-14)','12-14'),(4,'Secundaria - Bachillerato - FP (15-18)','15-18');
/*!40000 ALTER TABLE `grupoedad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `link`
--

DROP TABLE IF EXISTS `link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `link` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `url` text NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `link`
--

LOCK TABLES `link` WRITE;
/*!40000 ALTER TABLE `link` DISABLE KEYS */;
INSERT INTO `link` VALUES (1,'Educación Primaria (6-8)','int_primaria'),(2,'Educación Primaria (9-11)','int_primaria'),(3,'Educación Secundaria (12-14)','int_secundaria'),(19,'Educación emocional','1_edu_emocional'),(20,'Educación en valores','2_edu_valores'),(21,'Grupo y aula','3_grupoyaula'),(22,'Autoconcepto y autoestima','ee_autocyautoe'),(23,'Autoregulación','ee_autoreg'),(24,'Habilidades sociales','ee_habil'),(25,'Empatía','ee_emp'),(26,'Resolución de conflictos','ee_resconf'),(27,'Interculturalidad','ev_intercul'),(28,'Respeto y tolerancia','ev_restol'),(29,'Solidaridad','ev_solid'),(30,'Responsabilidad','ev_resp'),(31,'Cohesión de grupo','ga_cohesion'),(32,'Gestión de aula','ga_gestionaula'),(33,'Trabajo colaborativo y cooperativo','ga_trabajo'),(34,'Secundaria - Bachillerato - FP (15-18)','int_secundaria');
/*!40000 ALTER TABLE `link` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `picto`
--

DROP TABLE IF EXISTS `picto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `picto` (
  `id` int NOT NULL AUTO_INCREMENT,
  `link` text NOT NULL,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `picto`
--

LOCK TABLES `picto` WRITE;
/*!40000 ALTER TABLE `picto` DISABLE KEYS */;
INSERT INTO `picto` VALUES (1,'http://www.arasaac.org/classes/img/thumbnail.php?i=c2l6ZT0zMDAmcnV0YT0uLi8uLi9yZXBvc2l0b3Jpby9vcmlnaW5hbGVzLzMzMDY0LnBuZw==','recreo'),(2,'http://www.arasaac.org/classes/img/thumbnail.php?i=c2l6ZT0zMDAmcnV0YT0uLi8uLi9yZXBvc2l0b3Jpby9vcmlnaW5hbGVzLzM0MTgucG5n','interrogacion'),(3,'http://www.arasaac.org/classes/img/thumbnail.php?i=c2l6ZT0zMDAmcnV0YT0uLi8uLi9yZXBvc2l0b3Jpby9vcmlnaW5hbGVzLzcwNjIucG5n','compaero'),(4,'http://www.arasaac.org/classes/img/thumbnail.php?i=c2l6ZT0zMDAmcnV0YT0uLi8uLi9yZXBvc2l0b3Jpby9vcmlnaW5hbGVzLzIxOTE3LnBuZw==','gustar'),(5,'http://www.arasaac.org/classes/img/thumbnail.php?i=c2l6ZT0zMDAmcnV0YT0uLi8uLi9yZXBvc2l0b3Jpby9vcmlnaW5hbGVzLzIyMDA1LnBuZw==','no gustar'),(6,'http://www.arasaac.org/classes/img/thumbnail.php?i=c2l6ZT0zMDAmcnV0YT0uLi8uLi9yZXBvc2l0b3Jpby9vcmlnaW5hbGVzLzY1MzcucG5n','jugar'),(7,'http://www.arasaac.org/classes/img/thumbnail.php?i=c2l6ZT0zMDAmcnV0YT0uLi8uLi9yZXBvc2l0b3Jpby9vcmlnaW5hbGVzLzk4MTQucG5n','aula'),(8,'http://www.arasaac.org/classes/img/thumbnail.php?i=c2l6ZT0zMDAmcnV0YT0uLi8uLi9yZXBvc2l0b3Jpby9vcmlnaW5hbGVzLzI2MzY4LnBuZw==','rechazar'),(9,'http://www.arasaac.org/classes/img/thumbnail.php?i=c2l6ZT0zMDAmcnV0YT0uLi8uLi9yZXBvc2l0b3Jpby9vcmlnaW5hbGVzLzg2NjIucG5n','pensar'),(10,'http://www.arasaac.org/classes/img/thumbnail.php?i=c2l6ZT0zMDAmcnV0YT0uLi8uLi9yZXBvc2l0b3Jpby9vcmlnaW5hbGVzLzI0NzYzLnBuZw==','por que'),(11,'http://www.arasaac.org/classes/img/thumbnail.php?i=c2l6ZT0zMDAmcnV0YT0uLi8uLi9yZXBvc2l0b3Jpby9vcmlnaW5hbGVzLzU1MjYucG5n','no'),(12,'http://www.arasaac.org/classes/img/thumbnail.php?i=c2l6ZT0zMDAmcnV0YT0uLi8uLi9yZXBvc2l0b3Jpby9vcmlnaW5hbGVzLzExMjg3LnBuZw==','invitar'),(13,'http://www.arasaac.org/classes/img/thumbnail.php?i=c2l6ZT0zMDAmcnV0YT0uLi8uLi9yZXBvc2l0b3Jpby9vcmlnaW5hbGVzLzY2MjUucG5n','tu'),(14,'http://www.arasaac.org/classes/img/thumbnail.php?i=c2l6ZT0zMDAmcnV0YT0uLi8uLi9yZXBvc2l0b3Jpby9vcmlnaW5hbGVzLzY5MDIucG5n','antipatico'),(15,'http://www.arasaac.org/classes/img/thumbnail.php?i=c2l6ZT0zMDAmcnV0YT0uLi8uLi9yZXBvc2l0b3Jpby9vcmlnaW5hbGVzLzEzMzU4LnBuZw==','quienes'),(16,'http://www.arasaac.org/classes/img/thumbnail.php?i=c2l6ZT0zMDAmcnV0YT0uLi8uLi9yZXBvc2l0b3Jpby9vcmlnaW5hbGVzLzExMTYzLnBuZw==','adivina'),(17,'http://www.arasaac.org/classes/img/thumbnail.php?i=c2l6ZT0zMDAmcnV0YT0uLi8uLi9yZXBvc2l0b3Jpby9vcmlnaW5hbGVzLzEwMjc2LnBuZw==','quien'),(18,'http://www.arasaac.org/classes/img/thumbnail.php?i=c2l6ZT0zMDAmcnV0YT0uLi8uLi9yZXBvc2l0b3Jpby9vcmlnaW5hbGVzLzU1MDgucG5n','mas'),(19,'http://www.arasaac.org/classes/img/thumbnail.php?i=c2l6ZT0zMDAmcnV0YT0uLi8uLi9yZXBvc2l0b3Jpby9vcmlnaW5hbGVzLzQ1NzAucG5n','ayudar'),(20,'http://www.arasaac.org/classes/img/thumbnail.php?i=c2l6ZT0zMDAmcnV0YT0uLi8uLi9yZXBvc2l0b3Jpby9vcmlnaW5hbGVzLzI4NDU5LnBuZw==','molestar');
/*!40000 ALTER TABLE `picto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pictospregunta`
--

DROP TABLE IF EXISTS `pictospregunta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pictospregunta` (
  `id` int NOT NULL AUTO_INCREMENT,
  `pregunta` int NOT NULL,
  `order` int NOT NULL DEFAULT '1',
  `picto` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `idPicto_idx` (`picto`),
  KEY `idPregunta_idx` (`pregunta`),
  CONSTRAINT `idPicto` FOREIGN KEY (`picto`) REFERENCES `picto` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `idPreguntaPictos` FOREIGN KEY (`pregunta`) REFERENCES `pregunta` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pictospregunta`
--

LOCK TABLES `pictospregunta` WRITE;
/*!40000 ALTER TABLE `pictospregunta` DISABLE KEYS */;
INSERT INTO `pictospregunta` VALUES (1,4,1,2),(2,4,2,4),(3,4,3,3),(4,4,4,7),(5,33,1,2),(6,33,2,11),(7,33,3,5),(8,33,4,3),(9,33,5,7),(10,57,1,2),(11,57,2,15),(12,57,3,9),(13,57,4,13),(14,57,5,6),(15,84,1,2),(16,84,2,15),(17,84,3,9),(18,84,4,8),(19,84,5,6),(20,112,1,16),(21,112,2,17),(22,112,3,18),(23,112,4,19),(24,112,5,3),(25,131,1,16),(26,131,2,17),(27,131,3,18),(28,131,4,20),(29,131,5,3);
/*!40000 ALTER TABLE `pictospregunta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pregunta`
--

DROP TABLE IF EXISTS `pregunta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pregunta` (
  `id` int NOT NULL AUTO_INCREMENT,
  `pregunta` text NOT NULL,
  `tipo_estructura` int NOT NULL,
  `tipo_pregunta` int NOT NULL,
  `grupo_edad` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `id_idx` (`tipo_pregunta`),
  KEY `id_idx1` (`grupo_edad`),
  KEY `id_idx2` (`tipo_estructura`),
  CONSTRAINT `idGrupoPregunta` FOREIGN KEY (`grupo_edad`) REFERENCES `grupoedad` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `idTipoEstructura` FOREIGN KEY (`tipo_estructura`) REFERENCES `tipoestructura` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `idTipoPregunta` FOREIGN KEY (`tipo_pregunta`) REFERENCES `tipopregunta` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=151 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pregunta`
--

LOCK TABLES `pregunta` WRITE;
/*!40000 ALTER TABLE `pregunta` DISABLE KEYS */;
INSERT INTO `pregunta` VALUES (1,'¿Quiénes son los compañeros o compañeras de tu clase con los que te gustaría seguir el curso que viene?',1,1,1),(2,'¿Con qué personas prefieres jugar en el recreo?',1,1,1),(3,'¿Qué personas de tu clase echarías de menos si no estuviesen?',1,1,1),(4,'¿Con qué compañeros o compañeras te gustaría sentarte en el aula?',1,1,1),(5,'¿Quiénes son tus mejores amigos?',2,1,1),(6,'¿Qué compañeros o compañeras te parecen más simpáticos?',2,1,1),(7,'¿A qué personas de la clase invitarías a tu cumpleaños?',2,1,1),(8,'¿Quiénes son los compañeros o compañeras de tu clase con los que te gustaría seguir el curso que viene?',1,1,2),(9,'¿Con qué personas de la clase prefieres trabajar o elegirías para hacer un trabajo de clase?',1,1,2),(10,'¿Con qué compañeros o compañeras te gustaría sentarte en el aula?',1,1,2),(11,'¿Con qué personas prefieres estar juntos en el recreo?',1,1,2),(12,'¿A qué compañeros o compañeras escogerías para formar un equipo de baloncesto en educación física?',1,1,2),(13,'¿Quiénes son tus mejores amigos y amigas?',2,1,2),(14,'¿A qué personas de la clase invitarías a tu cumpleaños?',2,1,2),(15,'Si pudieras invitar a una fiesta, una excursión, un partido a algunos amigos y amigas de clase, ¿a qué personas de la clase invitarías?',2,1,2),(16,'¿Con qué personas de la clase irías al cine el próximo viernes?',2,1,2),(17,'¿Quiénes son los compañeros o compañeras de tu clase con los que te gustaría seguir el curso que viene?',1,1,3),(18,'¿Con qué personas de la clase prefieres trabajar o elegirías para hacer un trabajo de clase?',1,1,3),(19,'¿A qué compañeros o compañeras elegirías para hacer un trabajo en grupo?',1,1,3),(20,'Si tuvieses que escoger un grupo de compañeros y compañeras para hacer una obra de teatro, ¿a quiénes escogerías?',1,1,3),(21,'¿A qué compañeros o compañeras escogerías para formar un equipo de baloncesto en educación física?',1,1,3),(22,'Si pudieras invitar a una fiesta, una excursión, un partido a algunos amigos y amigas de clase, ¿a quiénes invitarías?',2,1,3),(23,'¿Con quién irías al cine el próximo viernes?',2,1,3),(24,'¿A qué compañeros o compañeras pedirías consejo ante un problema personal?',2,1,3),(25,'¿Con qué personas de la clase prefieres trabajar o elegirías para hacer un trabajo de clase?',1,1,4),(26,'¿Con qué compañeros o compañeras te gustaría quedar para estudiar?',1,1,4),(27,'¿A qué compañeros o compañeras elegirías para hacer un trabajo en grupo?',1,1,4),(28,'¿A qué compañeros o compañeras seguirías en istagram o twitter?',2,1,4),(29,'¿A qué compañeros o compañeras mandarías una solicitud de amistad por facebook?',2,1,4),(30,'¿A qué compañeros o compañeras pedirías consejo ante problemas personales?',2,1,4),(31,'¿Quiénes son los compañeros o compañeras de tu clase con los que NO te gustaría seguir el curso que viene? ¿Por qué?',1,2,1),(32,'¿Con qué personas prefieres NO jugar en el recreo? ¿Por qué?',1,2,1),(33,'¿Con qué compañeros o compañeras NO te gustaría sentarte en el aula? ¿Por qué?',1,2,1),(34,'¿Qué compañeros o compañeras NO te parecen simpáticos? ¿Por qué?',2,2,1),(35,'¿A qué personas de la clase NO invitarías a tu cumpleaños? ¿Por qué?',2,2,1),(36,'¿Con qué compañeros o compañeras prefieres NO encontrarte en un cumpleaños? ¿Por qué?',2,2,1),(37,'¿Quiénes son los compañeros o compañeras de tu clase con los que NO te gustaría seguir el curso que viene? ¿Por qué?',1,2,2),(38,'¿A qué personas NO elegirías para hacer un trabajo de clase? ¿Por qué?',1,2,2),(39,'¿Con qué compañeros o compañeras NO te gustaría sentarte en el aula? ¿Por qué?',1,2,2),(40,'¿Con qué personas prefieres NO estar en el recreo? ¿Por qué?',1,2,2),(41,'¿Qué compañeros o compañeras NO te parecen simpáticos? ¿Por qué?',2,2,2),(42,'¿A qué personas de la clase NO invitarías a tu cumpleaños? ¿Por qué?',2,2,2),(43,'Si pudieras invitar a una fiesta, una excursión, un partido a algunos amigos de clase, ¿a qué personas de la clase NO invitarías? ¿Por qué?',2,2,2),(44,'¿Quiénes son los compañeros o compañeras de tu clase con los que NO te gustaría seguir el curso que viene? ¿Por qué?',1,2,3),(45,'¿A qué personas NO elegirías para hacer un trabajo de clase? ¿Por qué?',1,2,3),(46,'¿A qué compañeros o compañeras NO elegirías para hacer un trabajo en grupo? ¿Por qué?',1,2,3),(47,'Si tuvieses que escoger un grupo de compañeros para hacer una obra de teatro, ¿a quiénes NO escogerías? ¿Por qué?',1,2,3),(48,'¿A qué compañero o compañera NO llamarías para quedar una tarde? ¿Por qué?',2,2,3),(49,'¿A qué compañeros o compañeras NO pedirías consejo ante un problema personal? ¿Por qué?',2,2,3),(50,'¿Con qué personas de la clase NO te gusta trabajar o NO elegirías para hacer un trabajo de clase? ¿Por qué?',1,2,4),(51,'¿Con qué compañeros o compañeras NO te gustaría quedar para estudiar? ¿Por qué?',1,2,4),(52,'¿A qué compañeros o compañeras NO elegirías para hacer un trabajo en grupo? ¿Por qué?',1,2,4),(53,'¿A qué compañeros o compañeras NO seguirías en istagram o twitter? ¿Por qué?',2,2,4),(54,'¿A qué compañeros o compañeras NO mandarías una solicitud de amistad en facebook? ¿Por qué?',2,2,4),(55,'¿A qué compañeros o compañeras NO pedirías consejo ante un problema personal? ¿Por qué?',2,2,4),(56,'Adivina los compañeros o compañeras que habrán puesto que les gustaría seguir el curso que viene contigo.',1,3,1),(57,'¿Qué niños o niñas crees que te escogerían para jugar en el recreo?',1,3,1),(58,'¿Qué personas de tu clase crees que te echarían de menos si cambiases de colegio?',1,3,1),(59,'¿Qué compañeros o compañeras crees que quieren sentarse en el aula contigo?',1,3,1),(60,'¿Quién o quiénes crees que te escogen como mejor amigo o mejor amiga?',2,3,1),(61,'¿A qué personas de la clase crees que les pareces simpático?',2,3,1),(62,'¿Quién o quiénes crees que te van a invitar a su cumpleaños?',2,3,1),(63,'Adivina los compañeros o compañeras que habrán puesto que les gustaría seguir el curso que viene contigo.',1,3,2),(64,'¿Quién o quiénes crees que te han elegido para hacer un trabajo de aula?',1,3,2),(65,'¿Qué compañeros o compañeras crees que quieren sentarse en el aula contigo?',1,3,2),(66,'¿Qué niños o niñas crees que te escogerían para estar juntos en el recreo?',1,3,2),(67,'¿Quién o quiénes crees que te escogen como mejor amigo o mejor amiga?',2,3,2),(68,'¿Quién o quiénes crees que te van a invitar a su cumpleaños?',2,3,2),(69,'¿Qué personas de tu clase crees que te invitarían a una fiesta, una excursión, o un partido?',2,3,2),(70,'¿A qué personas de tu clase crees que les gustaría ir al cine contigo?',2,3,2),(71,'Adivina los compañeros o compañeras que habrán puesto que les gustaría seguir el curso que viene contigo.',1,3,3),(72,'¿Quién o quiénes crees que te han elegido para hacer un trabajo de aula?',1,3,3),(73,'¿Qué compañeros o compañeras crees que te escogerían para hacer una obra de teatro con ellos?',1,3,3),(74,'¿Qué personas de tu clase crees que te invitarían a una fiesta, a una excursión, o a un partido?',2,3,3),(75,'¿A qué personas de tu clase crees que les gustaría ir al cine el próximo viernes contigo?',2,3,3),(76,'¿Qué compañeros o compañeras crees que te pedirían consejo ante un problema personal?',2,3,3),(77,'¿Quién o quiénes crees que te han elegido para hacer un trabajo de aula?',1,3,4),(78,'¿A qué personas de tu clase crees que les gustaría quedar a estudiar contigo?',1,3,4),(79,'¿Quién o quiénes crees que te han elegido para formar un grupo de trabajo?',1,3,4),(80,'¿Qué compañeros o compañeras crees que te seguirían en istagram o twitter?',2,3,4),(81,'¿Qué compañeros o compañeras crees que te mandarían una solicitud de amistad por facebook?',2,3,4),(82,'¿Qué compañeros o compañeras crees que te pedirían consejo ante un problema personal?',2,3,4),(83,'Adivina los compañeros o compañeras que habrán puesto que NO les gustaría seguir el curso que viene contigo. ¿Por qué?',1,4,1),(84,'¿Qué niños o niñas crees que NO te escogerían para jugar en el recreo? ¿Por qué?',1,4,1),(85,'¿Qué personas de tu clase crees que NO te echarían de menos si cambiases de colegio?  ¿Por qué?',1,4,1),(86,'¿Qué compañeros o compañeras crees que NO quieren sentarse en el aula contigo?  ¿Por qué?',1,4,1),(87,'¿Quién o quiénes crees que NO te escogen como amigo o amiga?  ¿Por qué?',2,4,1),(88,'¿A qué personas de la clase crees que NO les pareces simpático o simpática?  ¿Por qué?',2,4,1),(89,'¿Quién o quiénes crees que NO te van a invitar a su cumpleaños?  ¿Por qué?',2,4,1),(90,'Adivina los compañeros o compañeras que habrán puesto que NO les gustaría seguir el curso que viene contigo.  ¿Por qué?',1,4,2),(91,'¿Quién o quiénes crees que NO te han elegido para hacer un trabajo de aula? ¿Por qué?',1,4,2),(92,'¿Qué compañeros o compañeras crees que NO quieren sentarse en el aula contigo?  ¿Por qué?',1,4,2),(93,'¿Qué niños o niñas crees que NO te escogerían para estar juntos en el recreo?  ¿Por qué?',1,4,2),(94,'¿Quién o quiénes crees que NO te escogen como amigo o amiga?  ¿Por qué?',2,4,2),(95,'¿Quién o quiénes crees que NO te van a invitar a su cumpleaños?  ¿Por qué?',2,4,2),(96,'¿Qué personas de tu clase crees que NO te invitarían a una fiesta, una excursión, o un partido?  ¿Por qué?',2,4,2),(97,'¿Qué personas de tu clase crees que NO les gustaría ir al cine contigo?  ¿Por qué?',2,4,2),(98,'Adivina los compañeros o compañeras que habrán puesto que NO les gustaría seguir el curso que viene contigo.  ¿Por qué crees esto?',1,4,3),(99,'¿Quién o quiénes crees que NO te han elegido como compañero o compañera de trabajo?  ¿Por qué?',1,4,3),(100,'¿Qué compañeros o compañeras crees que NO te escogerían para hacer una obra de teatro con ellos?  ¿Por qué?',1,4,3),(101,'¿Qué personas de tu clase crees que NO te invitarían a una fiesta, una excursión, o un partido?  ¿Por qué?',2,4,3),(102,'¿A qué personas de tu clase crees que NO les gustaría ir al cine contigo?  ¿Por qué?',2,4,3),(103,'¿Qué compañeros o compañeras crees que NO te pedirían consejo ante un problema personal?  ¿Por qué?',2,4,3),(104,'¿Quién o quiénes crees que NO te han elegido como compañero o compañera de trabajo?  ¿Por qué?',1,4,4),(105,'¿A qué personas de tu clase crees que NO les gustaría quedar para estudiar contigo?  ¿Por qué?',1,4,4),(106,'¿Quién o quiénes crees que NO te han elegido para formar un grupo de trabajo?  ¿Por qué?',1,4,4),(107,'¿Qué compañeros o compañeras crees que NO te seguirían en instagram o twitter?  ¿Por qué?',2,4,4),(108,'¿Qué compañeros o compañeras crees que NO te mandarían una solicitud de amistad por facebook?  ¿Por qué?',2,4,4),(109,'¿Qué compañeros o compañeras crees que NO te pedirían consejo ante un problema personal?  ¿Por qué?',2,4,4),(110,'Adivina quién es el compañero o compañera más listo o lista de la clase.',1,5,1),(111,'Adivina quién es el niño o la niña al que más quiere la profesora o profesor.',1,5,1),(112,'Adivina quién ayuda más a sus compañeros y compañeras.',1,5,1),(113,'Adivina quién es el compañero o compañera que tiene más amigos y amigas.',2,5,1),(114,'Adivina quién es el compañero o compañera más feliz.',2,5,1),(115,'Dime aquel compañero o compañera que es elegido como líder, como niño o niña más popular de la clase.',1,5,2),(116,'Adivina qué compañero o compañera es más inteligente.',1,5,2),(117,'Adivina quién es el compañero o compañera que tiene capacidad para atender y escuchar a los demás.',2,5,2),(118,'Adivina quién es el compañero o compañera que tiene más amigos y amigas.',2,5,2),(119,'Adivina quién tiene capacidad para resolver conflictos entre los compañeros y compañeras.',2,5,2),(120,'Dime aquel compañero o compañera que es muy agradable, cordial y realmente bueno o buena para trabajar en equipo.',1,5,3),(121,'Adivina quién es el compañero o compañera que tiene capacidad para resolver conflictos entre los compañeros y compañeras.',1,5,3),(122,'Adivina quién es el compañero o compañera que tiene capacidad para atender y escuchar a los demás.',2,5,3),(123,'Adivina quién es el compañero o compañera que tiene más amigos y amigas.',2,5,3),(124,'Dime aquel compañero o compañera que es muy agradable, cordial y realmente bueno o buena para trabajar en equipo. Coopera, ayuda, comparte y respeta los turnos.',1,5,4),(125,'Adivina quién es el compañero o compañera que tiene capacidad para resolver conflictos entre los compañeros y compañeras.',1,5,4),(126,'Dime aquel compañero o compañera que crees que tiene más seguidores en twitter o instagram.',2,5,4),(127,'Dime aquel compañero o compañera que crees que tiene más amigos en facebook.',2,5,4),(128,'Adivina quién es el compañero o compañera que sabe comunicarse mejor y que le entienden y escuchen con más facilidad.',2,5,4),(129,'Adivina quién es el o la que menos sabe en clase.',1,6,1),(130,'Adivina quién es el niño o la niña al que menos quiere la profesora o el profesor.',1,6,1),(131,'Adivina quién molesta más a sus compañeros y compañeras.',1,6,1),(132,'Adivina quién es el compañero o compañera que tiene menos amigos y amigas.',2,6,1),(133,'Adivina quién es el compañero o compañera más triste.',2,6,1),(134,'Dime aquel compañero o compañera que molesta más a los demás.',1,6,2),(135,'Dime aquel compañero o compañera que no comparte ni respeta a los demás.',1,6,2),(137,'Dime aquel compañero o compañera que se mete con los demás.',2,6,2),(138,'Dime aquel compañero o compañera que cuando llega a los grupos molesta, no comparte ni respeta, e intenta que todos hagan las cosas a su manera.',1,6,3),(139,'Dime aquel compañero o compañera que siempre pide ayuda para hacer cualquier cosa, incluso antes de haberlo intentado.',1,6,3),(140,'Dime aquel compañero o compañera que es muy tímido o tímida con los demás, siempre juega o trabaja solo o sola y es más difícil llegar a conocer.',2,6,3),(141,'Dime aquel compañero o compañera que empieza las peleas, se mete con los demás, les empuja o les pega.',2,6,3),(142,'Dime aquel compañero o compañera que cuando llega a los grupos molesta, no comparte ni respeta, e intenta que todos hagan las cosas a su manera.',1,6,4),(143,'Dime aquel compañero o compañera que siempre pide ayuda para hacer cualquiera cosa, incluso antes de haberlo intentado.',1,6,4),(144,'Dime aquel compañero o compañera que crees que tiene menos seguidores en twitter o instagram.',2,6,4),(145,'Dime aquel compañero o compañera que crees que tiene menos amigos en facebook.',2,6,4),(146,'Adivina quién es el compañero o compañera que tiene problemas para comunicarse.',2,6,4),(147,'Dime quién es el compañero o compañera que trolea en las redes sociales para reírse de los demás.',2,6,4),(148,'Si pudieses invitar a una fiesta, una excursión, un partido a algunos amigos o amigas de clase, ¿a quién o quiénes NO invitarías? ¿Por qué?',2,4,3),(150,'Adivina quién es más maleducado o maleducada con los compañeros y compañeras.',2,6,2);
/*!40000 ALTER TABLE `pregunta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `preguntastest`
--

DROP TABLE IF EXISTS `preguntastest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `preguntastest` (
  `id` int NOT NULL AUTO_INCREMENT,
  `test` int NOT NULL,
  `pregunta` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `id_idx` (`pregunta`),
  KEY `idTest_idx` (`test`),
  CONSTRAINT `idPregunta` FOREIGN KEY (`pregunta`) REFERENCES `pregunta` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `idTest` FOREIGN KEY (`test`) REFERENCES `test` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `preguntastest`
--

LOCK TABLES `preguntastest` WRITE;
/*!40000 ALTER TABLE `preguntastest` DISABLE KEYS */;
INSERT INTO `preguntastest` VALUES (1,1,17),(2,1,44),(3,1,71),(4,1,98),(5,1,120),(6,1,138),(13,2,24),(14,2,49),(15,2,75),(16,2,103),(17,2,122),(18,2,141),(31,5,24),(32,5,49),(33,5,75),(34,5,103),(35,5,122),(36,5,141);
/*!40000 ALTER TABLE `preguntastest` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `profesor`
--

DROP TABLE IF EXISTS `profesor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `profesor` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user` int NOT NULL,
  `evaluacion` int NOT NULL DEFAULT '0',
  `email` varchar(255) NOT NULL,
  `username` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `email_UNIQUE` (`email`),
  UNIQUE KEY `username_UNIQUE` (`username`),
  KEY `idUser_idx` (`user`),
  CONSTRAINT `idUserTeacher` FOREIGN KEY (`user`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `profesor`
--

LOCK TABLES `profesor` WRITE;
/*!40000 ALTER TABLE `profesor` DISABLE KEYS */;
INSERT INTO `profesor` VALUES (1,1,1,'admin@prueba.es','admin');
/*!40000 ALTER TABLE `profesor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `respuesta`
--

DROP TABLE IF EXISTS `respuesta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `respuesta` (
  `id` int NOT NULL AUTO_INCREMENT,
  `alumno` int NOT NULL,
  `pregunta` int NOT NULL,
  `respuesta` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `idAlumno_idx` (`alumno`),
  KEY `idPregunta_idx` (`pregunta`),
  CONSTRAINT `idAlumnoRespuesta` FOREIGN KEY (`alumno`) REFERENCES `alumnostest` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `idPreguntaRespuesta` FOREIGN KEY (`pregunta`) REFERENCES `pregunta` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `respuesta`
--

LOCK TABLES `respuesta` WRITE;
/*!40000 ALTER TABLE `respuesta` DISABLE KEYS */;
/*!40000 ALTER TABLE `respuesta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rol`
--

DROP TABLE IF EXISTS `rol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rol` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `admin` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre_UNIQUE` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rol`
--

LOCK TABLES `rol` WRITE;
/*!40000 ALTER TABLE `rol` DISABLE KEYS */;
INSERT INTO `rol` VALUES (1,'alumno',0),(2,'profesor',0),(3,'admin',1);
/*!40000 ALTER TABLE `rol` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `test`
--

DROP TABLE IF EXISTS `test`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `test` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `clase` int NOT NULL,
  `estructura` int NOT NULL,
  `date_created` datetime NOT NULL,
  `uploaded` int DEFAULT NULL,
  `downloaded` int DEFAULT NULL,
  `profesor` int NOT NULL,
  `closed` int DEFAULT NULL,
  `year` int NOT NULL,
  `first` int DEFAULT NULL,
  `followUp` int DEFAULT NULL,
  `final` int DEFAULT NULL,
  `survey1` int DEFAULT NULL,
  `survey2` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `nombre_UNIQUE` (`nombre`),
  KEY `idClase_idx` (`clase`),
  KEY `idEstructura_idx` (`estructura`),
  KEY `idTeacher_idx` (`profesor`),
  KEY `idYear_idx` (`year`),
  KEY `idFirst_idx` (`first`),
  CONSTRAINT `idClaseTest` FOREIGN KEY (`clase`) REFERENCES `clase` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `idEstructuraTest` FOREIGN KEY (`estructura`) REFERENCES `tipoestructura` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `idFirstTest` FOREIGN KEY (`first`) REFERENCES `test` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `idTeacherTest` FOREIGN KEY (`profesor`) REFERENCES `profesor` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `idYearTest` FOREIGN KEY (`year`) REFERENCES `year` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test`
--

LOCK TABLES `test` WRITE;
/*!40000 ALTER TABLE `test` DISABLE KEYS */;
INSERT INTO `test` VALUES (1,'Test 1',1,1,'2022-08-09 04:36:44',1,0,1,0,1,NULL,0,0,0,0),(2,'Test 2',1,2,'2022-08-09 08:46:22',1,0,1,1,1,NULL,1,1,0,0),(5,'Test 2 - seguimiento',1,2,'2022-08-13 00:19:25',0,0,1,0,1,2,1,0,0,0);
/*!40000 ALTER TABLE `test` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipoestructura`
--

DROP TABLE IF EXISTS `tipoestructura`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tipoestructura` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tipo` varchar(45) NOT NULL,
  `descripcion` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `tipo_UNIQUE` (`tipo`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipoestructura`
--

LOCK TABLES `tipoestructura` WRITE;
/*!40000 ALTER TABLE `tipoestructura` DISABLE KEYS */;
INSERT INTO `tipoestructura` VALUES (1,'F','Formal'),(2,'I','Informal');
/*!40000 ALTER TABLE `tipoestructura` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipopregunta`
--

DROP TABLE IF EXISTS `tipopregunta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tipopregunta` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tipo` varchar(3) NOT NULL,
  `descripcion` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `tipo_UNIQUE` (`tipo`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipopregunta`
--

LOCK TABLES `tipopregunta` WRITE;
/*!40000 ALTER TABLE `tipopregunta` DISABLE KEYS */;
INSERT INTO `tipopregunta` VALUES (1,'PGP','Percepción del grupo positiva'),(2,'PGN','Percepción del grupo negativa'),(3,'PPP','Percepción propia positiva'),(4,'PPN','Percepción propia negativa'),(5,'AAP','Asociación de atributos positiva'),(6,'AAN','Asociación de atributos negativa');
/*!40000 ALTER TABLE `tipopregunta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `apellidos` varchar(255) NOT NULL,
  `date_joined` datetime NOT NULL,
  `DNI` varchar(9) DEFAULT NULL,
  `colegio` int NOT NULL,
  `rol` int NOT NULL,
  `validado` int DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `activo` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `DNI_UNIQUE` (`DNI`),
  KEY `idRol_idx` (`rol`),
  KEY `idColegio_idx` (`colegio`),
  CONSTRAINT `idColegioUser` FOREIGN KEY (`colegio`) REFERENCES `colegio` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `idRol` FOREIGN KEY (`rol`) REFERENCES `rol` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'Admin','Prueba','2022-08-09 01:54:11','12345678W',1,3,0,'$2b$12$8dbxXD..yP1QVzXg7H0r/uO06fe6J6XGhA3tSPxY2hd4ZkYgEBkg2',1),(2,'al1','ap1 ap1','2022-08-09 01:56:09','12345678Q',1,1,NULL,NULL,1),(3,'al2','ap2 ap2','2022-08-09 02:00:04','78456123E',1,1,NULL,NULL,1),(4,'al3','ap3 ap3','2022-08-09 02:01:06','79456321Y',1,1,NULL,NULL,1),(5,'al3','ap3 ap3','2022-08-09 02:01:48','13456289T',1,1,NULL,NULL,1),(6,'al4','ap4 ap4','2022-08-09 02:03:13','45123695R',1,1,NULL,NULL,1),(7,'al5 ','ap5 ap5','2022-08-09 09:50:38','78456123K',1,1,NULL,NULL,1),(14,'al6','ap6','2022-08-11 01:24:17',NULL,1,1,NULL,NULL,1),(16,'al7','ap7','2022-08-11 01:33:23',NULL,1,1,NULL,NULL,1),(17,'al8','ap8','2022-08-11 01:33:56',NULL,1,1,NULL,NULL,0);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `year`
--

DROP TABLE IF EXISTS `year`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `year` (
  `id` int NOT NULL AUTO_INCREMENT,
  `school_year` varchar(10) NOT NULL,
  `current` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `school_year_UNIQUE` (`school_year`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `year`
--

LOCK TABLES `year` WRITE;
/*!40000 ALTER TABLE `year` DISABLE KEYS */;
INSERT INTO `year` VALUES (1,'2021/2022',1);
/*!40000 ALTER TABLE `year` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-08-13 20:29:42
