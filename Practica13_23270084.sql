#Practica 13: 
#Autor: John Lenin Hernández López
# source C:\Users\xbox3\Documents\Quinto semestre\Base de datos 3\SQL\Practica13_23270084.sql

DROP DATABASE IF EXISTS dbtiendaletty;
CREATE DATABASE dbtiendaletty;
USE dbtiendaletty;

CREATE TABLE articulos (
  codigoBarras CHAR(13) NOT NULL PRIMARY KEY,
  nombreArt VARCHAR(80) NULL,
  marca VARCHAR(50) NULL,
  cantidadAlmacen INT NULL,
  precioUnit DECIMAL(10,2) NULL,
  caducidad DATE NULL
);

CREATE TABLE cliente (
  numTelC CHAR(10) NOT NULL PRIMARY KEY,
  nombreC VARCHAR(50) NULL,
  correo VARCHAR(50) NULL
);

CREATE TABLE vendedor (
  numTelV CHAR(10) NOT NULL PRIMARY KEY,
  nombreV VARCHAR(200) NULL,
  horaEntrada TIME NULL,
  horaSalida TIME NULL
);

CREATE TABLE proveedores (
  claveProv CHAR(12) NOT NULL PRIMARY KEY,
  numTelProv CHAR(10) NULL,
  empresa VARCHAR(30) NULL
);

CREATE TABLE loginVendedor(
	numTelV CHAR(10),
	clave VARCHAR(100),
	FOREIGN KEY (numTelV) REFERENCES vendedor(numTelV)
);

CREATE TABLE ventas (
  idVenta INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  numTelC CHAR(10) NULL,
  numTelV CHAR(10) NULL,
  totalpago DECIMAL(10,2) NULL,
  codigoBarras CHAR (13)  NULL,
  FOREIGN KEY (numTelC) REFERENCES cliente(numTelC),
  FOREIGN KEY (numTelV) REFERENCES vendedor(numTelV),
  FOREIGN KEY (codigoBarras) REFERENCES articulos(codigoBarras)
);

CREATE TABLE detalles (
  claveProv CHAR(12) NOT NULL,
  codigoBarras CHAR(13) NULL,
  costos DECIMAL(10,2) NULL,
  cantidadEntregada INT NULL,
  FOREIGN KEY (claveProv) REFERENCES proveedores(claveProv),
  FOREIGN KEY (codigoBarras) REFERENCES articulos(codigoBarras)
);