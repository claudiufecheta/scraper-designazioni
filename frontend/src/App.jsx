import { useState, useMemo } from 'react'
import { runScrape } from './services/scraperService'
import UrlSelector from './components/UrlSelector'
import MatchCard from './components/MatchCard'
import LoadingSpinner from './components/LoadingSpinner'

function groupByDate(results) {
  return results.reduce((acc, r) => {
    const key = r.data || 'Data non disponibile'
    if (!acc[key]) acc[key] = []
    acc[key].push(r)
    return acc
  }, {})
}

/**
 * Formatta i risultati per la clipboard raggruppando per categoria e partita.
 * Partite con più designazioni (stesso squadra1+squadra2+data) vengono unite.
 */
function formatForClipboard(results) {
  // Raggruppa per categoria, poi per partita
  const byCategoria = {}
  for (const r of results) {
    if (!byCategoria[r.categoria]) byCategoria[r.categoria] = {}
    const matchKey = `${r.data}||${r.squadra1}||${r.squadra2}`
    if (!byCategoria[r.categoria][matchKey]) {
      byCategoria[r.categoria][matchKey] = {
        data: r.data,
        squadra1: r.squadra1,
        squadra2: r.squadra2,
        designazioni: [],
      }
    }
    byCategoria[r.categoria][matchKey].designazioni.push({ ruolo: r.ruolo, nome: r.nome })
  }

  let text = ''
  for (const [categoria, matches] of Object.entries(byCategoria)) {
    text += `⚽ ${categoria} ⚽\n`
    for (const match of Object.values(matches)) {
      text += `  ${match.data}\n`
      text += `  ${match.squadra1} - ${match.squadra2}\n`
      for (const d of match.designazioni) {
        text += `  ${d.ruolo}: ${d.nome}\n`
      }
      text += '\n'
    }
  }

  return text.trim()
}

export default function App() {
  const [status, setStatus] = useState('idle') // idle | loading | success | error
  const [results, setResults] = useState([])
  const [errors, setErrors] = useState([])
  const [errorMessage, setErrorMessage] = useState('')
  const [copied, setCopied] = useState(false)

  async function handleScrape(url, sezione) {
    setStatus('loading')
    setResults([])
    setErrors([])
    setErrorMessage('')
    setCopied(false)

    try {
      const data = await runScrape(url, sezione)
      setResults(data.results || [])
      setErrors(data.errors || [])
      setStatus('success')
    } catch (err) {
      setErrorMessage(err.message || 'Errore sconosciuto')
      setStatus('error')
    }
  }

  async function handleCopy() {
    const text = formatForClipboard(results)
    await navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const grouped = useMemo(() => groupByDate(results), [results])
  const sortedDates = Object.keys(grouped).sort()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Overlay loader */}
      {status === 'loading' && <LoadingSpinner />}

      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center gap-3">
          <span className="text-2xl">⚽</span>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Designazioni Viewer</h1>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-6 space-y-6">
        {/* URL Selector */}
        <UrlSelector onScrape={handleScrape} isLoading={status === 'loading'} />

        {/* Error */}
        {status === 'error' && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-2xl p-4 text-sm">
            <strong>Errore:</strong> {errorMessage}
          </div>
        )}

        {/* Backend warnings */}
        {errors.length > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-2xl p-4 space-y-1">
            <p className="text-sm font-semibold text-yellow-700">Avvisi durante lo scraping:</p>
            {errors.map((e, i) => (
              <p key={i} className="text-xs text-yellow-600">{e}</p>
            ))}
          </div>
        )}

        {/* Results */}
        {status === 'success' && (
          <>
            {results.length === 0 ? (
              <div className="text-center py-12 text-gray-400">
                <p className="text-4xl mb-2">🔍</p>
                <p>Nessuna designazione trovata per la sezione Faenza.</p>
              </div>
            ) : (
              <>
                {/* Bottone Copia risultati */}
                <button
                  onClick={handleCopy}
                  className={`w-full sm:w-auto px-6 py-3 font-semibold rounded-xl transition-colors text-white ${
                    copied ? 'bg-green-700' : 'bg-green-600 hover:bg-green-700'
                  }`}
                >
                  {copied ? '✓ Copiato!' : '📋 Copia risultati'}
                </button>

                {/* Schede partite raggruppate per data */}
                <div className="space-y-6">
                  {sortedDates.map((date) => (
                    <section key={date}>
                      <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
                        {date}
                      </h3>
                      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                        {grouped[date].map((match, idx) => (
                          <MatchCard key={idx} match={match} />
                        ))}
                      </div>
                    </section>
                  ))}
                </div>
              </>
            )}
          </>
        )}
      </main>
    </div>
  )
}
