drop database if EXISTS testeo;
create database testeo;
use testeo;

CREATE TABLE IF NOT EXISTS `TableA` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `value` INT NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `TableB` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `description` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE = InnoDB;

INSERT INTO `TableA` (`name`, `value`) VALUES
  ('John', 10),
  ('Jane', 15),
  ('Bob', 20),
  ('Alice', 25);

INSERT INTO `TableB` (`name`, `description`) VALUES
  ('John', 'Manager'),
  ('Jane', 'Supervisor'),
  ('Bob', 'Employee'),
  ('Dave', 'Intern'),
  ('Alice', 'Director');


SELECT *
FROM TableA
where TableA.name = 'John'
INNER JOIN TableB ON TableA.id = TableB.id;
