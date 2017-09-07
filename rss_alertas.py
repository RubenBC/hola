#!/usr/bin/python3

import feedparser
from bs4 import BeautifulSoup
import requests
import sqlite3 as sq
import re
import time
import telebot
from modulos.constants import TOKEN
from modulos import modulo
import logging
import sys


logging.basicConfig(filename="/home/pi/bot/log_rss_alertas.log",
					filemode='w',
					level=logging.WARNING,
					format='\n%(asctime)s %(levelname)-8s %(message)s',
					datefmt='              %H:%M:%S     %d %b %Y\n    ')

bot = telebot.TeleBot(TOKEN)

logging.warning('Se inicia el script')

try:
	d = feedparser.parse('http://www.newpct.com/feed/')
	
	# Capturo el post de control en la variabe "c"
	with open("/home/pi/bot/archivos/control_alerta.txt", "r") as a:
		c = a.read()
	logging.warning('Post de control a la variable c')
except Exception:
	y = sys.exc_info()
	logging.error('Error capturando el post de control  %s\n              %s'
	              % (y[0], str(y[1]).upper()))
	
	# Comparo el post de control "c" con cada post de newpct, si coinciden
	# salimos, si no coinciden y el nuevo post no contiene la palabra "Temporada"
	# (eso signifina que es una serie), agrega la peli a la base de datos pelis.db
for i in range(0, 300):
	try:
		if c == (d["entries"][i]["link"]):
			logging.warning('Post de control coincide con el post[i]')
			break
		else:
			title = (d["entries"][i]["title"])
			conexion = sq.connect('/home/pi/bot/database/alertas.bd')
			cursor = conexion.cursor()
			tabla = "SELECT * FROM alerta"
			if cursor.execute(tabla):
				filas = cursor.fetchall()
				for fila in filas:
					time.sleep(2)
					if re.match(str(fila[3]).lower(), str(title).lower()):
						link = modulo.link_torrent(d["entries"][i]["link"])
						bot.send_message(fila[1], '🎬  ' + d["entries"][i]["title"] +
						                 '\n\n' + '🔗   ' + link)
						logging.error('Se envia la peli %a' % link)
					
					else:
						pass
	except Exception:
		y = sys.exc_info()
		logging.error('Error comprobando alertas  %s\n              %s' %
		              (y[0], str(y[1]).upper()))
		
		# Escribo el nuevo post de control
try:
	with open("/home/pi/bot/archivos/control_alerta.txt", "w") as archivo:
		archivo.write((d["entries"][0]["link"]))
except Exception:
	y = sys.exc_info()
	logging.error('Error escribiendo nuevo post de control  %s\n              %s' %
	              (y[0], str(y[1]).upper()))
logging.warning('FINALIZADO')
