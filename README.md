# Projekt_03 Engeto Academy: Analýza výsledků voleb do Poslanecké sněmovny 2017

Tento projekt slouží k **automatickému stažení a zpracování výsledků voleb do Poslanecké sněmovny 2017** z webu https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ
Skript stáhne data zadaného okresu, projde všechny obce v daném okrese a uloží výsledky do CSV souboru.

---

## Instalace ##

### 1. Klonování repozitáře
Naklonujte nebo stáhněte tento projekt do svého počítače.

### 2. Vytvoření a aktivace virtuálního prostředí v terminálu
Doporučený postup je spustit projekt v samostatném virtuálním prostředí:

python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows

### 3. Instalace závislostí
Projekt používá knihovny uvedené v requirements.txt.
Nainstalujte je pomocí:

pip install -r requirements.txt

V requirements.txt je zachyceno celé prostředí včetně verzí všech závislostí:

beautifulsoup4==4.13.5
certifi==2025.8.3
charset-normalizer==3.4.3
idna==3.10
numpy==2.3.2
python-dateutil==2.9.0.post0
pytz==2025.2
requests==2.32.5
six==1.17.0
soupsieve==2.8
typing_extensions==4.15.0
tzdata==2025.2
urllib3==2.5.0

### Použití
**Skript se spouští pomocí příkazové řádky se dvěma argumenty:**

1. URL okresu na stránce volby.cz

2. Název výstupního souboru (CSV)

*Příklad pro okres Benešov:*
python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101" vysledky.csv

### Ukázkový průběh v terminálu
Nalezeno obcí: 114
Zpracovávám obec 1/114... Benešov
Zpracovávám obec 2/114... Bernartice
Zpracovávám obec 3/114... Bílkovice
Zpracovávám obec 4/114... Blažejovice
...
Hotovo! Data uložená do vysledky.csv


### Ukázkový výstup v CSV
Pro okres Benešov skript stáhne data všech obcí a uloží je do CSV.
*Soubor může vypadat takto:*

| Kód obce | Název obce | Voliči v seznamu | Vydané obálky | Platné hlasy | Občanská demokratická strana | Řád národa - Vlastenecká unie | CESTA ODPOVĚDNÉ SPOLEČNOSTI | ... |
| -------- | ---------- | ---------------- | ------------- | ------------ | ---------------------------- | ----------------------------- | --------------------------- | --- |
| 529303   | Benešov    | 13 104           | 8 485         | 8 437        | 1 052                        | 10                            | 2                           | ... |
| 532568   | Bernartice | 191              | 148           | 148          | 4                            | 0                             | 40                          | ... |
| 530743   | Bílkovice  | 170              | 121           | 118          | 7                            | 0                             | 0                           | ... |
...


**Každý řádek odpovídá jedné obci a obsahuje:**
základní údaje (kód obce, název, počty voličů, obálek a platných hlasů), počty hlasů pro jednotlivé politické strany

### Očekávaný výstup

Výsledkem běhu skriptu je CSV soubor s přehlednými daty o volebních výsledcích pro všechny obce vybraného okresu. 
Tento soubor je možné dále analyzovat např. v Excelu, Pandas nebo vizualizačních nástrojích.






