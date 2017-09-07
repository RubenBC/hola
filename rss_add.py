#!/usr/bin/python3

"""Este script se encarga de parsear el feed de newpct, comprueba cada nuevo post, y si es una
película la agrega a la base de datos pelis.bd, ubicada en la carpeta database.

Este script se ejecutará con un cron cada 15 minutos para comprobar nuevos resultados.
"""

import feedparser
from bs4 import BeautifulSoup
import requests
import sqlite3 as sq
import re
import time
import telebot
from modulos.constants import TOKEN
from modulos import modulo


################################################################################
# ############################  MODULO LOGGING   ###############################
################################################################################

import logging
import sys


logging.basicConfig(filename="/home/pi/bot/log_rss_add.log",
					filemode='w',
					level=logging.WARNING,
					format='\n%(asctime)s %(levelname)-8s %(message)s',
					datefmt='              %H:%M:%S     %d %b %Y\n    ')

bot = telebot.TeleBot(TOKEN)

logging.warning('Se inicia el script')

# Obtiene los post de newpct
try:
	d = feedparser.parse('http://www.newpct.com/feed/')
	
	# Capturo el post de control en la variabe "c"
	with open("/home/pi/bot/archivos/control_rss.txt", "r") as a:
		c = a.read()
		time.sleep(3)
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
			url = (d["entries"][i]["link"])
			req = requests.get(url)
			soup = BeautifulSoup(req.text, "html.parser")
			logging.warning('link === %s' % (d["entries"][i]["link"]))
			
	except Exception:
		y = sys.exc_info()
		logging.error('Error de parseo soup  %s\n              %s' % (y[0], str(y[1]).upper()))
		
	# Saca el titulo de la peli.
	try:
		
		t = soup.find(id='title_ficha')
		titul = re.search('(?<=Gratis">)' + '.*' + '(?=</a></h2>)', str(t))
		titulo = titul.group()
		logging.warning('Titulo nuevo obtenido:\n              %s' % titulo)
	except Exception:
		y = sys.exc_info()
		logging.error('Error sacando el titulo, +-98  %s\n              %s' %
						(y[0], str(y[1]).upper()))
		titulo = 'desconocido'
	
	# saca la calidad de la peli
	try:
		sub = soup.find(id='subtitle_ficha')
		c1 = str(sub).split(']')
		c2 = c1[0].split('[')
		calidad = (c2[1])
		logging.warning('Calidad nueva obtenida:\n              %s' % calidad.upper())

	except Exception:
		calidad = 'desconocida'
		y = sys.exc_info()
		logging.error('Error sacando la calidad  %s\n              %s' % (y[0], str(y[1]).upper()))
	
	# saca el enlace al .torrent
	try:
		enl = soup.find(id='content-torrent')
		enla = re.search('(?<=href=")' + '.*' + '(?=" id)', str(enl))
		enlace = enla.group()
		logging.warning('Enlace nuevo obtenido:\n              %s' % enlace.upper())

	except Exception:
		enlace = 'desconocido'
		y = sys.exc_info()
		logging.error('Error sacando el enlace  %s\n              %s' % (y[0], str(y[1]).upper()))
	
	# Añade los datos obtenidos a la base de datos pelis.db
	try:
		logging.warning('Se agrega a la bd:\n              %s' % str(titulo.upper()))
		fecha = (str(time.strftime("%d/%m/%y")))
		modulo.add_peli(fecha, str(titulo), str(calidad), str(enlace))
	except Exception:
		y = sys.exc_info()
		logging.error('Error añadiendo a la base de datos  %s\n              %s' %
						(y[0], str(y[1]).upper()))


# Escribo el nuevo post de control
try:
	with open("/home/pi/bot/archivos/control_rss.txt", "w") as archivo:
		archivo.write((d["entries"][0]["link"]))
except Exception:
	y = sys.exc_info()
	logging.error('Error escribiendo nuevo post de control  %s\n              %s' %
				  (y[0], str(y[1]).upper()))
logging.warning('FINALIZADO')
