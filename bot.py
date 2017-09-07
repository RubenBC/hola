#!/usr/bin/python3

import time
import sys
import re
import telebot
from telebot import types
import requests
import sqlite3 as sq
import argparse
import os


# Modulos propios
from modulos import modulo
from modulos.constants import BIENVENIDA, HELP_, TOKEN

################################################################################
# ############################  MODULO LOGGING   ###############################
################################################################################

import logging

logging.basicConfig(filename="/home/pi/bot/bot.log",
					filemode='w',
					level=logging.INFO,
					format='\n%(asctime)s %(levelname)-8s %(message)s',
					datefmt='              %H:%M:%S     %d %b %Y\n    ')


################################################################################
# ###########################   iNSTANCIA TELEBOT   ############################
################################################################################

bot = telebot.TeleBot(TOKEN)

# Cuando se manda un comando con el bot detenido se desecha el comando
bot.skip_pending = True


###############################################################################
# #################################   START   #################################
###############################################################################

@bot.message_handler(commands=['start'])
def start(mensaje):
	try:
		# Se obtienen los datos del usuario y se le da la bienvenida
		chat_id = mensaje.chat.id
		nombre = mensaje.chat.first_name
		user_telegram = mensaje.chat.username
		
		# Si el usuario no ha añadido el username o first_name,
		# toma como valor "vacio" para evitar fallos al retornar None
		if nombre is None:
			nombre = 'vacio'
		if user_telegram is None:
			user_telegram = 'vacio'
		
		logging.info('El usuario %s ha iniciado el bot' % nombre)
		bot.send_message(chat_id, 'HOLA ' + nombre.upper() + '\n\n' + BIENVENIDA)
		quita_teclado(mensaje.chat.id)

	except Exception:
		y = sys.exc_info()
		logging.warning('Error en función Start  %s\n              %s' % (y[0], str(y[1]).upper()))
	
	# Comprueba si el usuario está en la base de datos
	try:
		conexion = sq.connect('/home/pi/bot/database/usuarios.bd')
		cursor = conexion.cursor()
		tabla = "SELECT ids FROM user"
		if cursor.execute(tabla):
			filas = cursor.fetchall()
			esta = False
			for fila in filas:
				if chat_id in fila:
					esta = True
			
			# Si ya está registrado pasamos
			if esta is True:
				pass
			
			# Si no lo está se añade a la base de datos el nombre, su nick y chat id y se informa.
			else:
				modulo.registro_usuario(nombre, user_telegram, chat_id)
				logging.info('Nuevo usuario registrado: %s' % nombre)
				bot.send_message(chat_id, 'Hola ' + nombre + ', Tu usuario ha sido ingresado '
															 'en la base de datos 👍 ')
	except Exception:
		y = sys.exc_info()
		logging.warning('Error en función Start añade bd  %s\n              %s'
		                % (y[0], str(y[1]).upper()))
	
###############################################################################
# ################################   HELP   ###################################
###############################################################################

# Comando que muestra la ayuda
@bot.message_handler(commands=['help'])
def ayuda(mensaje):
	logging.info('El usuario %s ha iniciado ayuda' % mensaje.chat.first_name)
	bot.send_message(mensaje.chat.id, HELP_)


###############################################################################
# ##############################  TECLADO ALERTAS   ###########################
###############################################################################

# Comando que lanza el teclado alertas
@bot.message_handler(commands=['alertas'])
def alertas(mensaje):
	teclado_alertas(mensaje)


# Configura el teclado del menu alertas
def teclado_alertas(mensaje):
	try:
		logging.info('El usuario %s ha iniciado teclado_alertas' % mensaje.chat.first_name)
		chat_id = mensaje.chat.id
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
		markup.add('➕   Añadir', '📋   Lista')
		markup.add('❌   Eliminar', 'salir')
		markup.Remove_keyboard = True
		msg = bot.send_message(chat_id, 'Pulsa /help si necesitas ayuda',
							   reply_markup=markup)
		bot.register_next_step_handler(msg, process_teclado_alerta)
	except Exception:
		p = sys.exc_info()
		logging.warning('Error en función teclado alertas  '
						'%s\n              %s' % (p[0], str(p[1]).upper()))


# Función que se encarga de realizar la acción del boton del teclado pulsado
def process_teclado_alerta(mensaje):
	try:
		men = mensaje.text
		chat_id = mensaje.chat.id
		
		# Añade una serie a las alertas
		if men == '➕   Añadir':
			logging.info("El usuario %s inicia añadir" % mensaje.chat.first_name)
			msg = bot.reply_to(mensaje, 'Introduce el nombre de la serie o la pélicula\n'
										'Por ejemplo, iron man 3')
			bot.register_next_step_handler(msg, add_alertas)
			quita_teclado(chat_id)
			
		# Muestra las series que tienes agregadas en la alerta
		if men == '📋   Lista':
			logging.info("El usuario %s inicia lista" % mensaje.chat.first_name)
			modulo.ver_alertas(chat_id)
			time.sleep(.5)
			teclado_alertas(mensaje)
		
		# Elimina una serie de la alerta
		if men == '❌   Eliminar':
			logging.info("El usuario %s inicia eliminar" % mensaje.chat.first_name)
			modulo.ver_alertas(chat_id)
			msg = bot.reply_to(mensaje, 'Introduce el indice a eliminar')
			bot.register_next_step_handler(msg, elimina_alerta)
		
		if men == 'salir':
			logging.info("El usuario %s inicia salir" % mensaje.chat.first_name)
			quita_teclado(chat_id)
			pass
		
	except Exception:
		p = sys.exc_info()
		logging.warning('Error en proces_next_step  '
						'%s\n              %s' % (p[0], str(p[1]).upper()))


# Función que elimina el teclado de la pantalla
def quita_teclado(chat_id):
	logging.info('El usuario %s ha iniciado quita_teclado' % chat_id)
	markup = types.ReplyKeyboardRemove(selective=False)
	bot.send_message(chat_id, '👍', reply_markup=markup)


###############################################################################
# ############################  ELIMINA UNA ALERTA    ##########################
###############################################################################

def elimina_alerta(mensaje):
	logging.info('El usuario %s ha eliminado una alerta' % mensaje.chat.first_name)
	chat_id = mensaje.chat.id
	indice = mensaje.text
	modulo.elimina_alerta(chat_id, indice)
	teclado_alertas(mensaje)


###############################################################################
# ##################  AÑADIR UNA PELI O SERIE A LA ALERTA   ###################
###############################################################################

def add_alertas(mensaje):
	try:
		logging.info('El usuario %s ha añadido una alerta' % mensaje.chat.first_name)
		texto = mensaje.text
		rege = str(texto).replace(' ', '.*')
		regex = '.*' + rege + '.*'
		chat_id = mensaje.chat.id
		modulo.add_alerta(chat_id, texto, regex)
		bot.send_message(chat_id, '✅  "' + texto.upper() + '"' + '   Agregado a la base de datos')
		quita_teclado(chat_id)
	except Exception:
		p = sys.exc_info()
		logging.warning('Error en add_alertas  '
						'%s\n              %s' % (p[0], str(p[1]).upper()))
	time.sleep(.5)
	teclado_alertas(mensaje)


###############################################################################
# #############################  BUSCAR EN LA WEB   ###########################
###############################################################################

# Este comando realiza una busqueda solo en la web, no se agregan los resultados a la b.d.
@bot.message_handler(commands=['w'])
def busca_web(mensaje):
	# Pasa el input al modulo busca_web, del paquete busca_peli
	# Los caracteres * y + están prohibidos al entrar en conflicto con la búsqueda regex
	try:
		if '*' in mensaje.text or '+' in mensaje.text:
			chat_id = mensaje.chat.id
			bot.send_message(chat_id, "No se pueden introducir los caracteres: '*' ni '+'")
			return
		
		# Realiza la búsqueda
		else:
			chat_id = mensaje.chat.id
			bot.send_message(chat_id, 'Buscando.....  🔎')
			men = modulo.quita_acentos(mensaje.text)
			men = men.split(' ')
			mensajes = men[1:]
			busqueda = ' '.join(mensajes)
			texto = busqueda.lower()
			logging.info('El usuario %s realiza la busqueda web: %s' % (mensaje.chat.first_name, texto))
	
			modulo.busca_web(texto, chat_id)
			bot.send_message(chat_id, '👍')
	except Exception:
		p = sys.exc_info()
		logging.warning('Error en busca_web  '
						'%s\n              %s' % (p[0], str(p[1]).upper()))


###############################################################################
# ############################  BUSQUEDA ESTANDAR   ###########################
###############################################################################

# Realiza una busqueda, primero en la b.d. Si no obtiene resultados busca en la web
# y agrega los resultados a la b.d.
@bot.message_handler(commands=['', 'busca'])
def busca_bd(mensaje):
	# Pasa el input al modulo busca_bd, del paquete busca_peli
	# Los caracteres * y + están prohibidos al entrar en conflicto con la búsqueda regex
	try:
		if '*' in mensaje.text or '+' in mensaje.text:
			chat_id = mensaje.chat.id
			bot.send_message(chat_id, "No se pueden introducir los caracteres: '*' ni '+'")
			bot.send_message(chat_id, '👍')
			return
		
		# inicia la busqueda
		else:
			chat_id = mensaje.chat.id
			bot.send_message(chat_id, 'Buscando.....  🔎')
			men = modulo.quita_acentos(mensaje.text)
			men = men.split(' ')
			mensajes = men[1:]
			busqueda = ' '.join(mensajes)
			texto = busqueda.lower()
			logging.info('El usuario %s realiza la bsqueda estandar: %s' % (mensaje.chat.first_name, texto))
			modulo.busca_bd(texto, chat_id)
			bot.send_message(chat_id, '👍')
	except Exception:
		p = sys.exc_info()
		logging.warning('Error en busca_bd  '
						'%s\n              %s' % (p[0], str(p[1]).upper()))


###############################################################################
# ############################    ADMIN    ####################################
###############################################################################

@bot.message_handler(commands=['admin'])
# def admin(mensaje):
def teclado_admin(mensaje):
	try:
		if mensaje.chat.id == 71240965:
			chat_id = mensaje.chat.id
			markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
			markup.add('👤   Usuarios', '📄   Log')
			markup.add('🔴   Salir', '♻   Restart')
			markup.Remove_keyboard = False
			msg = bot.send_message(chat_id, 'Pulsa /help si necesitas ayuda',
			                       reply_markup=markup)
			bot.register_next_step_handler(msg, process_teclado_admin)
			logging.info('Iniciada función Admin por %s' % mensaje.chat.first_name)
		else:
			bot.send_message(mensaje.chat.id, 'No eres admin')
			quita_teclado(mensaje.chat.id)
			logging.warning('El usuario % ha intentado acceder a admin' % mensaje.chat.username)
	except Exception:
		p = sys.exc_info()
		logging.warning('Error en función teclado admin  '
		                '%s\n              %s' % (p[0], str(p[1]).upper()))


def process_teclado_admin(mensaje):
	try:
		men = mensaje.text
		chat_id = mensaje.chat.id
		
		# Añade una serie a las alertas
		if men == '👤   Usuarios':
			conexion = sq.connect('/home/pi/bot/database/usuarios.bd')
			cursor = conexion.cursor()
			tabla = "SELECT * FROM user"
			if cursor.execute(tabla):
				filas = cursor.fetchall()
				for fila in filas:
					bot.send_message(chat_id, fila[3] + '   -   ' + fila[4] +
					                 '   -   ' + str(fila[5]))
				teclado_admin(mensaje)

		# Muestra las series que tienes agregadas en la alerta
		if men == '📄   Log':
			with open('/home/pi/bot/bot.log') as b:
				bot.send_document(chat_id, b)
				teclado_admin(mensaje)
			
		if men == '♻   Restart':
			quita_teclado(mensaje.chat.id)
			os.system("ps -ef | grep bot.py | awk '{print $2}' | xargs sudo kill")
			
		if men == '🔴   Salir':
			quita_teclado(mensaje.chat.id)

	except Exception:
		p = sys.exc_info()
		logging.warning('Error en proces_next_step2  '
		                '%s\n              %s' % (p[0], str(p[1]).upper()))

bot.polling()
