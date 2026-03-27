import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
from typing import Optional


REQUEST_TIMEOUT = 15


def _make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (compatible; designazioni-viewer/1.0)"
    })
    return session


def _fetch_url(session: requests.Session, url: str) -> Optional[bytes]:
    try:
        resp = session.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.content
    except requests.exceptions.Timeout:
        raise TimeoutError(f"Timeout raggiunto per: {url}")
    except requests.exceptions.HTTPError as e:
        raise ConnectionError(f"HTTP {e.response.status_code} per: {url}")
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Errore di rete per {url}: {e}")


def _extract_nome_sezione(cell) -> tuple[str, str]:
    if cell is None:
        return "", ""
    try:
        nome = str(cell.contents[0]).strip() if cell.contents else cell.get_text(strip=True).split('\n')[0].strip()
    except Exception:
        nome = cell.get_text(strip=True).split('\n')[0].strip()
    sez_div = cell.find('div', class_='designazione-sezione')
    sezione = sez_div.get_text(strip=True) if sez_div else ""
    return nome, sezione


def _resolve_round_url(base_url: str, category_url: str, href: str) -> str:
    """
    Risolve l'href del girone contro category_url.
    Se il risultato cade fuori dalla directory regionale di base_url,
    forza il filename dentro quella directory (es. OTR con URL regionale).
    """
    resolved = urljoin(category_url, href)

    parsed_base = urlparse(base_url)
    # directory base: es. /designazioni/emiliaromagna/
    base_path = parsed_base.path
    if base_path.endswith('/'):
        base_dir = base_path
    else:
        last_segment = base_path.rsplit('/', 1)[-1]
        # Se l'ultimo segmento non ha estensione è una directory (es. "emiliaromagna")
        if '.' not in last_segment:
            base_dir = base_path + '/'
        else:
            base_dir = base_path.rsplit('/', 1)[0] + '/'

    parsed_resolved = urlparse(resolved)
    if not parsed_resolved.path.startswith(base_dir):
        parsed_href = urlparse(href)
        filename = parsed_href.path.rsplit('/', 1)[-1]
        query = parsed_href.query or parsed_resolved.query
        fixed_path = base_dir + filename
        resolved = parsed_base._replace(path=fixed_path, query=query, fragment='').geturl()

    return resolved


def _get_date_from_title(title_text: str) -> Optional[str]:
    if not title_text:
        return None
    last_token = title_text.strip().split()[-1]
    for fmt in ("%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(last_token, fmt).strftime("%d/%m/%Y")
        except ValueError:
            continue
    return None


def scrape(base_url: str, sezione: str = "Faenza") -> dict:
    """
    Esegue lo scraping del sito AIA-FIGC a partire da base_url.
    Restituisce {"results": [...], "errors": [...]}.
    """
    results = []
    errors = []
    session = _make_session()

    # Normalizza: se l'ultimo segmento non ha estensione è una directory → aggiungi /
    parsed_tmp = urlparse(base_url)
    last_seg = parsed_tmp.path.rstrip('/').rsplit('/', 1)[-1]
    if '.' not in last_seg and not base_url.endswith('/'):
        base_url = base_url + '/'

    try:
        main_content = _fetch_url(session, base_url)
    except Exception as e:
        errors.append(str(e))
        return {"results": results, "errors": errors}

    soup = BeautifulSoup(main_content, 'html.parser')

    # Trova tabella Categorie
    categories_table = None
    for table in soup.select('table'):
        th = table.find('th')
        if th and th.get_text(strip=True) == 'Categorie':
            categories_table = table
            break

    if not categories_table:
        errors.append("Tabella 'Categorie' non trovata. Verifica l'URL inserito.")
        return {"results": results, "errors": errors}

    categories = categories_table.select('td.table-col-double')
    if not categories:
        errors.append("Nessuna categoria trovata nella pagina.")
        return {"results": results, "errors": errors}

    for category in categories:
        a = category.select_one('a[href]')
        if not a:
            continue
        category_name = a.get_text(strip=True)
        url_cat = urljoin(base_url, a['href'])

        try:
            cat_content = _fetch_url(session, url_cat)
        except Exception as e:
            errors.append(f"[{category_name}] {e}")
            continue

        soup2 = BeautifulSoup(cat_content, 'html.parser')
        group_anchors = soup2.select('td a[href]')
        if not group_anchors:
            continue

        for ga in group_anchors:
            round_url = _resolve_round_url(base_url, url_cat, ga['href'])
            try:
                round_content = _fetch_url(session, round_url)
            except Exception as e:
                errors.append(f"[{category_name}] Girone: {e}")
                continue

            soup3 = BeautifulSoup(round_content, 'html.parser')

            header = soup3.select_one('h3')
            header_text = header.get_text(strip=True) if header else ""
            match_date = _get_date_from_title(header_text)

            tbody = soup3.select_one('tbody')
            if tbody:
                matches = tbody.select('tr')
            else:
                all_trs = soup3.select('tr')
                matches = [tr for tr in all_trs if 'table-header-designazioni' not in (tr.get('class') or [])]

            if not matches:
                continue

            headers_th = soup3.select('th')

            for match in matches:
                fields = match.select('td')
                if len(fields) < 3:
                    continue

                squadra1 = fields[0].get_text(strip=True)
                squadra2 = fields[1].get_text(strip=True)

                for i in range(2, len(fields)):
                    name, sez = _extract_nome_sezione(fields[i])
                    ruolo = headers_th[i - 1].get_text(strip=True) if len(headers_th) > i - 1 else "N/D"

                    if sez == sezione:
                        results.append({
                            "categoria": category_name,
                            "squadra1": squadra1,
                            "squadra2": squadra2,
                            "nome": name,
                            "sezione": sez,
                            "ruolo": ruolo,
                            "data": match_date,
                        })

    return {"results": results, "errors": errors}
