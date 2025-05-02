"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie
author: Vendulka Hrubá
email: vendys.hruba@seznam.cz
discord: Vendy H. (vendy_72847)
"""

import requests                 # umožnění stahování obsahu webových stránek
import sys                      # umožnění práce s příkazovou řádkou
import csv                      # umožnění práce se soubory typu CSV
from bs4 import BeautifulSoup   # umožnění parsingu HTML – tedy rozboru a „čtení“ obsahu webových stránek.


def zkontroluj_argumenty():
    """
    Načte a zkontroluje vstupní argumenty.

    Vrací:
        url (str): Ověřená URL adresa se seznamem obcí.
        vystup (str): Název výstupního CSV souboru.
    """

    # Kontrola celkového počtu argumentů
    if len(sys.argv) != 3: # POZN.: sys.argv[0] je název souboru (projekt_3.py)
        print("Chybný počet vstupních argumentů. Použití:")
        print("python projekt_3.py <url> <vystupni_soubor.csv>")
        sys.exit(1)

    # Uložení jednotlivých argumentů
    url = sys.argv[1]
    vystup = sys.argv[2]

    # Kontrola správného formátu URL
    if not url.startswith("https://www.volby.cz/pls/ps2017nss/ps3"):
        print("URL musí začínat https://www.volby.cz/pls/ps2017nss/ps3")
        sys.exit(1)

    # Kontrola správného formátu .cscv
    if not vystup.endswith(".csv"):
        print("Výstupní soubor musí mít příponu .csv")
        sys.exit(1)

    # Kontrola dostupnosti URL
    try:
        if requests.get(url).status_code != 200:
            print("URL není dostupné.")
            sys.exit(1)
    except requests.RequestException as e:
        print(f"Chyba při ověřování URL: {e}")
        sys.exit(1)

    return url, vystup


def nacti_html(url):
    """
    Načte a vrátí HTML obsah stránky jako objekt BeautifulSoup.

    Vrací:
        BeautifulSoup: Objekt pro práci s HTML.
        None: Pokud dojde k chybě při požadavku.
    """
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    except requests.RequestException as e:
        print(f"Chyba při načítání stránky: {url}")
        print(e)
        return None


def ziskej_obce_ze_stranky(soup):
    """
    Získá ze zadaného BeautifulSoup objektu (HTML stránky) seznam obcí včetně jejich čísel, názvů a odkazů na výběr okrsku.

    Vrací:
        list: Seznam slovníků s klíči 'cislo', 'nazev' a 'odkaz'.
    """
    obce = []
    for tr in soup.find_all('tr'):
        td = tr.find_all('td')
        if len(td) == 3:
            cislo = td[0].text.strip()
            nazev = td[1].text.strip()
            odkaz = td[2].find('a')
            if odkaz and 'href' in odkaz.attrs:
                href = odkaz['href']
                obce.append({
                    'cislo': cislo,
                    'nazev': nazev,
                    'odkaz': f'https://www.volby.cz/pls/ps2017nss/{href}'
                })
    return obce


def ziskej_vysledky_z_obce(obec_url):
    """
    Načte stránku jedné obce a získá volební výsledky.

    Vrací:
        dict: Slovník s údaji o počtu voličů, vydaných obálkách,
              platných hlasech a hlasech pro jednotlivé strany.
        None: Pokud se stránka nepodaří načíst.
    """
    soup = nacti_html(obec_url)
    if soup is None:
        return None

    vysledky = {
        "volici_v_seznamu": "0",
        "vydane_obalky": "0",
        "platne_hlasy": "0",
        "strany": {}
    }

    tabulka_stat = soup.find('table', {"id": "ps311_t1"})
    if tabulka_stat:
        radky = tabulka_stat.find_all("tr")
        for radek in radky:
            bunky = radek.find_all("td")
            if len(bunky) >= 2:
                nazev = bunky[0].text.strip()
                hodnota = bunky[1].text.strip().replace('\xa0', '').replace(' ', '')
                if "Voliči v seznamu" in nazev:
                    vysledky["volici_v_seznamu"] = hodnota
                elif "Vydané obálky" in nazev:
                    vysledky["vydane_obalky"] = hodnota
                elif "Platné hlasy" in nazev:
                    vysledky["platne_hlasy"] = hodnota

    tabulky = soup.find_all("table", {"class": "table"})[1:]
    for tabulka in tabulky:
        for radek in tabulka.find_all("tr"):
            bunky = radek.find_all("td")
            if len(bunky) >= 3:
                nazev_strany = bunky[1].text.strip()
                hlasy = bunky[2].text.strip().replace('\xa0', '').replace(' ', '')
                vysledky["strany"][nazev_strany] = hlasy

    return vysledky


def zapis_do_csv(obce, vysledky_dict, vystup):
    """
    Zapíše volební výsledky do CSV souboru.

    Výstup:
        Vytvoří CSV soubor, kde každý řádek odpovídá jedné obci a sloupce obsahují
        základní údaje a počet hlasů pro každou politickou stranu.
    """
    vsechny_strany = set()
    for vysledky in vysledky_dict.values():
        vsechny_strany.update(vysledky["strany"].keys())
    vsechny_strany = sorted(vsechny_strany)

    hlavicka = [
        "kód obce",
        "název obce",
        "voliči v seznamu",
        "vydané obálky",
        "platné hlasy"
    ] + vsechny_strany

    with open(vystup, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(hlavicka)

        for obec in obce:
            vysledky = vysledky_dict.get(obec['cislo'], {})
            if not vysledky:
                continue
            radek = [
                obec['cislo'],
                obec['nazev'],
                vysledky["volici_v_seznamu"],
                vysledky["vydane_obalky"],
                vysledky["platne_hlasy"]
            ]
            for strana in vsechny_strany:
                radek.append(vysledky["strany"].get(strana, "0"))
            writer.writerow(radek)


def main():
    """
    Hlavní řídicí funkce programu.

    Postupně:
    1. Získá a zkontroluje argumenty z příkazové řádky (URL + výstupní soubor).
    2. Načte HTML stránku se seznamem obcí.
    3. Získá odkazy na detailní stránky jednotlivých obcí.
    4. Pro každou obec stáhne volební výsledky.
    5. Výsledky uloží do CSV souboru.

    Výstup:
        Vytvořený CSV soubor s volebními výsledky podle zadané URL.
    """
    url, vystup = zkontroluj_argumenty()
    soup = nacti_html(url)
    obce = ziskej_obce_ze_stranky(soup)
    vysledky_dict = {}

    print(f"Zjišťuji výsledky pro {len(obce)} obcí...")
    for obec in obce:
        print(f"Zpracovávám obec: {obec['nazev']}")
        vysledky = ziskej_vysledky_z_obce(obec['odkaz'])
        if vysledky:
            vysledky_dict[obec['cislo']] = vysledky

    zapis_do_csv(obce, vysledky_dict, vystup)
    print(f"Hotovo! Data byla uložena do {vystup}")


if __name__ == "__main__":
    main()