import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin, urlparse, parse_qs
import sys
import time

BASE_URL = "https://www.volby.cz/pls/ps2017nss/"

def get_soup(url):
    resp = requests.get(url)
    resp.encoding = "utf-8"
    return BeautifulSoup(resp.text, "html.parser")

def parse_obec(url, nazev_obce):
    soup = get_soup(url)
    kod_obce = parse_qs(urlparse(url).query).get("xobec", ["N/A"])[0]
    def safe_find(headers):
        td = soup.find("td", {"headers": headers})
        return td.text.strip() if td else ""
    volici = safe_find("sa2")
    obalky = safe_find("sa3")
    platne = safe_find("sa6")
   
   # Strany a hlasy 
    # všechny názvy stran (v obou tabulkách)
    strany = [td.text.strip() for td in soup.find_all("td", class_="overflow_name")]

    # všechny počty hlasů (v obou tabulkách)
    hlasy = [td.text.strip() for td in soup.find_all("td", headers=lambda h: h and h.endswith("sb3"))]

    
    data = {
        "Kód obce": kod_obce,
        "Název obce": nazev_obce,
        "Voliči v seznamu": volici,
        "Vydané obálky": obalky,
        "Platné hlasy": platne,
    }
    for s, h in zip(strany, hlasy):
        data[s] = h
    return data

def main():
    if len(sys.argv) != 3:
        print("Použití: python main.py <URL_OKRESU> <vystup.csv>")
        sys.exit(1)
    url_okres = sys.argv[1]
    vystup = sys.argv[2]
    soup = get_soup(url_okres)
    tabulky = soup.find_all("table", class_="table")
    obec_links = []
    for tabulka in tabulky:
        for tr in tabulka.find_all("tr"):
            cislo_td = tr.find("td", class_="cislo")
            nazev_td = tr.find("td", class_="overflow_name")
            if cislo_td and nazev_td:
                a = cislo_td.find("a", href=True)
                if a and "xobec=" in a["href"]:
                    url = urljoin(BASE_URL, a["href"])
                    nazev_obce = nazev_td.text.strip()
                    obec_links.append((url, nazev_obce))
    obec_links = list(dict.fromkeys(obec_links))
    print(f"Nalezeno obcí: {len(obec_links)}")
    data_rows = []
    for idx, (url, nazev_obce) in enumerate(obec_links[:3], 1):  # [:3] = jen první 3 obce
        print(f"Zpracovávám obec {idx}/{len(obec_links)}... {nazev_obce}")
        obec_data = parse_obec(url, nazev_obce)
        data_rows.append(obec_data)
        time.sleep(1)  # pauza mezi požadavky

    all_keys = set()
    for row in data_rows:
        all_keys.update(row.keys())
    hlavicka = ["Kód obce", "Název obce", "Voliči v seznamu", "Vydané obálky", "Platné hlasy"] + \
        [k for k in all_keys if k not in ("Kód obce", "Název obce", "Voliči v seznamu", "Vydané obálky", "Platné hlasy")]
    with open(vystup, "w", newline="", encoding="utf-8") as f:
        zapisovac = csv.DictWriter(f, fieldnames=hlavicka)
        zapisovac.writeheader()
        zapisovac.writerows(data_rows)
    print(f"Hotovo! Data uložená do {vystup}")

if __name__ == "__main__":
    main()

    # python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101" vysledky.csv
