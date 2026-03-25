import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from functools import lru_cache
from datetime import datetime

# ---------------------------------------------------------
# SCRAPER DESIGNAZIONI UN SINGOLO LINK PER VOLTA DA MODIFICARE MANUALMENTE IN BASE_URL
# ---------------------------------------------------------


session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (compatible; aio-scraper/1.0; +https://example.local/)"
})
REQUEST_TIMEOUT = 10

# Cache semplice sulle richieste (memorizza il contenuto per URL)
@lru_cache(maxsize=512)
def fetch_url(url: str) -> bytes:
    """
    Recupera il contenuto della pagina come bytes e lo cachea.
    """
    resp = session.get(url, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.content

# ---------------------------------------------------------
# Funzioni di utilità
# ---------------------------------------------------------
def extract_nome_sezione(cell):
    """
    Estrae il nome e la sezione da una cella <td>.
    """
    if cell is None:
        return "", ""
    # Se il nodo ha children testuali, prendo il primo
    try:
        if cell.contents:
            nome = str(cell.contents[0]).strip()
        else:
            nome = cell.get_text(strip=True).split('\n')[0].strip()
    except Exception:
        nome = cell.get_text(strip=True).split('\n')[0].strip()
    sez_div = cell.find('div', class_='designazione-sezione')
    sezione = sez_div.get_text(strip=True) if sez_div else ""
    return nome, sezione

def get_date_from_title(title_text: str):
    """
    Estrae l'ultima parola del titolo e prova a convertirla in data (dd/mm/YYYY o dd-mm-YYYY).
    """
    if not title_text:
        return None
    last_token = title_text.strip().split()[-1]
    for fmt in ("%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(last_token, fmt).date()
        except ValueError:
            continue
    return None

# ---------------------------------------------------------
# Scraper ottimizzato
# ---------------------------------------------------------
def scrape_aia_figc():
    #base_url = "https://www.aia-figc.it/designazioni/emiliaromagna/"
    base_url = "https://www.aia-figc.it/designazioni/emiliaromagna/default.asp?gare=4-117"
    #base_url = "https://www.aia-figc.it/designazioni/canc/"
    #base_url = "https://www.aia-figc.it/designazioni/cand/"
    

    results = []

    try:
        main_html = fetch_url(base_url)
        soup = BeautifulSoup(main_html, 'html.parser')

        # Trova la tabella con intestazione "Categorie"
        categories_table = None
        for table in soup.select('table'):
            th = table.find('th')
            if th and th.get_text(strip=True) == 'Categorie':
                categories_table = table
                break

        if not categories_table:
            print("Tabella con intestazione 'Categorie' non trovata. Interrompo lo scraping.")
            return results

        # Prendo direttamente i td con classe table-col-double
        categories = categories_table.select('td.table-col-double')
        if not categories:
            print("Non esistono designazioni per alcuna categoria.")
            return results

        # Livello 2: itero sui link trovati nei box delle categorie
        for category in categories:
            a = category.select_one('a[href]')
            if not a:
                continue
            category_href = a['href']
            url_specific_category = urljoin(base_url, category_href)
            try:
                cat_html = fetch_url(url_specific_category)
            except Exception:
                # se la pagina non è raggiungibile, salto la categoria
                continue

            soup2 = BeautifulSoup(cat_html, 'html.parser')

            # Prendo direttamente gli anchor dentro i td (riduce parsing)
            group_anchors = soup2.select('td a[href]')
            if not group_anchors:
                # se non ci sono anchor, salto
                continue

            # Livello 3: itero sui link dei gironi
            for ga in group_anchors:
                group_href = ga['href']
                round_url = urljoin(url_specific_category, group_href)
                try:
                    round_html = fetch_url(round_url)
                except Exception:
                    continue

                soup3 = BeautifulSoup(round_html, 'html.parser')

                # Estrazione veloce della intestazione con data (h1/h2/h3)
                header = soup3.select_one('h3')
                header_text = header.get_text(strip=True) if header else ""
                match_date = get_date_from_title(header_text)

                # Trovo le righe delle partite: preferisco tbody se presente
                tbody = soup3.select_one('tbody')
                if tbody:
                    matches = tbody.select('tr')
                else:
                    # prendo tutti i tr e scarto quelli con classe table-header-designazioni
                    all_trs = soup3.select('tr')
                    matches = [tr for tr in all_trs if 'table-header-designazioni' not in (tr.get('class') or [])]

                if not matches:
                    continue

                # Prendo le intestazioni (th) una sola volta per la pagina
                matches_header_data = soup3.select('th')

                # Estraggo dati per ogni partita
                for match in matches:
                    match_fields = match.select('td')
                    if len(match_fields) < 3:
                        continue

                    squadra1 = match_fields[0].get_text(strip=True)
                    squadra2 = match_fields[1].get_text(strip=True)

                    # colonne successive contengono i nomi/ruoli
                    for i in range(2, len(match_fields)):
                        name_td = match_fields[i]
                        name, sez = extract_nome_sezione(name_td)
                        ruolo = matches_header_data[i-1].get_text(strip=True) if len(matches_header_data) > i-1 else None

                        # Mantengo la stessa condizione logica del tuo script originale
                        if sez == "Faenza":
                            results.append({
                                'categoria': a.get_text(strip=True),
                                'squadra1': squadra1,
                                'squadra2': squadra2,
                                'nome': name,
                                'sezione': sez,
                                'ruolo': ruolo,
                                'data': match_date.strftime("%d/%m/%Y") if match_date else None
                            })

    except Exception as e:
        # Errore generale: stampo il messaggio e ritorno quanto raccolto fino a qui
        print(f"Errore durante l'accesso alla pagina principale: {e}")

    return results

# ---------------------------------------------------------
# Esecuzione e riepilogo finale (Opzione A: stampa riepilogo)
# ---------------------------------------------------------
if __name__ == "__main__":
    dati_estratti = scrape_aia_figc()

    print("\n" + "="*60)
    print("RIEPILOGO DATI ESTRATTI")
    print("="*60)

    if dati_estratti:
        for i, dato in enumerate(dati_estratti, 1):
            print(f"\n  ⚽ {dato['categoria']} ⚽")
            print(f"  {dato['data']}")
            print(f"  {dato['squadra1']} - {dato['squadra2']}")
            print(f"  {dato['ruolo']}: {dato['nome']}")
    else:
        print("\nNessun dato estratto.")

    print(f"\nTotale partite trovate: {len(dati_estratti)}")
