import requests
import sys
import csv
from bs4 import BeautifulSoup

def zkontroluj_argumenty():
    if len(sys.argv) != 3:
        print("[0] Chybný počet vstupních argumentů. Použití:")
        print("python main.py <url> <vystupni_soubor.csv>")
        sys.exit(1)

    url = sys.argv[1]
    vystup = sys.argv[2]

    if not url.startswith("https://www.volby.cz/pls/ps2017nss/ps3"):
        print("[1] URL musi zacinat https://www.volby.cz/pls/ps2017nss/ps3")
        sys.exit(1)

    if not vystup.endswith(".csv"):
        print("[2] Vystupni soubor musi mit priponu .csv")
        sys.exit(1)

    try:
        if requests.get(url).status_code != 200:
            print("[3] URL neni dostupne.")
            sys.exit(1)
    except requests.RequestException as e:
        print(f"[4] Chyba pri overovani URL: {e}")
        sys.exit(1)

    print("[5] Argumenty OK")
    return url, vystup

def nacti_html(url):
    try:
        response = requests.get(url)
        return BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        print(f"[6] Chyba pri nacitani stranky: {url}")
        print(e)
        return None

def ziskej_seznam_obci(soup):
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
    print(f"[6a] Nacteno {len(obce)} obci ze seznamu.")
    return obce

def ziskej_vysledky(obec_url):
    soup = nacti_html(obec_url)
    if soup is None:
        return None

    vysledky = {
        "volici_v_seznamu": "0",
        "vydane_obalky": "0",
        "platne_hlasy": "0",
        "strany": {}
    }

    try:
        prvni_tabulka = soup.find_all("table", class_="table")[0]
        radky = prvni_tabulka.find_all("tr")
        for radek in radky:
            bunky = radek.find_all("td")

            if prvni_tabulka.has_attr("id") and prvni_tabulka["id"] == "ps311_t1" and len(bunky) == 9:
                hodnoty = [td.text.strip().replace('\xa0', '').replace(' ', '') for td in bunky]
                vysledky["volici_v_seznamu"] = hodnoty[3]
                vysledky["vydane_obalky"] = hodnoty[4]
                vysledky["platne_hlasy"] = hodnoty[7]
                break

            elif not prvni_tabulka.has_attr("id") and len(bunky) == 6:
                hodnoty = [td.text.strip().replace('\xa0', '').replace(' ', '') for td in bunky]
                vysledky["volici_v_seznamu"] = hodnoty[0]
                vysledky["vydane_obalky"] = hodnoty[1]
                vysledky["platne_hlasy"] = hodnoty[4]
                break
    except (IndexError, AttributeError):
        print("[DEBUG] Statisticka tabulka nebyla nalezena nebo ma necekavanou strukturu.")

    tabulky = soup.find_all("table", class_="table")[1:]
    for tabulka in tabulky:
        for radek in tabulka.find_all("tr"):
            bunky = radek.find_all("td")
            if len(bunky) >= 3:
                posledni_bunka = bunky[-1]
                if posledni_bunka.find("a"):  # kontrola existence odkazu
                    nazev_strany = bunky[1].text.strip()
                    hlasy = bunky[2].text.strip().replace('\xa0', '').replace(' ', '')
                    vysledky["strany"][nazev_strany] = hlasy

    return vysledky

def ziskej_soucet_vysledku_z_okrsku(obec_url):
    soup = nacti_html(obec_url)
    if soup is None:
        return None

    odkazy = []
    for td in soup.find_all("td"):
        a_tag = td.find("a")
        if a_tag and "href" in a_tag.attrs:
            href = a_tag["href"]
            if href.startswith("ps311"):
                url = f'https://www.volby.cz/pls/ps2017nss/{href}'
                if url not in odkazy:
                    odkazy.append(url)

    print(f"[DEBUG] Nalezeno {len(odkazy)} okrskovych odkazu.")

    souhrn = {
        "volici_v_seznamu": 0,
        "vydane_obalky": 0,
        "platne_hlasy": 0,
        "strany": {}
    }

    for idx, odkaz in enumerate(odkazy, start=1):
        print(f"[DEBUG] ({idx}/{len(odkazy)}) Zpracovavam okrsek: {odkaz}")
        vysledky = ziskej_vysledky(odkaz)
        # print(f"[DEBUG] Nactene hodnoty z okrsku: {vysledky}")
        if not vysledky:
            continue

        souhrn["volici_v_seznamu"] += int(vysledky["volici_v_seznamu"])
        souhrn["vydane_obalky"] += int(vysledky["vydane_obalky"])
        souhrn["platne_hlasy"] += int(vysledky["platne_hlasy"])
        # print(f"[DEBUG] Souhrn zatim: volici={souhrn['volici_v_seznamu']}, obalky={souhrn['vydane_obalky']}, platne={souhrn['platne_hlasy']}")

        for strana, hlasy in vysledky["strany"].items():
            souhrn["strany"][strana] = souhrn["strany"].get(strana, 0) + int(hlasy)

    souhrn["volici_v_seznamu"] = str(souhrn["volici_v_seznamu"])
    souhrn["vydane_obalky"] = str(souhrn["vydane_obalky"])
    souhrn["platne_hlasy"] = str(souhrn["platne_hlasy"])
    for k in souhrn["strany"]:
        souhrn["strany"][k] = str(souhrn["strany"][k])

    return souhrn

def zapis_do_csv(obce, vysledky_dict, vystup):
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

    with open(vystup, mode='w', newline='', encoding='utf-8-sig') as csvfile:
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
    print("[1] Spoustim hlavni program")
    url, vystup = zkontroluj_argumenty()
    soup = nacti_html(url)
    obce = ziskej_seznam_obci(soup)
    vysledky_dict = {}

    print(f"[7] Zjistuji vysledky pro {len(obce)} obci...")
    for index, obec in enumerate(obce, start=1):
        print(f"[8.{index}] Zpracuji obec: {obec['nazev']}")
        try:
            soup_obce = nacti_html(obec['odkaz'])
            if not soup_obce:
                continue
            title_tag = soup_obce.find("title")
            if title_tag and "výběr okrsku" in title_tag.text:
                print(f"[9.{index}] Detekovan vyber okrsku")
                vysledky = ziskej_soucet_vysledku_z_okrsku(obec['odkaz'])
            else:
                print(f"[9.{index}] Detekovana stranka s primymi vysledky")
                vysledky = ziskej_vysledky(obec['odkaz'])
            if vysledky:
                print(f"[11.{index}] Vysledky nacteny")
                vysledky_dict[obec['cislo']] = vysledky
            else:
                print(f"[12.{index}] Vysledky nebyly nacteny")
        except Exception as e:
            print(f"[10.{index}] Chyba pri zpracovani obce {obec['nazev']}: {e}")

    print("[13] Zapisuji do CSV souboru...")
    zapis_do_csv(obce, vysledky_dict, vystup)
    print(f"[14] Hotovo! Data byla ulozena do {vystup}")

if __name__ == "__main__":
    main()