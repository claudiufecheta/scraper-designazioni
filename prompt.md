Agisci come un Senior Full Stack Engineer esperto in React, architetture scalabili e sviluppo di applicazioni web production-ready.
Devi progettare e implementare una web app chiamata "Designazioni Viewer" — un'interfaccia React che consente di lanciare uno scraping su un sito di designazioni arbitri AIA-FIGC e visualizzare i risultati in modo chiaro e organizzato.

🎯 OBIETTIVO APP
L'app sostituisce il seguente script Python attualmente usato da terminale: cat_scraper.py
Lo script visita pagine del sito https://www.aia-figc.it/designazioni/ (che non ha blocchi o restrizioni allo scraping), naviga la struttura gerarchica delle categorie → gironi → partite, e raccoglie i dati delle designazioni dove la sezione dell'arbitro è "Faenza".
Il problema attuale: ogni cambio di base_url richiede una modifica manuale al codice. L'app deve risolvere questo problema.

⚠️ VINCOLO ARCHITETTURALE FONDAMENTALE
React nel browser non può fare scraping direttamente a causa dei blocchi CORS. È necessario un backend che esegua le richieste HTTP per conto del frontend.
La soluzione raccomandata è:

Backend: Python con FastAPI (riuso dello scraper esistente)
Frontend: React (Vite) + Tailwind CSS
Comunicazione: REST API locale (FastAPI espone un endpoint, React lo chiama)

Se proponi un'architettura diversa, motivala esplicitamente spiegando come risolve il problema CORS.

🔴 REGOLE FONDAMENTALI

Architettura modulare e separata (frontend / backend)
Nessuna duplicazione di codice (DRY)
Separazione netta tra UI, business logic e data layer
Naming chiaro e consistente
Codice leggibile e production-ready
Gestione errori e edge cases (timeout, pagine non raggiungibili, struttura HTML cambiata)
Mobile-first design
Ogni scelta architetturale deve essere motivata


📦 FUNZIONALITÀ RICHIESTE
1. Selezione base_url

Campo di input (o dropdown con URL predefiniti) per scegliere il base_url su cui lanciare lo scraping
URL di esempio già presenti come shortcut:

https://www.aia-figc.it/designazioni/emiliaromagna/
https://www.aia-figc.it/designazioni/emiliaromagna/default.asp?gare=4-117
https://www.aia-figc.it/designazioni/canc/
https://www.aia-figc.it/designazioni/cand/


Possibilità di inserire URL personalizzati

2. Avvio scraping

Pulsante "Avvia scraping" che chiama il backend
Indicatore di caricamento durante l'elaborazione
Gestione errori visibile all'utente

3. Visualizzazione risultati
I dati estratti hanno questa struttura per ogni record:
json{
  "categoria": "...",
  "squadra1": "...",
  "squadra2": "...",
  "nome": "...",
  "sezione": "Faenza",
  "ruolo": "...",
  "data": "dd/mm/YYYY"
}
```

L'interfaccia deve mostrare i risultati in modo chiaro, raggruppati per **data** e/o **categoria**, con visualizzazione tipo "scheda partita" (non una semplice tabella).

### 4. Filtri

- Filtraggio per categoria
- Filtraggio per data
- Filtraggio per ruolo

### 5. Riepilogo

- Contatore totale partite trovate
- Riepilogo per ruolo (es. quante volte come Arbitro, AA1, AA2, ecc.)

---

## 🏗️ OUTPUT RICHIESTO

### 1. Architettura scelta
- Spiegazione della struttura generale
- Come viene risolto il problema CORS
- Pattern utilizzati

### 2. Struttura cartelle completa

Mostra il file tree sia del backend che del frontend:
```
/backend
  main.py
  scraper.py
  requirements.txt
  ...

/frontend
  /src
    /components
    /features
    /hooks
    /services
    /utils
    ...
3. Backend (FastAPI)

Endpoint POST /scrape che accetta { "url": "..." } e restituisce i dati estratti
Adattamento dello scraper Python esistente come modulo importabile
CORS configurato per accettare richieste da localhost:5173
Gestione timeout e errori di rete
requirements.txt completo

4. Frontend (React)

Componente principale con selezione URL e avvio scraping
Componenti per la visualizzazione delle schede partita
Servizio per la chiamata API al backend
Gestione stato di loading/error/success
Filtri funzionanti lato client sui dati ricevuti

5. Esempi di codice
Fornisci il codice completo e funzionante per:

backend/scraper.py (adattamento dello script esistente)
backend/main.py (FastAPI con l'endpoint /scrape)
frontend/src/services/scraperService.js (chiamata al backend)
frontend/src/components/MatchCard.jsx (componente scheda partita)
frontend/src/App.jsx (componente principale)

6. Setup e avvio
Istruzioni chiare per:
bash# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev

🔍 REVIEW CRITICA (OBBLIGATORIA)
Alla fine:

Evidenzia i limiti dell'architettura proposta
Quando questa soluzione non è adatta
Come si potrebbe deployare in produzione (non solo in locale)
Possibili miglioramenti futuri (es. caching, storico delle ricerche, export CSV)


🎯 OBIETTIVO FINALE
Il risultato deve essere immediatamente avviabile in locale da uno sviluppatore, con backend Python e frontend React separati, comunicanti via API REST, e un'interfaccia che rende l'uso dello scraper molto più comodo rispetto al terminale.