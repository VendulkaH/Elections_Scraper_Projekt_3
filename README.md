# Election Scraper

Třetí projekt v rámci Python Akademie od Engeta.

## Popis projektu

Tento projekt je scraper volebních výsledků z roku 2017 v ČR. Program stáhne data z webu [volby.cz](https://volby.cz), extrahuje informace o jednotlivých obcích a jejich volebních výsledcích a následně ukládá data do CSV souboru.

## Spuštění projektu

### Požadavky
- Python 3.12
- Knihovny uvedené v `requirements.txt`

### Instalace
1. Vytvořte a aktivujte virtuální prostředí:
   ```bash
   python -m venv venv # vytvoření virtuálního prostředí
   venv\Scripts\activate  # aktivace virtuálního prostředí
   ```
2. Nainstalujte požadované balíčky:
   ```bash
   pip install -r requirements.txt
   ```

### Spuštění skriptu
Skript se spouští z příkazové řádky a požaduje dva povinné argumenty:
```bash
python main.py <URL_uzemniho_celku> <vystupni_soubor.csv>
```

#### Příklad použití:
```bash
Visual Studio Code:
(venv) PS C:\Users\vendy\Desktop\ENGETO\Elections_Scraper_Projekt_3> python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2112" vysledky_rakovnik.csv
[1] Spoustim hlavni program
[5] Argumenty OK
[6a] Nacteno 83 obci ze seznamu.
[7] Zjistuji vysledky pro 83 obci...
[8.1] Zpracuji obec: Bdín
[9.1] Detekovana stranka s primymi vysledky
[11.1] Vysledky nacteny
...
[11.81] Vysledky nacteny
[8.82] Zpracuji obec: Zbečno
[9.82] Detekovan vyber okrsku
[DEBUG] Nalezeno 2 okrskovych odkazu.
[DEBUG] (1/2) Zpracovavam okrsek: https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj=2&xobec=542610&xokrsek=1&xvyber=2112
[DEBUG] (2/2) Zpracovavam okrsek: https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj=2&xobec=542610&xokrsek=2&xvyber=2112
[11.82] Vysledky nacteny
[8.83] Zpracuji obec: Žďár
[9.83] Detekovana stranka s primymi vysledky
[11.83] Vysledky nacteny
[13] Zapisuji do CSV souboru...
[14] Hotovo! Data byla ulozena do vysledky_rakovnik.csv
```
Tento příkaz stáhne výsledky pro okres Rakovník a uloží je do `vysledky_rakovnik.csv`.

## Ukázka výstupního CSV souboru
| Číslo obce | Název obce | Voliči v seznamu | Vydané obálky | Platné hlasy | ANO 2011 | Blok proti islam.-Obran.domova | CESTA ODPOVĚDNÉ SPOLEČNOSTI |
|------------|------------|------------------|----------------|----------------|----------|-------------------------------|------------------------------|
| 565423     | Bdín       | 51               | 34             | 34             | 15       | 0                             | 0                            |
| 541672     | Branov     | 170              | 120            | 119            | 40       | 0                             | 0                            |
| 565041     | Břežany    | 106              | 71             | 69             | 20       | 0                             | 0                            |
| 541699     | Čistá      | 724              | 388            | 387            | 114      | 0                             | 0                            |
| 565181     | Děkov      | 160              | 63             | 63             | 10       | 0                             | 0                            |
| 529711     | Drahouš    | 64               | 41             | 41             | 17       | 1                             | 0                            |
