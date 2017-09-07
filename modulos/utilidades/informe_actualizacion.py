#!/usr/bin/python
# -*- coding: utf-8 -*-

import _sqlite3 as sq
import telebot
from constants import TOKEN

# creamos un bot con nuestro token:
bot = telebot.TeleBot(TOKEN)

mensaje = ''


conect = sq.connect('/home/pi/bot/database/usuarios.bd')
cursor = conect.cursor()
tabla = "SELECT * FROM user"

if cursor.execute(tabla):
	filas = cursor.fetchall()
	for fila in filas:
		try:
			user = (fila[5])
			bot.send_message(user, mensaje)
		except:
			print('el usuario  ' + fila[4] + '  Se ha dado de baja')
