import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
from typing import Optional
from concurrent.futures import ThreadPoolExecutor


REQUEST_TIMEOUT = 15
MAX_WORKERS = 15


def _make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (compatible; designazioni-viewer/1.0)"
    })
    return session


def _fetch_url(session: requests.Session, url: str) -> bytes:
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
    resolved = urljoin(category_url, href)

    parsed_base = urlparse(base_url)
    base_path = parsed_base.path
    if base_path.endswith('/'):
        base_dir = base_path
    else:
        last_segment = base_path.rsplit('/', 1)[-1]
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


def _parse_girone(category_name: str, content: bytes, sezione: str, match_date: Optional[str] = None) -> list[dict]:
    """Estrae le designazioni filtrate per sezione da una pagina girone."""
    soup = BeautifulSoup(content, 'lxml')

    header = soup.select_one('h3')
    date = _get_date_from_title(header.get_text(strip=True) if header else "")

    tbody = soup.select_one('tbody')
    matches = tbody.select('tr') if tbody else [
        tr for tr in soup.select('tr')
        if 'table-header-designazioni' not in (tr.get('class') or [])
    ]

    headers_th = soup.select('th')
    results = []

    for match in matches:
        fields = match.select('td')
        if len(fields) < 3:
            continue
        squadra1 = fields[0].get_text(strip=True)
        squadra2 = fields[1].get_text(strip=True)
        for i in range(2, len(fields)):
            nome, sez = _extract_nome_sezione(fields[i])
            if sez != sezione:
                continue
            ruolo = headers_th[i - 1].get_text(strip=True) if len(headers_th) > i - 1 else "N/D"
            results.append({
                "categoria": category_name,
                "squadra1": squadra1,
                "squadra2": squadra2,
                "nome": nome,
                "sezione": sez,
                "ruolo": ruolo,
                "data": date,
            })

    return results


def scrape(base_url: str, sezione: str = "Faenza") -> dict:
    """
    Esegue lo scraping del sito AIA-FIGC a partire da base_url.
    Restituisce {"results": [...], "errors": [...]}.
    Le richieste HTTP ai livelli 2 e 3 vengono eseguite in parallelo.
    """
    results = []
    errors = []
    session = _make_session()

    # Normalizza: directory senza trailing slash → aggiunge /
    parsed_tmp = urlparse(base_url)
    last_seg = parsed_tmp.path.rstrip('/').rsplit('/', 1)[-1]
    if '.' not in last_seg and not base_url.endswith('/'):
        base_url = base_url + '/'

    # --- Livello 1: pagina principale ---
    try:
        main_content = _fetch_url(session, base_url)
    except Exception as e:
        return {"results": [], "errors": [str(e)]}

    soup = BeautifulSoup(main_content, 'lxml')

    categories_table = None
    for table in soup.select('table'):
        th = table.find('th')
        if th and th.get_text(strip=True) == 'Categorie':
            categories_table = table
            break

    if not categories_table:
        return {"results": [], "errors": ["Tabella 'Categorie' non trovata. Verifica l'URL inserito."]}

    categories = categories_table.select('td.table-col-double')
    if not categories:
        return {"results": [], "errors": ["Nessuna categoria trovata nella pagina."]}

    # --- Livello 2: fetch pagine categoria in parallelo ---
    def fetch_category(category):
        a = category.select_one('a[href]')
        if not a:
            return None
        name = a.get_text(strip=True)
        url_cat = urljoin(base_url, a['href'])
        try:
            content = _fetch_url(session, url_cat)
            return (name, url_cat, content, None)
        except Exception as e:
            return (name, url_cat, None, str(e))

    cat_data = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for r in executor.map(fetch_category, categories):
            if r is None:
                continue
            name, url_cat, content, err = r
            if err:
                errors.append(f"[{name}] {err}")
            else:
                cat_data.append((name, url_cat, content))

    # Costruisce la lista di tutti i gironi da fetchare
    girone_tasks = []  # (category_name, round_url)
    for name, url_cat, content in cat_data:
        soup2 = BeautifulSoup(content, 'lxml')
        for ga in soup2.select('td a[href]'):
            round_url = _resolve_round_url(base_url, url_cat, ga['href'])
            girone_tasks.append((name, round_url))

    # --- Livello 3: fetch pagine girone in parallelo ---
    def fetch_girone(task):
        name, round_url = task
        try:
            content = _fetch_url(session, round_url)
            return (name, content, None)
        except Exception as e:
            return (name, None, str(e))

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for task, r in zip(girone_tasks, executor.map(fetch_girone, girone_tasks)):
            name, content, err = r
            if err:
                errors.append(f"[{task[0]}] {err}")
                continue
            results.extend(_parse_girone(name, content, sezione))

    return {"results": results, "errors": errors}
