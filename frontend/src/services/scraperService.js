const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

/**
 * Lancia lo scraping sul backend.
 * @param {string} url - URL base da scrapare
 * @param {string} sezione - Sezione da filtrare (default: "Faenza")
 * @returns {Promise<{results: Array, errors: Array}>}
 */
export async function runScrape(url, sezione = 'Faenza') {
  const response = await fetch(`${API_BASE}/scrape`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url, sezione }),
  })

  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || `Errore HTTP ${response.status}`)
  }

  return response.json()
}
