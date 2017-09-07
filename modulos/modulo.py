#!/usr/bin/python3

import requests
import sqlite3 as sq
import telebot
from telebot import types
import time
import re
import sys
from datetime import date, timedelta
from modulos.constants import TOKEN
import os

################################################################################
# ############################  MODULO LOGGING   ###############################
################################################################################

import logging

if __name__ == "__main__":

	logging.basicConfig(filename="modulo.log",
	                    filemode='w',
	                    level=logging.INFO,
	                    format='\n%(asctime)s %(levelname)-8s %(message)s',
	                    datefmt='              %H:%M:%S     %d %b %Y\n    ')


bot = telebot.TeleBot(TOKEN)


############################################################################
# ##########################  QUITA LOS ACENTOS  ###########################
############################################################################

# Se le pasa como argumento un string y lo retorna sin acentos
def quita_acentos(cadena):
	try:
		if 'á' in cadena:
			cadena = cadena.replace('á', 'a')
		if 'é' in cadena:
			cadena = cadena.replace('é', 'e')
		if 'í' in cadena:
			cadena = cadena.replace('í', 'i')
		if 'ó' in cadena:
			cadena = cadena.replace('ó', 'o')
		if 'ú' in cadena:
			cadena = cadena.replace('ú', 'u')
		return cadena
	except Exception:
		p = sys.exc_info()
		logging.warning('Error en busca_bd  '
						'%s\n              %s' % (p[0], str(p[1]).upper()))


##############################################################################
# #######################  DEVUELVE EL LINK AL .TORRENT  #####################
##############################################################################

# Se le pasa como argumento el enlace de la peli o serie de newpct y retorna el link al .torrent
def link_torrent(link):
	# Guarda la url "link" en la variable "website"
	try:
		website1 = requests.get(link)
		website = website1.text
		
		# Saca el enlace limpio de "website" y lo guarda en "torrent"
		corte1 = str(website).split('content-torrent')
		corte2 = str(corte1[1]).split('.torrent')
		torrent = str(corte2[0]).split('a href=\'')[1] + '.torrent'
		return torrent
	except Exception:
		p = sys.exc_info()
		logging.warning('Error modulo.link_torrent  '
						'%s\n              %s' % (p[0], str(p[1]).upper()))
	

#############################################################################
# ###########################  AÑADE UNA ALERTA  ############################# #
#############################################################################

# Añade una serie o peli a la base de datos alertas,
# guarda chat_id y título, también título para busqueda regex
def add_alerta(chat_id, titulo, regex):
	try:
		conect = sq.connect('/home/pi/bot/database/alertas.bd')
		conect.text_factory = str
		cursor = conect.cursor()
		
		# define la tabla series y las celdas id, titulos, calidades y obt
		alerta = """CREATE TABLE IF NOT EXISTS alerta(
									id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
									chat_id INT NOT NULL,
									titulo CHAR NOT NULL,
									regex CHAR NOT NULL
									)"""
		# Ejecuta la creacion de la tabla series
		cursor.execute(alerta)
		
		# Define los datos que se introduciran
		datos = (chat_id, titulo, regex)
		
		# Creamos la orden que insertara los datos ordenados
		alerta = """INSERT INTO alerta(chat_id,
										titulo,
										regex)
										VALUES(?,?,?)
									"""
		# Ejecuta la introduccion de los datos en la tabla series
		cursor.execute(alerta, datos)
		cursor.close()
		conect.commit()
		conect.close()
	except Exception:
		p = sys.exc_info()
		logging.warning('Error en modulo.add_alerta  '
						'%s\n              %s' % (p[0], str(p[1]).upper()))


############################################################################
# ###########  Envia lista de películas incluidas en alertas  ##############
############################################################################

def ver_alertas(chat_id):
	try:
		conect = sq.connect('/home/pi/bot/database/alertas.bd')
		cursor = conect.cursor()
		tabla = "SELECT * FROM alerta"
		
		if cursor.execute(tabla):
			filas = cursor.fetchall()
			for fila in filas:
				if chat_id == fila[1]:
					bot.send_message(chat_id, str(fila[0]) + '    🎬   ' + fila[2])
	except Exception:
		p = sys.exc_info()
		logging.warning('Error en modulo.ver_alertas  '
						'%s\n              %s' % (p[0], str(p[1]).upper()))


####################################################################################
# ###############  Añade una pelicula a la base de datos pelis.bd  #################
####################################################################################

def add_peli(fecha, titulo, calidad, enlace):
	try:
		conect = sq.connect('/home/pi/bot/database/pelis.bd')
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
		conect.commit()
	except Exception:
		p = sys.exc_info()
		logging.warning('Error en modulo.add_peli  '
						'%s\n              %s' % (p[0], str(p[1]).upper()))
	finally:
		cursor.close()
		conect.close()
		


###################################################################################
# ##################  AGREGA UN USUARIO A LA BASE DE DATOS  #######################
###################################################################################

def registro_usuario(nombre, usuario, ids):
	# Obtenemos fecha
	try:
		fecha = str(date.today())
		hora = str(time.strftime('%H'))
		conect = sq.connect('/home/pi/bot/database/usuarios.bd')
		cursor = conect.cursor()
		
		usuarios = """CREATE TABLE IF NOT EXISTS user(
					id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
					fecha INT NOT NULL,
					hora INT NOT NULL,
					nombre CHAR NOT NULL,
					usuario CHAR NOT NULL,
					ids INT NOT NULL)"""
		
		cursor.execute(usuarios)
		datos = (fecha, hora, nombre, usuario, ids)
		
		usuarios = """INSERT INTO user(
					fecha,
					hora,
					nombre,
					usuario,
					ids)
					VALUES(?,?,?,?,?)
				"""
		cursor.execute(usuarios, datos)
		cursor.close()
		conect.commit()
		conect.close()
	except Exception:
		p = sys.exc_info()
		logging.warning('Error modulo.registro_usuario  '
		                '%s\n              %s' % (p[0], str(p[1]).upper()))
	
######################################################################################
# ###############################  Busquedas standar  ################################
######################################################################################

def busca_bd(texto, chat_id):
	try:
		# Contador del Nº de resultados encontrados
		cont = 0
		encuentra = False
		
		# Añade '.*' en los espacios, al principio y al final para la busqueda regex
		bus = texto.replace(' ', '.*')
		bus = '.*' + bus + '.*'
		
		# Busca el imput en la base de datos
		conect = sq.connect('/home/pi/bot/database/pelis.bd')
		cursor = conect.cursor()
		tabla = "SELECT * FROM series"
		cursor.execute(tabla)
		filas = list(cursor)
		for fila in filas:
			
			# Si lo encuentra...
			if re.search(bus.lower(), fila[2].lower()) and cont < 15:
				encuentra = True
				cont = cont + 1
				
				# Manda un mensaje con el título, la calidad y el enlace de la película
				bot.send_message(chat_id, '🎬   ' + fila[2].upper() + '   🍿' +
								 fila[3] + '\n' + fila[4] + '    🔗')
				conect.commit()
				
				# Si hay más de 14 resultados, se consideran demasiados, se informa y se para
				if cont > 14:
					bot.send_message(chat_id, '‼  Hay resultados sin mostrar, '
											  'afina la busqueda  ‼')
					return
		# Si no obtiene ningún resultado busca en la web
		if not encuentra:
			try:
				cursor.close()
				conect.close()
				bot.send_message(chat_id, 'ℹ   sin resultados en la base de datos, '
										  'buscando en la web')
				
				busqueda = texto.replace(' ', '+')
				cont = 0
				fecha = str(time.strftime("%d/%m/%y"))
				
				# Busca en la web el input
				pagina = str('https://pasateatorrent.com/?s=' + busqueda +
							 '&post_type=Buscar+pel%C3%ADcula')
				
				# Saca la direccíón de cada película encontrada
				req = requests.get(pagina)
				html = req.text
				bloques_url = html.split('height="225"')
				for i in bloques_url:
					cont += 1
					if cont > 14:
						bot.send_message(chat_id, '‼  Hay resultados sin mostrar, afina la busqueda  ‼')
						return
					enlaces = re.search('(?<=<a href=")' + '.*' +
										'(?="><div class="contenedor_imagenes)', i)
					url = (enlaces.group())
					
					# obtiene los titulos de cada pelicula encontrada
					titulo1 = requests.get(url)
					titulo2 = titulo1.text
					titulo3 = re.search('(?<=apartado_texto_page">)' + '.*' +
										'(?=</div></h1>)', titulo2)
					titulo = (titulo3.group().lower())
					
					# obtiene el enlace al torrent
					descarga1 = titulo2.split('<tr class="lol">')
					for u in descarga1:
						if 'Click Aquí' in u:
							enlace = re.search('(?<=<td><a href=")' + '.*' +
											   '(?=">Click Aquí)', u)
							enlace = (enlace.group())
							
							# obtiene la calidad
							calidad1 = u.split('<td>')
							calidad = calidad1[2].replace('</td>', '')
							bot.send_message(chat_id, '🎬   ' +
											 titulo.upper() + '    🍿' +
											 calidad + '\n' +
											 enlace + '\n' + 'Add to BD')
							# Le quita los acentos al título
							titulo = quita_acentos(titulo)
							
							# Cada película encontrada es añadida a la base de dato
							# Cuando se vuelva a buscar la película,
							# la obtendrá rápidamente de la base de datos
							add_peli(fecha, titulo, calidad, enlace)
							
							# Si hay más de 14 resultados, se consideran demasiados, se informa y se para
							if cont > 14:
								bot.send_message(chat_id, '‼  Hay resultados sin mostrar, '
														  'afina la busqueda  ‼')
								return
			except:
				pass
			
			# Cuando termina la busqueda,
			# cont es 1, es que no ha obtenido resultados y se informa
			if cont == 1:
				bot.send_message(chat_id, '‼  NO HAY RESULTADOS....  ‼')
	except Exception:
		p = sys.exc_info()
		logging.warning('Error modulo.busca_bd  '
							'%s\n              %s' % (p[0], str(p[1]).upper()))

#####################################################################################
# ###########################  Busquedas solo web  ##################################
#####################################################################################


def busca_web(texto, chat_id):
	try:
		busqueda = texto.replace(' ', '+')
		cont = 0
		
		# Busca en la web el input
		pagina = str('https://pasateatorrent.com/?s=' + busqueda +
					 '&post_type=Buscar+pel%C3%ADcula')
		
		# Saca la direccíón de cada película encontrada
		req = requests.get(pagina)
		html = req.text
		bloques_url = html.split('height="225"')
		for i in bloques_url:
			try:
				enlaces = re.search('(?<=<a href=")' + '.*' +
									'(?="><div class="contenedor_imagenes)', i)
				url = (enlaces.group())
				
				# obtiene los titulos de cada pelicula encontrada
				titulo1 = requests.get(url)
				titulo2 = titulo1.text
				titulo3 = re.search('(?<=apartado_texto_page">)' + '.*' +
									'(?=</div></h1>)', titulo2)
				titulo = (titulo3.group().lower())
				
				# obtiene el enlace al torrent
				descarga1 = titulo2.split('<tr class="lol">')
				for u in descarga1:
					if 'Click Aquí' in u:
						enlace = re.search('(?<=<td><a href=")' + '.*' +
										   '(?=">Click Aquí)', u)
						enlace = (enlace.group())
						
						# obtiene la calidad
						calidad1 = u.split('<td>')
						calidad = calidad1[2].replace('</td>', '')
						bot.send_message(chat_id, '🎬   ' +
										 titulo.upper() + '    🍿' +
										 calidad + '\n' +
										 enlace)
						cont += 1
						
						# Si hay más de 14 resultados, se consideran demasiados, se informa y se para
						if cont > 14:
							bot.send_message(chat_id, '‼  Hay resultados sin mostrar, ')

				

			except:
				pass
	except Exception:
		p = sys.exc_info()
		logging.warning('Error modulo.busca_web  '
						'%s\n              %s' % (p[0], str(p[1]).upper()))
	if cont == 0:
		bot.send_message(chat_id, '‼  Sin resultados....')
		
		
###############################################################################
# ##############################  ELIMINA ALERTA   ############################
###############################################################################

def elimina_alerta(chat_id, indice):
	estado = False
	try:
		conect = sq.connect('/home/pi/bot/database/alertas.bd')
		cursor = conect.cursor()
		tabla = "SELECT * FROM alerta"
		
		if cursor.execute(tabla):
			filas = cursor.fetchall()
			for fila in filas:
				if fila[0] == int(indice) and chat_id == fila[1]:
					estado = True
					cursor.execute("DELETE FROM alerta WHERE id=" + indice)
					conect.commit()
					bot.send_message(chat_id, 'Se ha eliminado el '
					                          'indice %s :  "%s"' % (fila[0], fila[2].upper()))
						
			if not estado:
					bot.send_message(chat_id, '⛔   Índice no válido')

	except Exception:
		p = sys.exc_info()
		logging.warning('Error en modulo.ver_alertas  '
		                '%s\n              %s' % (p[0], str(p[1]).upper()))
