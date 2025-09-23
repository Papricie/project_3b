
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

    # Z odkazu na stránku obce zjistíme kód (číslo v parametru ?xobec=...)
    kod_obce = parse_qs(urlparse(url).query).get("xobec", ["N/A"])[0]
    # Použijeme funkce z knihovny urllib.parse.
    # Pokud by kód obce v URL chyběl, použijeme "N/A".

    def safe_find(headers):
        """Pomocná funkce: bezpečně najde obsah buňky <td> podle toho, 
        co má napsáno v "headers". Pokud se buňka nenajde, 
        vrátí prázdný text místo chyby."""
        td = soup.find("td", {"headers": headers})  
        # Najde první buňku <td> s daným atributem headers.
        return td.text.strip() if td else ""        
        # Pokud existuje, vrátí text uvnitř. Pokud ne, vrátí "".
    
    # Teď pomocí safe_find najdeme základní údaje o voličích:
    volici = safe_find("sa2")   # Celkový počet voličů v seznamu.
    obalky = safe_find("sa3")   # Kolik bylo vydaných obálek.
    platne = safe_find("sa6")   # Kolik bylo platných hlasů.

    # Najdeme všechny názvy politických stran v této obci.
    # Jsou v buňkách tabulky <td> s class="overflow_name".
    strany = [td.text.strip() for td in soup.find_all
              ("td", class_="overflow_name")]

    # Najdeme všechny počty hlasů pro strany.
    hlasy = []                         
    # Sem uložíme čísla (počty hlasů).
    for td in soup.find_all("td"):     
        # Projdeme všechny buňky tabulky <td>.
        headers = td.get("headers", "")  
        # Zjistíme, co je napsáno v "headers".
        if isinstance(headers, list):    
        # Někdy je to seznam → převedeme na text.
            headers = " ".join(headers)
        if headers.endswith("sb3"):      
        # Hledáme jen ty buňky, které mají v názvu sb3 (sloupec s hlasy).
            hlasy.append(td.text.strip())  
            # Přidáme počet hlasů do seznamu.

    # Vytvoříme slovník (tabulku v paměti), kam uložíme výsledky pro obec.
    data = {
        "Kód obce": kod_obce,          # Číselný kód obce.
        "Název obce": nazev_obce,      # Název obce (z okresní stránky).
        "Voliči v seznamu": volici,    # Počet voličů.
        "Vydané obálky": obalky,       # Počet vydaných obálek.
        "Platné hlasy": platne,        # Počet platných hlasů.
    }

    # Teď přidáme všechny strany a jejich počty hlasů.
    # Přiřazujeme podle pořadí – první strana má první číslo, 
    # druhá strana druhé číslo atd.
    for s, h in zip(strany, hlasy):
        data[s] = h

    return data  # Vrátíme slovník se všemi výsledky pro tuto jednu obec.

#------------------------------------------------------------------------------

def main():
    """Hlavní funkce – stará se o celý postup: zpracování okresu 
    a zápis výsledků do souboru."""

    # Nejprve zkontrolujeme, jestli uživatel zadal přesně dva argumenty.
    if len(sys.argv) != 3:
        print("Použití: python main.py <URL_OKRESU> <vystup.csv>")  
        # Nápověda pro uživatele.
        sys.exit(1)  
        # Ukončí program.

    url_okres = sys.argv[1]  
    # První argument = adresa okresu (odkaz na stránku).
    vystup = sys.argv[2]     
    # Druhý argument = název výstupního CSV souboru.

    soup = get_soup(url_okres)             
    # Stáhneme stránku okresu.
    tabulky = soup.find_all("table", class_="table")  
    # Najdeme všechny tabulky se seznamem obcí.

    obec_links = []  # Tady budeme mít seznam (odkaz, název obce).
    for tabulka in tabulky:                    
        # Projdeme každou tabulku.
        for tr in tabulka.find_all("tr"):      
            # Projdeme každý řádek v tabulce.
            cislo_td = tr.find("td", class_="cislo")          
            # Najdeme buňku s číslem obce.
            nazev_td = tr.find("td", class_="overflow_name")  
            # Najdeme buňku s názvem obce.
            if cislo_td and nazev_td:          
                # Pokud obě buňky existují:
                a = cislo_td.find("a", href=True)  
                # Najdeme odkaz uvnitř čísla obce.
                if a and "xobec=" in a["href"]:    
                    # Pokud je to skutečně odkaz na obec:
                    url = urljoin(BASE_URL, a["href"])  
                    # Spojíme základní URL a relativní odkaz.
                    nazev_obce = nazev_td.text.strip()  
                    # Název obce (text uvnitř buňky).
                    obec_links.append((url, nazev_obce))  
                    # Přidáme dvojici (odkaz, název).

    # Odstraníme duplicity (pokud by se nějak objevily).
    obec_links = list(dict.fromkeys(obec_links))
    print(f"Nalezeno obcí: {len(obec_links)}")  
    # Vypíšeme, kolik obcí jsme našli.

    data_rows = []  # Tady bude seznam se slovníky (každá obec = jeden slovník).
    for idx, (url, nazev_obce) in enumerate(obec_links[:3], 1):  
        # [:3] znamená: vem jen první 3 obce na test.
        print(f"Zpracovávám obec {idx}/{len(obec_links)}... {nazev_obce}")  
        # Vypíšeme průběh.
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

# python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101" vysledky.csv
# uvozovky jsou nutné, protože URL obsahuje znaky & a =

#------------------------------------------------------------------------------  





    






















