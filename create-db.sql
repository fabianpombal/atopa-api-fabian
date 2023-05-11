-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema atopa
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `atopa` ;

-- -----------------------------------------------------
-- Schema atopa
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `atopa` DEFAULT CHARACTER SET utf8 ;
USE `atopa` ;

-- -----------------------------------------------------
-- Table `atopa`.`TipoPregunta`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `atopa`.`TipoPregunta` ;

CREATE TABLE IF NOT EXISTS `atopa`.`TipoPregunta` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `tipo` VARCHAR(3) NOT NULL,
  `descripcion` TEXT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `tipo_UNIQUE` (`tipo` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `atopa`.`TipoEstructura`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `atopa`.`TipoEstructura` ;

CREATE TABLE IF NOT EXISTS `atopa`.`TipoEstructura` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `tipo` VARCHAR(45) NOT NULL,
  `descripcion` TEXT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `tipo_UNIQUE` (`tipo` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `atopa`.`GrupoEdad`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `atopa`.`GrupoEdad` ;

CREATE TABLE IF NOT EXISTS `atopa`.`GrupoEdad` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `grupo_edad` VARCHAR(45) NOT NULL,
  `franja_edad` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `grupo_edad_UNIQUE` (`grupo_edad` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `atopa`.`Pregunta`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `atopa`.`Pregunta` ;

CREATE TABLE IF NOT EXISTS `atopa`.`Pregunta` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `pregunta` TEXT NOT NULL,
  `tipo_estructura` INT NOT NULL,
  `tipo_pregunta` INT NOT NULL,
  `grupo_edad` INT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  INDEX `id_idx` (`tipo_pregunta` ASC),
  INDEX `id_idx1` (`grupo_edad` ASC),
  INDEX `id_idx2` (`tipo_estructura` ASC),
  CONSTRAINT `idTipoPregunta`
    FOREIGN KEY (`tipo_pregunta`)
    REFERENCES `atopa`.`TipoPregunta` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `idTipoEstructura`
    FOREIGN KEY (`tipo_estructura`)
    REFERENCES `atopa`.`TipoEstructura` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `idGrupoPregunta`
    FOREIGN KEY (`grupo_edad`)
    REFERENCES `atopa`.`GrupoEdad` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `atopa`.`Rol`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `atopa`.`Rol` ;

CREATE TABLE IF NOT EXISTS `atopa`.`Rol` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(255) NOT NULL,
  `admin` INT NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `nombre_UNIQUE` (`nombre` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `atopa`.`Colegio`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `atopa`.`Colegio` ;

CREATE TABLE IF NOT EXISTS `atopa`.`Colegio` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `fecha_inicio` VARCHAR(5) NOT NULL DEFAULT '01-09',
  `localidad` VARCHAR(255) NOT NULL,
  `hash` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `email_UNIQUE` (`email` ASC),
  UNIQUE INDEX `nombre_UNIQUE` (`nombre` ASC),
  UNIQUE INDEX `hash_UNIQUE` (`hash` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `atopa`.`User`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `atopa`.`User` ;

CREATE TABLE IF NOT EXISTS `atopa`.`User` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(255) NOT NULL,
  `apellidos` VARCHAR(255) NOT NULL,
  `date_joined` DATETIME NOT NULL,
  `DNI` VARCHAR(9) NULL,
  `colegio` INT NOT NULL,
  `rol` INT NOT NULL,
  `validado` INT NULL,
  `password` VARCHAR(255) NULL,
  `activo` INT NOT NULL DEFAULT 1,
  `fecha_nacimiento` VARCHAR(10) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `DNI_UNIQUE` (`DNI` ASC, `colegio` ASC),
  INDEX `idRol_idx` (`rol` ASC),
  INDEX `idColegio_idx` (`colegio` ASC),
  UNIQUE INDEX `student_UNIQUE` (`nombre` ASC, `apellidos` ASC, `fecha_nacimiento` ASC, `rol` ASC),
  CONSTRAINT `idRol`
    FOREIGN KEY (`rol`)
    REFERENCES `atopa`.`Rol` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `idColegioUser`
    FOREIGN KEY (`colegio`)
    REFERENCES `atopa`.`Colegio` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `atopa`.`Profesor`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `atopa`.`Profesor` ;

CREATE TABLE IF NOT EXISTS `atopa`.`Profesor` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user` INT NOT NULL,
  `evaluacion` INT NOT NULL DEFAULT 0,
  `email` VARCHAR(255) NOT NULL,
  `username` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `email_UNIQUE` (`email` ASC),
  INDEX `idUser_idx` (`user` ASC),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC),
  CONSTRAINT `idUserTeacher`
    FOREIGN KEY (`user`)
    REFERENCES `atopa`.`User` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `atopa`.`Year`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `atopa`.`Year` ;

CREATE TABLE IF NOT EXISTS `atopa`.`Year` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `school_year` VARCHAR(10) NOT NULL,
  `current` INT NOT NULL,
  `colegio` INT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  INDEX `fk_colegio_idx` (`colegio` ASC),
  CONSTRAINT `fk_colegio`
    FOREIGN KEY (`colegio`)
    REFERENCES `atopa`.`Colegio` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `atopa`.`Clase`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `atopa`.`Clase` ;

CREATE TABLE IF NOT EXISTS `atopa`.`Clase` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(255) NOT NULL,
  `grupo_edad` INT NOT NULL,
  `modify` INT NULL,
  `teacher` INT NOT NULL,
  `year` INT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  INDEX `idGrupo_idx` (`grupo_edad` ASC),
  INDEX `idTeacher_idx` (`teacher` ASC),
  INDEX `idYear_idx` (`year` ASC),
  UNIQUE INDEX `nombre_unique` (`nombre` ASC, `teacher` ASC, `year` ASC),
  CONSTRAINT `idGrupoClase`
    FOREIGN KEY (`grupo_edad`)
    REFERENCES `atopa`.`GrupoEdad` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `idTeacherClase`
    FOREIGN KEY (`teacher`)
    REFERENCES `atopa`.`Profesor` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `idYearClase`
    FOREIGN KEY (`year`)
    REFERENCES `atopa`.`Year` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `atopa`.`Test`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `atopa`.`Test` ;

CREATE TABLE IF NOT EXISTS `atopa`.`Test` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(255) NOT NULL,
  `clase` INT NOT NULL,
  `estructura` INT NOT NULL,
  `date_created` DATETIME NOT NULL,
  `uploaded` INT NULL,
  `downloaded` INT NULL,
  `profesor` INT NOT NULL,
  `closed` INT NULL,
  `year` INT NOT NULL,
  `first` INT NULL,
  `followUp` INT NULL,
  `final` INT NULL,
  `survey1` INT NULL,
  `survey2` INT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `nombre_UNIQUE` (`nombre` ASC),
  INDEX `idClase_idx` (`clase` ASC),
  INDEX `idEstructura_idx` (`estructura` ASC),
  INDEX `idTeacher_idx` (`profesor` ASC),
  INDEX `idYear_idx` (`year` ASC),
  INDEX `idFirst_idx` (`first` ASC),
  CONSTRAINT `idClaseTest`
    FOREIGN KEY (`clase`)
    REFERENCES `atopa`.`Clase` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `idEstructuraTest`
    FOREIGN KEY (`estructura`)
    REFERENCES `atopa`.`TipoEstructura` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `idTeacherTest`
    FOREIGN KEY (`profesor`)
    REFERENCES `atopa`.`Profesor` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `idYearTest`
    FOREIGN KEY (`year`)
    REFERENCES `atopa`.`Year` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `idFirstTest`
    FOREIGN KEY (`first`)
    REFERENCES `atopa`.`Test` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `atopa`.`PreguntasTest`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `atopa`.`PreguntasTest` ;

CREATE TABLE IF NOT EXISTS `atopa`.`PreguntasTest` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `test` INT NOT NULL,
  `pregunta` INT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  INDEX `id_idx` (`pregunta` ASC),
  INDEX `idTest_idx` (`test` ASC),
  CONSTRAINT `idPregunta`
    FOREIGN KEY (`pregunta`)
    REFERENCES `atopa`.`Pregunta` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `idTest`
    FOREIGN KEY (`test`)
    REFERENCES `atopa`.`Test` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `atopa`.`Picto`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `atopa`.`Picto` ;

CREATE TABLE IF NOT EXISTS `atopa`.`Picto` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `link` TEXT NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `name_UNIQUE` (`name` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `atopa`.`PictosPregunta`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `atopa`.`PictosPregunta` ;

CREATE TABLE IF NOT EXISTS `atopa`.`PictosPregunta` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `pregunta` INT NOT NULL,
  `order` INT NOT NULL DEFAULT 1,
  `picto` INT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  INDEX `idPicto_idx` (`picto` ASC),
  INDEX `idPregunta_idx` (`pregunta` ASC),
  CONSTRAINT `idPreguntaPictos`
    FOREIGN KEY (`pregunta`)
    REFERENCES `atopa`.`Pregunta` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `idPicto`
    FOREIGN KEY (`picto`)
    REFERENCES `atopa`.`Picto` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `atopa`.`Alumno`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `atopa`.`Alumno` ;

CREATE TABLE IF NOT EXISTS `atopa`.`Alumno` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `sexo` VARCHAR(1) NOT NULL,
  `user` INT NOT NULL,
  `activo` INT NOT NULL DEFAULT 1,
  `alias` VARCHAR(45) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  INDEX `idUser_idx` (`user` ASC),
  CONSTRAINT `idUserAlumno`
    FOREIGN KEY (`user`)
    REFERENCES `atopa`.`User` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `atopa`.`AlumnosTest`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `atopa`.`AlumnosTest` ;

CREATE TABLE IF NOT EXISTS `atopa`.`AlumnosTest` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `test` INT NOT NULL,
  `alumno` INT NOT NULL,
  `answer` INT NULL,
  `code` VARCHAR(255) NULL,
  `activo` INT NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  INDEX `idTest_idx` (`test` ASC),
  INDEX `idAlumno_idx` (`alumno` ASC),
  UNIQUE INDEX `code_UNIQUE` (`code` ASC),
  CONSTRAINT `idTestAlumno`
    FOREIGN KEY (`test`)
    REFERENCES `atopa`.`Test` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `idAlumnoTest`
    FOREIGN KEY (`alumno`)
    REFERENCES `atopa`.`Alumno` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `atopa`.`Respuesta`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `atopa`.`Respuesta` ;

CREATE TABLE IF NOT EXISTS `atopa`.`Respuesta` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `alumno` INT NOT NULL,
  `pregunta` INT NOT NULL,
  `respuesta` TEXT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  INDEX `idAlumno_idx` (`alumno` ASC),
  INDEX `idPregunta_idx` (`pregunta` ASC),
  CONSTRAINT `idAlumnoRespuesta`
    FOREIGN KEY (`alumno`)
    REFERENCES `atopa`.`AlumnosTest` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `idPreguntaRespuesta`
    FOREIGN KEY (`pregunta`)
    REFERENCES `atopa`.`Pregunta` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `atopa`.`Link`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `atopa`.`Link` ;

CREATE TABLE IF NOT EXISTS `atopa`.`Link` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `url` TEXT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `name_UNIQUE` (`name` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `atopa`.`Preferencias`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `atopa`.`Preferencias` ;

CREATE TABLE IF NOT EXISTS `atopa`.`Preferencias` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user` INT NOT NULL,
  `sp` INT NOT NULL,
  `spv` INT NOT NULL,
  `np` INT NOT NULL,
  `data` INT NOT NULL,
  `ep` INT NOT NULL,
  `rp` INT NOT NULL,
  `ic` INT NOT NULL,
  `iap` INT NOT NULL,
  `ip` INT NOT NULL,
  `ipv` INT NOT NULL,
  `imp` INT NOT NULL,
  `ipp` INT NOT NULL,
  `pp` INT NOT NULL,
  `pap` INT NOT NULL,
  `os` INT NOT NULL,
  `oip` INT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `user_UNIQUE` (`user` ASC),
  CONSTRAINT `idUser`
    FOREIGN KEY (`user`)
    REFERENCES `atopa`.`User` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `atopa`.`AlumnosClase`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `atopa`.`AlumnosClase` ;

CREATE TABLE IF NOT EXISTS `atopa`.`AlumnosClase` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `alumno` INT NOT NULL,
  `clase` INT NOT NULL,
  `alias` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  INDEX `alumno_fk_idx` (`alumno` ASC),
  INDEX `clase_fk_idx` (`clase` ASC),
  UNIQUE INDEX `alias_UNIQUE` (`alias` ASC, `clase` ASC),
  UNIQUE INDEX `alumno_UNIQUE` (`alumno` ASC, `clase` ASC),
  CONSTRAINT `alumno_fk`
    FOREIGN KEY (`alumno`)
    REFERENCES `atopa`.`Alumno` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `clase_fk`
    FOREIGN KEY (`clase`)
    REFERENCES `atopa`.`Clase` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `atopa`.`Encuesta`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `atopa`.`Encuesta` ;

CREATE TABLE IF NOT EXISTS `atopa`.`Encuesta` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `test` INT NULL,
  `user` INT NOT NULL,
  `respuesta` TEXT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  INDEX `user_fk_idx` (`user` ASC),
  INDEX `test_fk_idx` (`test` ASC),
  CONSTRAINT `user_fk`
    FOREIGN KEY (`user`)
    REFERENCES `atopa`.`User` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `test_fk`
    FOREIGN KEY (`test`)
    REFERENCES `atopa`.`Test` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
