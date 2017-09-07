#!/usr/bin/python3

import sqlite3 as sq
import acentos
from time import sleep


def bd(fecha, titulo, calidad, enlace):
	conect = sq.connect(
			'/home/pi/bot/modulos/pelis_limpio.bd')
	conect.text_factory = str
	cursor = conect.cursor()
	# define la tabla series y las celdas id, titulos, calidades y obt
	series = """CREATE TABLE IF NOT EXISTS series(
                                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                fecha CHAR NOT NULL,
                                titulo CHAR NOT NULL,
                                calidad CHAR NOT NULL,
                                enlace CHAR NOT NULL
                                )"""
	# Ejecuta la creacion de la tabla series
	cursor.execute(series)
	
	# Define los datos que se introduciran
	datos = (fecha, titulo, calidad, enlace)
	
	# Creamos la orden que insertara los datos ordenados
	series = """INSERT INTO series(
                                    fecha,
                                    titulo,
                                    calidad,
                                    enlace)
                                    VALUES(?,?,?,?)
                                """
	# Ejecuta la introduccion de los datos en la tabla series
	cursor.execute(series, datos)
	cursor.close()
	conect.commit()
	conect.close()


def tildes():
	conexion = sq.connect('/home/pi/bot/database/pelis.bd')
	cursor = conexion.cursor()
	tabla = "SELECT * FROM series"
	if cursor.execute(tabla):
		filas = cursor.fetchall()
		for fila in filas:
			titulo = fila[2].lower()
			fecha = fila[1]
			calidad = fila[3]
			enlace = fila[4]
			if 'á' in titulo or \
				'é' in titulo or \
				'í' in titulo or \
				'ó' in titulo or \
				'ú' in titulo:
				titulo = acentos.acentos(titulo).lower()
				print(titulo, calidad)
				
			else:
				titulo = fila[2].lower()
				print(titulo, calidad)
			bd(fecha, titulo, calidad, enlace)
			
			
tildes()
