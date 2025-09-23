

# python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101" vysledky.csv

import requests             # knihovna pro stahování obsahu z internetu (HTTP požadavky)
from bs4 import BeautifulSoup  # knihovna pro parsování (čtení a hledání v HTML kódu)
import csv                  # knihovna pro práci se soubory CSV (uložení výsledků)
from urllib.parse import urljoin, urlparse, parse_qs  # funkce pro práci s URL (spojování, rozklad na části, čtení query parametrů)
import sys                  # knihovna pro čtení argumentů z příkazové řádky
import time                 # knihovna pro zpomalení skriptu (pauza mezi požadavky na server)

# Základní URL volebního webu – bude se používat při spojování s relativními odkazy
BASE_URL = "https://www.volby.cz/pls/ps2017nss/"


def get_soup(url):
    """Stáhne HTML stránku a vrátí ji jako objekt BeautifulSoup pro snadné vyhledávání."""
    resp = requests.get(url)          # pošle požadavek na server
    resp.encoding = "utf-8"           # nastaví správné kódování (aby české znaky nebyly rozbité)
    return BeautifulSoup(resp.text, "html.parser")  # vrátí zpracovanou HTML stránku


def parse_obec(url, nazev_obce):
    """Načte stránku jedné obce, vytáhne výsledky voleb a vrátí je jako slovník."""
    soup = get_soup(url)  # stáhneme stránku s výsledky pro konkrétní obec

    # z URL si vytáhneme kód obce (xobec=...)
    kod_obce = parse_qs(urlparse(url).query).get("xobec", ["N/A"])[0]

    # pomocná funkce: bezpečně najde <td> podle atributu 'headers'
    def safe_find(headers):
        td = soup.find("td", {"headers": headers})
        return td.text.strip() if td else ""   # vrátí obsah buňky, nebo prázdný string pokud neexistuje

    # základní údaje o voličích
    volici = safe_find("sa2")   # počet voličů v seznamu
    obalky = safe_find("sa3")   # počet vydaných obálek
    platne = safe_find("sa6")   # počet platných hlasů
   
    # názvy všech stran – jsou v buňkách s class="overflow_name"
    strany = [td.text.strip() for td in soup.find_all("td", class_="overflow_name")]

    # počty hlasů – jsou v buňkách s atributem headers, které končí na "sb3"
    hlasy = []
    for td in soup.find_all("td"):
        headers = td.get("headers", "")
        if isinstance(headers, list):           # BeautifulSoup někdy vrací headers jako list
            headers = " ".join(headers)         # sjednotíme na string
        if headers.endswith("sb3"):             # hledáme jen ty, které končí na sb3
            hlasy.append(td.text.strip())

    # složíme výsledky do slovníku
    data = {
        "Kód obce": kod_obce,
        "Název obce": nazev_obce,
        "Voliči v seznamu": volici,
        "Vydané obálky": obalky,
        "Platné hlasy": platne,
    }

    # každé straně přiřadíme její počet hlasů
    for s, h in zip(strany, hlasy):
        data[s] = h

    return data  # vrací slovník s daty jedné obce


def main():
    """Hlavní funkce – zpracuje okres a uloží výsledky do CSV."""
    # kontrola argumentů – musíme zadat 2 argumenty: URL a název CSV souboru
    if len(sys.argv) != 3:
        print("Použití: python main.py <URL_OKRESU> <vystup.csv>")
        sys.exit(1)

    url_okres = sys.argv[1]  # první argument = URL na stránku okresu
    vystup = sys.argv[2]     # druhý argument = název výstupního CSV

    soup = get_soup(url_okres)             # načteme stránku okresu
    tabulky = soup.find_all("table", class_="table")  # najdeme všechny tabulky s obcemi

    obec_links = []  # sem uložíme odkazy na jednotlivé obce
    for tabulka in tabulky:
        for tr in tabulka.find_all("tr"):              # projdeme každý řádek tabulky
            cislo_td = tr.find("td", class_="cislo")   # buňka s číslem obce (odkaz)
            nazev_td = tr.find("td", class_="overflow_name")  # buňka s názvem obce
            if cislo_td and nazev_td:
                a = cislo_td.find("a", href=True)      # odkaz na stránku obce
                if a and "xobec=" in a["href"]:        # kontrola, že je tam parametr obce
                    url = urljoin(BASE_URL, a["href"]) # spojíme základní URL + odkaz
                    nazev_obce = nazev_td.text.strip() # název obce z tabulky
                    obec_links.append((url, nazev_obce))

    # odstraníme duplicity (pokud by se nějak objevily)
    obec_links = list(dict.fromkeys(obec_links))
    print(f"Nalezeno obcí: {len(obec_links)}")

    data_rows = []
    # [:3] = jen první 3 obce na test
    for idx, (url, nazev_obce) in enumerate(obec_links[:3], 1):
        print(f"Zpracovávám obec {idx}/{len(obec_links)}... {nazev_obce}")
        obec_data = parse_obec(url, nazev_obce)  # stáhneme data pro obec
        data_rows.append(obec_data)              # uložíme do seznamu
        time.sleep(1)                            # pauza mezi požadavky (slušnost k serveru)

    # složíme hlavičku CSV (základní údaje + názvy všech stran)
    all_keys = set()
    for row in data_rows:
        all_keys.update(row.keys())
    hlavicka = ["Kód obce", "Název obce", "Voliči v seznamu", "Vydané obálky", "Platné hlasy"] + \
        [k for k in all_keys if k not in ("Kód obce", "Název obce", "Voliči v seznamu", "Vydané obálky", "Platné hlasy")]

    # zápis do CSV souboru
    with open(vystup, "w", newline="", encoding="utf-8") as f:
        zapisovac = csv.DictWriter(f, fieldnames=hlavicka)
        zapisovac.writeheader()     # zapíše hlavičku
        zapisovac.writerows(data_rows)  # zapíše všechny obce

    print(f"Hotovo! Data uložená do {vystup}")


if __name__ == "__main__":
    main()  # spustí hlavní funkci
