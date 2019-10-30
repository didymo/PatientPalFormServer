/*
Author: Brian Valenzi
Email: bv457@uowmail.edu.au
*/
CREATE DATABASE formserver;

USE formserver;

CREATE TABLE Uncompleted_Survey(
	id int NOT NULL,
	form_name VARCHAR(50) NOT NULL,
	version VARCHAR(10) NOT NULL,
	valid BOOLEAN NOT NULL,
	data_dump BLOB NOT NULL,
	deploy_date DATE NOT NULL,
	CONSTRAINT uncompleted_survey_pkey PRIMARY KEY (id));

CREATE TABLE Permitted_Patient_Hash(
	hash VARCHAR(10) NOT NULL,
	id int NOT NULL,
	CONSTRAINT patient_hash_pk PRIMARY KEY (hash),
	CONSTRAINT patient_hash_fk1 FOREIGN KEY(id) REFERENCES Uncompleted_Survey(id));

GRANT ALL ON formserver.* TO 'server'@'%' IDENTIFIED BY 'formserver';
GRANT FILE ON *.* TO 'server'@'%';

