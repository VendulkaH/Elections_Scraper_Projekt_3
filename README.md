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
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate  # Windows
   ```
2. Nainstalujte požadované balíčky:
   ```bash
   pip install -r requirements.txt
   ```

### Spuštění skriptu
Skript se spouští z příkazové řádky a požaduje dva povinné argumenty:
```bash
python projekt_3.py <URL_uzemniho_celku> <vystupni_soubor.csv>
```

#### Příklad použití:
```bash
Příkazový řádek:
python projekt_3.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=3&xnumnuts=3101" "vysledky_adamov.csv"

Průběh stahování:
Zjišťuji výsledky pro 109 obcí...
Zpracovávám obec: Adamov
Zpracovávám obec: Bečice
...
Zpracovávám obec: Žimutice
Hotovo! Data byla uložena do vysledky_adamov.csv
```
Tento příkaz stáhne výsledky pro okres Adamov a uloží je do `vysledky_adamov.csv`.

POZN.: Problém s diakritikou byl vyřešen následovně: otevřít prázdný excel sešit -> Data -> Načíst externí data > Z textu/CSV (vybrat název souboru: vysledky_adamov.csv) -> nastav kódování na UTF-8 -> dokončit (uloženo jako vysledky_adamov (opravena diakritika)).

## Ukázka výstupního CSV souboru
| Číslo obce | Název obce | Voliči v seznamu | Vydané obálky | Platné hlasy | ANO 2011 | Blok proti islam.-Obran.domova | CESTA ODPOVĚDNÉ SPOLEČNOSTI |
|------------|-------------|-------------------|----------------|----------------|----------|-------------------------------|------------------------------|
| 535826     | Adamov      | 0                 | 0              | 0              | 126      | 0                             | 2                            |
| 536156     | Bečice      | 0                 | 0              | 0              | 17       | 0                             | 0                            |
| 544272     | Borek       | 0                 | 0              | 0              | 275      | 0                             | 3                            |
