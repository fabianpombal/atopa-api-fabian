INSERT INTO `atopa`.`Colegio` (`nombre`, `email`, `localidad`) 
VALUES ('Colegio Nacional de Buenos Aires', 'cnba@gmail.com', 'Buenos Aires');
INSERT INTO `atopa`.`Colegio` (`nombre`, `email`, `localidad`) 
VALUES ('Colegio Santo Tomás', 'santo.tomas@hotmail.com', 'Córdoba');
INSERT INTO `atopa`.`Colegio` (`nombre`, `email`, `fecha_inicio`, `localidad`) 
VALUES ('Colegio San Agustín', 'sanagustin@gmail.com', '15-03', 'Rosario');

INSERT INTO `atopa`.`User` (`nombre`, `apellidos`, `date_joined`, `DNI`, `colegio`, `rol`, `validado`, `password`, `fecha_nacimiento`)
VALUES 
('Juan', 'Pérez García', '2021-05-01 10:30:00', '12345678A', 1, 2, 1, 'mypassword', '1990-01-01'),
('María', 'González López', '2021-05-02 12:00:00', '87654321B', 1, 2, 1, 'mariapass', '1995-02-28'),
('Pedro', 'Fernández Pérez', '2021-05-03 14:30:00', '11111111C', 3, 1, 1, NULL, '2000-10-10');

INSERT INTO `atopa`.`Profesor` (`user`, `evaluacion`, `email`, `username`)
VALUES (7, 5, 'juan@gmail.com', 'JuanPerez'),
       (8, 3, 'maria@yahoo.com', 'MariaGonzalez'),
       (9, 4, 'pedro@hotmail.com', 'PedroFernandez');
