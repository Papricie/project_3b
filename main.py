
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

#------------------------------------------------------------------------------

# Základní adresa volebního webu. 
# Budeme ji používat, abychom spojili částečné odkazy na obce
BASE_URL = "https://www.volby.cz/pls/ps2017nss/"

#------------------------------------------------------------------------------

def get_soup(url):
    """Stáhne stránku z internetu a převede ji do formátu, 
    se kterým se dobře pracuje."""
    resp = requests.get(url)          
    # Pošleme požadavek na web a stáhneme obsah stránky.
    resp.encoding = "utf-8"           
    # Nastavíme kódování na UTF-8 (aby se zobrazovala správně čeština).
    return BeautifulSoup(resp.text, "html.parser")  
    # Vrátíme HTML převedené do objektu, kde můžeme snadno hledat.

#------------------------------------------------------------------------------

def parse_obec(url, nazev_obce):
    """Zpracuje jednu obec – stáhne stránku a vybere z ní data 
    o voličích, obálkách a stranách."""
    soup = get_soup(url)  
    # Stáhneme HTML stránku s výsledky pro tuto konkrétní obec.

#------------------------------------------------------------------------------








