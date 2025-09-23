
#------------------------------------------------------------------------------

# HLAVIČKA PROJEKTU
"""
Třetí projekt do Engeto Online Python Akademie
autor: Patricie Hermanová
email: patriciehermanova@gmail.com
"""

#------------------------------------------------------------------------------

import requests                 
# Načteme knihovnu requests – ta umí stáhnout webovou stránku z internetu.
from bs4 import BeautifulSoup   
# Načteme BeautifulSoup – to je nástroj na čtení a vyhledávání v HTML kódu.
import csv                      
# Načteme knihovnu csv – ta se používá na zapisování dat do CSV souborů.
from urllib.parse import urljoin, urlparse, parse_qs  
# Načteme funkce pro práci s odkazy (URL).
import sys                      
# Knihovna sys – díky ní můžeme číst, co uživatel zadal při spuštění programu.
import time                     
# Knihovna time – tu použijeme na zpomalení programu (pauza mezi stahováním).

# Základní adresa volebního webu. 
# Budeme ji používat, abychom spojili částečné odkazy na obce
BASE_URL = "https://www.volby.cz/pls/ps2017nss/"



