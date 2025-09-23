
"""
Třetí projekt do Engeto Online Python Akademie
autor: Patricie Hermanová
email: patriciehermanova@gmail.com
"""

#------------------------------------------------------------------------------

import requests # stáhnutí webové stránky
from bs4 import BeautifulSoup # čtení a vyhledávání v HTML
import csv # zápis dat do CSV
from urllib.parse import urljoin, urlparse, parse_qs # práce s odkazy
import sys # vložené argumenty při spuštění programu
import time # pauza mezi stahováním

#------------------------------------------------------------------------------

BASE_URL = "https://www.volby.cz/pls/ps2017nss/"
# základní adresa volebního webu, spojení částečných odkazů na obce

#------------------------------------------------------------------------------

def get_soup(url):
    """Stáhne stránku z internetu a převede ji do formátu, 
    se kterým se dobře pracuje."""
    resp = requests.get(url) # pošle požadavek na web a stáhne obsah stránky
    resp.encoding = "utf-8" # kódování na UTF-8 (zobrazení češtiny)
    return BeautifulSoup(resp.text, "html.parser") # HTML převedené na objekt

#------------------------------------------------------------------------------

def parse_obec(url, nazev_obce):
    """Zpracuje jednu obec – stáhne stránku a vybere z ní data 
    o voličích, obálkách a stranách."""
    soup = get_soup(url) # HTML stránka s výsledky pro konkrétní obec

    kod_obce = parse_qs(urlparse(url).query).get("xobec", ["N/A"])[0]
    # z odkazu zjistí kód, pokud chybí, vypíše "N/A"

    def safe_find(headers):
        """Pomocná funkce: bezpečně najde obsah buňky <td> podle toho, 
        co má napsáno v "headers". Pokud se buňka nenajde, 
        vrátí prázdný text místo chyby."""
        td = soup.find("td", {"headers": headers}) # najde buňku <td> headers
        return td.text.strip() if td else "" # pokud existuje, vrátí text
    
    volici = safe_find("sa2")  
    obalky = safe_find("sa3")   
    platne = safe_find("sa6")
    # najde základní údaje o voličích   

    strany = [td.text.strip() for td in soup.find_all
              ("td", class_="overflow_name")]
    # najde názvy stran v buňkách tabulky <td> s class="overflow_name"

    hlasy = [] # uloží počty hlasů
    for td in soup.find_all("td"): # projde buňky tabulky <td>
        headers = td.get("headers", "") # zjistí, co je napsáno v "headers"
        if isinstance(headers, list): # seznam → převedeme na text
            headers = " ".join(headers)
        if headers.endswith("sb3"): # hledá buňky, které mají v názvu sb3
            hlasy.append(td.text.strip()) # přidá počet hlasů do seznamu

    data = {
        "Kód obce": kod_obce,          
        "Název obce": nazev_obce,      
        "Voliči v seznamu": volici,    
        "Vydané obálky": obalky,       
        "Platné hlasy": platne,        
    } # vytvoří slovník s výsledky pro obec

    for s, h in zip(strany, hlasy): # přidá všechny strany a počty hlasů
        data[s] = h

    return data  # vrátí slovník se všemi výsledky pro tuto obec

#------------------------------------------------------------------------------

def main():
    """Hlavní funkce – stará se o celý postup: zpracování okresu 
    a zápis výsledků do souboru."""

    if len(sys.argv) != 3: # zkontroluje přesně dva argumenty
        print("Použití: python main.py <URL_OKRESU> <vystup.csv>") # nápověda
        sys.exit(1) # ukončí program

    url_okres = sys.argv[1] # 1. argument = adresa okresu (odkaz na stránku)
    vystup = sys.argv[2] # 2. argument = název výstupního CSV souboru

    soup = get_soup(url_okres) # stáhne stránku okresu
    tabulky = soup.find_all("table", class_="table") # najde tabulky s obcemi

    obec_links = []  # tady bude seznam (odkaz, název obce)
    for tabulka in tabulky: # projde každou tabulku
        for tr in tabulka.find_all("tr"): # projde každý řádek
            cislo_td = tr.find("td", class_="cislo") # najde kód obce
            nazev_td = tr.find("td", class_="overflow_name") # najde název obce
            if cislo_td and nazev_td: # pokud obě buňky existují:
                a = cislo_td.find("a", href=True) # najde url uvnitř kódu obce
                if a and "xobec=" in a["href"]: # pokud je to url obce
                    url = urljoin(BASE_URL, a["href"]) # spojí se základním URL
                    nazev_obce = nazev_td.text.strip() # název (text buňky)
                    obec_links.append((url, nazev_obce)) # dvojice odkaz+název

    # Odstraní duplicity (pokud by se nějak objevily).
    obec_links = list(dict.fromkeys(obec_links))
    print(f"Nalezeno obcí: {len(obec_links)}")  
    # Vypisuje, kolik obcí je nalezeno.

    data_rows = []  # Tady bude seznam se slovníky (každá obec = jeden slovník).
    for idx, (url, nazev_obce) in enumerate(obec_links[:2], 1):  
        # [:2] znamená: vem jen první 2 obce na test.
        print(f"Zpracovávám obec {idx}/{len(obec_links)}... {nazev_obce}")  
        # Vypisuje průběh.
        obec_data = parse_obec(url, nazev_obce)  # Získáme data pro obec.
        data_rows.append(obec_data)              # Přidáme je do seznamu.
        time.sleep(1)  # Uděláme 1 vteřinu pauzu (abychom nezatížili server).

    # Teď zjistíme, jaké všechny sloupce (klíče) potřebujeme do CSV.
    all_keys = set()  # množina všech klíčů (názvy sloupců).
    for row in data_rows:         # projdeme všechny obce
        all_keys.update(row.keys())  # přidáme názvy sloupců

    # Hlavička CSV souboru – nejprve základní údaje, pak názvy všech stran.
    hlavicka = ["Kód obce", "Název obce", "Voliči v seznamu", "Vydané obálky", 
                "Platné hlasy"] + \
        [k for k in all_keys if k not in 
         ("Kód obce", "Název obce", "Voliči v seznamu", "Vydané obálky", 
          "Platné hlasy")]
    
    # Teď vytvoříme a zapíšeme CSV soubor.
    with open(vystup, "w", newline="", encoding="utf-8") as f:  
        # Otevřeme soubor pro zápis.
        zapisovac = csv.DictWriter(f, fieldnames=hlavicka)  
        # Připravíme zapisovač pro slovníky.
        zapisovac.writeheader()     
        # Zapíšeme první řádek – hlavičku tabulky.
        zapisovac.writerows(data_rows)  
        # Zapíšeme všechny obce.

        print(f"Hotovo! Data uložená do {vystup}")  
        # Potvrdíme, že program skončil a soubor je hotový.

if __name__ == "__main__":
    main()  # Tohle spustí funkci main() – takže program začne běžet.

#------------------------------------------------------------------------------   

"""python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101" vysledky.csv"""
# uvozovky jsou nutné, protože URL obsahuje znaky & a =

#------------------------------------------------------------------------------  





    






















