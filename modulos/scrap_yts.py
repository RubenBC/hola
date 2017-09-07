#!/usr/bin/python3


import requests
from bs4 import BeautifulSoup
import re
import logging
import sys


'''logging.basicConfig(# filename="log.log",
					filemode='w',
					level=logging.INFO,
					format='\n%(asctime)s %(levelname)-8s %(message)s',
					datefmt='              %H:%M:%S     %d %b %Y\n    ')'''

def url():
		cont = 0
		for i in range(2, 3):
			pagina = 'https://yts.ag/browse-movies?page=' + str(i)
			req = requests.get(pagina)

			# Pasamos el contenido HTML de la web a un objeto BeautifulSoup()
			soup = BeautifulSoup(req.text, "html.parser")
			for a in soup.find_all('a', href=True):
				if 'yts.ag/movie' in (a['href']):
					print(a['href'])
					url_txt = requests.get(a['href'])

					b = BeautifulSoup(url_txt.text, "html.parser")
					for n in b.find_all('title'):
						print(n)

					
					
					

url()
