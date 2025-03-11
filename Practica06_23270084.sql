# Practica06-Rubricas
# Nombre: John Lenin Hernandez Lopez
# Fecha: 25-febr-2025
# source C:\Users\xbox3\Documents\Quinto semestre\Base de datos 3\SQL\Practica06_23270084.sql



DROP DATABASE if exists dbtaller;
CREATE DATABASE dbtaller;
USE dbtaller;


CREATE TABLE Rol (
    id_rol INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE Permiso (
    id_permiso INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE Rol_Permiso (
    id_rol INT,
    id_permiso INT,
    objeto VARCHAR(50) NOT NULL,  
    PRIMARY KEY (id_rol, id_permiso, objeto),
    FOREIGN KEY (id_rol) REFERENCES Rol(id_rol) ON DELETE CASCADE,
    FOREIGN KEY (id_permiso) REFERENCES Permiso(id_permiso) ON DELETE CASCADE
);

CREATE TABLE Usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    id_rol INT,
    FOREIGN KEY (id_rol) REFERENCES Rol(id_rol) ON DELETE SET NULL
);

CREATE TABLE lineainv (
    clavein CHAR(10) PRIMARY KEY, 
    nombre VARCHAR(250)
);

CREATE TABLE profesor (
    idprofesor INT AUTO_INCREMENT PRIMARY KEY, 
    nombreProf VARCHAR(200)
);

CREATE TABLE tipoProyecto (
    tipo CHAR(3), 
    nombre VARCHAR(550),
	PRIMARY KEY (tipo, nombre)
);

CREATE TABLE proyecto (
    clave CHAR(10) PRIMARY KEY, 
    nombre_tipo VARCHAR(250), 
    clavein CHAR(10), 
    tipo CHAR(10),
    CONSTRAINT corresponde FOREIGN KEY (clavein) REFERENCES lineainv(clavein),
    CONSTRAINT asignado FOREIGN KEY (tipo, nombre_tipo) REFERENCES tipoproyecto(tipo, nombre)
);

CREATE TABLE alumno (
    nocontrol CHAR(10) PRIMARY KEY, 
    nombre VARCHAR(150), 
    clave CHAR(10),
    CONSTRAINT elige FOREIGN KEY (clave) REFERENCES proyecto(clave)
);

CREATE TABLE profesorproy (
    idprofesor INT, 
    clave CHAR(10), 
    calificacion FLOAT, 
    rol VARCHAR(45),
    CONSTRAINT asesora FOREIGN KEY (idprofesor) REFERENCES profesor(idprofesor),
    CONSTRAINT asigna FOREIGN KEY (clave) REFERENCES proyecto(clave)
);

CREATE TABLE datos (
    clave CHAR(8), 
    proyecto VARCHAR(150), 
    linea CHAR(10), 
    tipo CHAR(5),  
    nocontrol CHAR(10), 
    nombre_alumno VARCHAR(150), 
    nombreProf VARCHAR(150), 
    revisor1 VARCHAR(150),  
    revisor2 VARCHAR(150)
);

CREATE TABLE area (
    Id_area INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
    nombre_area VARCHAR(400) NOT NULL
);

CREATE TABLE indicador (
    Id_indicador INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
    nombre_indicador VARCHAR(500) NOT NULL,
    descripcion VARCHAR(700) NOT NULL
);

CREATE TABLE rubrica (
    Id_area INT, 
    Id_indicador INT, 
    PRIMARY KEY (Id_area, Id_indicador),
	ponderacion FLOAT,
    CONSTRAINT esta FOREIGN KEY (Id_area) REFERENCES area(Id_area) ON DELETE CASCADE,
    CONSTRAINT aplica FOREIGN KEY (Id_indicador) REFERENCES indicador(Id_indicador) ON DELETE CASCADE
);

INSERT INTO area (nombre_area) VALUES 
("Base de datos"),
("Ingeniería de software"),
("Redes de computadoras"),
("Tesis"),
("Arquitectura de computadoras");

INSERT INTO indicador (nombre_indicador, descripcion) VALUES
("Descripción de procesos", 
 "Explicación del proceso general actual.\nSe refiere a la descripción detallada del proceso general actual, estableciendo, entre otros, las actividades que se realizan, las entidades que participan en ese proceso general, indicando el rol que juegan, las relaciones y formas de comunicación que existen entre esas entidades, los insumos, así como la información resultante."),
("Especificación de los requisitos de software", 
 "Requisitos funcionales.\nRequisitos Funcionales: de información, de comportamiento, reglas del negocio.\nCada requisito funcional contiene un código identificador y una descripción clara, completa y sin ambigüedades."),
("Definición del problema", 
 "Se identifican los problemas de conectividad de red a resolver, ya sean de cableado o de servicios de red, por ejemplo: (DNS, WiFi, direcciones IP duplicadas)."),
("Requisitos de la red", 
 "Especificación de las características actuales de la red, por ejemplo: número de nodos, número de usuarios, cantidad de dispositivos.");

INSERT INTO rubrica VALUES
(3,3,10),
(3,4,10),
(2,1,9),
(2,2,28);

INSERT INTO lineainv VALUES
("RCISP", "Robotica, Control Inteligente y Sistemas de Percepcion"),
("DSIR", "Desarrollo de Software e Infraestrctura de Red"),
("TDWM", "Tecnologias de Desarrollo Web y Movil");

INSERT INTO tipoproyecto VALUES
("DT", "Estimacion de peso de ganado bovino mediante aprendizaje profundo"),
("DT", "Sistema de prevencion de alertas usando imagenes satelitales para desastres naturales"),
("DT", "Sistema de monitoreo para el desarrollo y cultivo de Pleurotus Ostreatus");


INSERT INTO profesor (nombreprof) VALUES
("Nestor Antonio Morales Navarro"),
("Madain Perez Patricio"),
("Maria Candelaria Gutierrez Gomez");