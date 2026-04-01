# Designazioni Viewer

Web app per consultare le designazioni arbitrali AIA-FIGC filtrate per sezione, con possibilità di copiare i risultati formattati per la pubblicazione sui social.

## Indice

- [Funzionalità](#funzionalità)
- [Architettura](#architettura)
- [Tecnologie](#tecnologie)
- [Struttura del progetto](#struttura-del-progetto)
- [Installazione locale](#installazione-locale)
- [Deploy in produzione](#deploy-in-produzione)
- [Come funziona lo scraping](#come-funziona-lo-scraping)

---

## Funzionalità

- **Selezione regione e sezione** tramite menu a cascata (20 regioni, tutte le sezioni AIA)
- **Tipo di ricerca** selezionabile:
  - **OTS** — ricerca nella pagina della singola sezione
  - **OTR** — ricerca sull'intera pagina regionale, filtrata per sezione
  - **CAN C / CAN D** — ricerca nelle competizioni nazionali, filtrata per sezione
- **Visualizzazione** delle designazioni raggruppate per data, con scheda per ogni partita
- **Copia risultati** — genera un testo formattato (raggruppato per categoria e partita) pronto per essere incollato in un post sui social

---

## Architettura

```
Browser (React) ──POST /scrape──► FastAPI (Python) ──HTTP──► www.aia-figc.it
                 ◄── JSON ────────
```

Il browser non può contattare direttamente il sito AIA per via del CORS. Il backend FastAPI esegue lo scraping server-side e restituisce i dati al frontend come JSON.

---

## Tecnologie

### Backend
| Libreria | Ruolo |
|---|---|
| **FastAPI** | Framework REST API |
| **Uvicorn** | Server ASGI |
| **requests** | Esecuzione richieste HTTP verso il sito AIA |
| **BeautifulSoup4 + lxml** | Parsing HTML delle pagine di designazione |
| **Pydantic v2** | Validazione del body della richiesta |

### Frontend
| Libreria | Ruolo |
|---|---|
| **React 18** | UI component-based |
| **Vite** | Build tool e dev server |
| **Tailwind CSS** | Utility-first styling |

---

## Struttura del progetto

```
scraper-designazioni/
├── backend/
│   ├── main.py          # FastAPI: endpoint POST /scrape e GET /health
│   ├── scraper.py       # Logica di scraping (navigazione categorie → gironi → partite)
│   └── requirements.txt # Dipendenze Python
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── src/
│       ├── App.jsx                    # Componente root: stato, logica, layout
│       ├── main.jsx                   # Entry point React
│       ├── index.css                  # Stili globali Tailwind
│       ├── data/
│       │   └── regioni.js             # Dati statici: tutte le regioni e sezioni AIA con URL
│       ├── services/
│       │   └── scraperService.js      # Chiamata HTTP verso il backend
│       └── components/
│           ├── UrlSelector.jsx        # Form selezione regione / sezione / tipo ricerca
│           ├── MatchCard.jsx          # Scheda singola designazione
│           └── LoadingSpinner.jsx     # Indicatore di caricamento
└── README.md
```

---

## Installazione locale

### Prerequisiti

- Python 3.10+
- Node.js 18+
- npm

### 1. Clona il repository

```bash
git clone https://github.com/claudiufecheta/scraper-designazioni.git
cd scraper-designazioni
```

### 2. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Il backend sarà disponibile su `http://localhost:8000`.
Verifica con: `http://localhost:8000/health` → `{"status": "ok"}`

### 3. Frontend

In un secondo terminale:

```bash
cd frontend
cp .env.example .env.local        # crea il file delle variabili d'ambiente
# modifica .env.local e imposta VITE_API_BASE con l'URL del tuo backend
npm install
npm run dev
```

Il frontend sarà disponibile su `http://localhost:5173`.

Per lo sviluppo locale imposta:
```
VITE_API_BASE=http://localhost:8000
```

---

## Deploy in produzione

L'app è deployata gratuitamente su:

| Componente | Piattaforma | URL |
|---|---|---|
| Backend | [Render](https://render.com) | `https://designazioni-api.onrender.com` |
| Frontend | [Vercel](https://vercel.com) | `https://scraper-designazioni.vercel.app` |

Entrambi i servizi sono collegati al repository GitHub e si aggiornano automaticamente ad ogni push su `main`.

### Re-deploy manuale (se necessario)

**Backend su Render:**
- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Region: Frankfurt (EU Central)

**Frontend su Vercel:**
- Root directory: `frontend`
- Framework: Vite
- Build command: `npm run build`
- Output directory: `dist`

> **Attenzione sul free tier di Render**: il backend va in sleep dopo 15 minuti di inattività. La prima richiesta dopo una pausa impiega circa 30 secondi. Comportamento normale, nessuna azione richiesta.

---

## Come funziona lo scraping

La funzione `scrape(base_url, sezione)` in `backend/scraper.py` esegue tre livelli di navigazione:

```
1. Pagina principale (base_url)
   └── Tabella "Categorie" → link per ogni categoria

2. Pagina categoria (es. Default.asp?gare=4-0-ECC)
   └── Link per ogni girone

3. Pagina girone (es. gir.asp?gare=4-117-1)
   └── Tabella partite → righe con squadre e designati
       └── Filtro: mantieni solo le righe dove sezione == parametro sezione
```

Ogni partita trovata viene restituita come oggetto JSON:

```json
{
  "categoria": "ECCELLENZA",
  "squadra1": "CORTICELLA S.S.D. SRL",
  "squadra2": "ARCETANA",
  "nome": "Pietro Pio Izzo",
  "sezione": "Faenza",
  "ruolo": "Arbitro",
  "data": "22/03/2026"
}
```

Gli errori di rete (timeout, 404) vengono raccolti e restituiti nel campo `errors` della risposta, senza interrompere il processo — i risultati parziali vengono sempre restituiti.

### Endpoint API

```
POST /scrape
Content-Type: application/json

{
  "url": "https://www.aia-figc.it/designazioni/emiliaromagna/",
  "sezione": "Faenza"
}
```

Risposta:
```json
{
  "results": [...],
  "errors": [...]
}
```

```
GET /health → {"status": "ok"}
```
