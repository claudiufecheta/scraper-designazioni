from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scraper import scrape

app = FastAPI(title="Designazioni Viewer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


class ScrapeRequest(BaseModel):
    url: str
    sezione: str = "Faenza"


@app.post("/scrape")
async def run_scrape(body: ScrapeRequest):
    if not body.url.startswith("https://www.aia-figc.it/"):
        raise HTTPException(status_code=400, detail="URL non valido: deve iniziare con https://www.aia-figc.it/")
    data = scrape(base_url=body.url, sezione=body.sezione)
    return data


@app.get("/health")
async def health():
    return {"status": "ok"}
