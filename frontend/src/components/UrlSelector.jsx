import { useState } from 'react'
import { REGIONI } from '../data/regioni'

const DEFAULT_REGIONE = REGIONI.find((r) => r.nome === 'Emilia Romagna')
const DEFAULT_SEZIONE = DEFAULT_REGIONE.sezioni.find((s) => s.nome === 'Faenza')

const TIPI = [
  { label: 'OTS', url: null },
  { label: 'CAN C', url: 'https://www.aia-figc.it/designazioni/canc/' },
  { label: 'CAN D', url: 'https://www.aia-figc.it/designazioni/cand/' },
]

export default function UrlSelector({ onScrape, isLoading }) {
  const [regione, setRegione] = useState(DEFAULT_REGIONE)
  const [sezione, setSezione] = useState(DEFAULT_SEZIONE)
  const [tipo, setTipo] = useState(TIPI[0])

  function handleRegioneChange(e) {
    const nuovaRegione = REGIONI.find((r) => r.nome === e.target.value)
    setRegione(nuovaRegione)
    setSezione(nuovaRegione.sezioni[0])
  }

  function handleSezioneChange(e) {
    setSezione(regione.sezioni.find((s) => s.nome === e.target.value))
  }

  function handleSubmit(e) {
    e.preventDefault()
    const url = tipo.url ?? sezione.url
    onScrape(url, sezione.nome)
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-4">
      <h2 className="text-lg font-semibold text-gray-800">Seleziona regione e sezione</h2>

      {/* Select Regione + Sezione */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex flex-col gap-1 flex-1">
          <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Regione</label>
          <select
            value={regione.nome}
            onChange={handleRegioneChange}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {REGIONI.map((r) => (
              <option key={r.nome} value={r.nome}>{r.nome}</option>
            ))}
          </select>
        </div>

        <div className="flex flex-col gap-1 flex-1">
          <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Sezione</label>
          <select
            value={sezione.nome}
            onChange={handleSezioneChange}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {regione.sezioni.map((s) => (
              <option key={s.nome} value={s.nome}>{s.nome}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Tipo ricerca */}
      <div className="flex flex-col gap-1">
        <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Tipo ricerca</label>
        <div className="flex gap-2">
          {TIPI.map((t) => (
            <button
              key={t.label}
              type="button"
              onClick={() => setTipo(t)}
              className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                tipo.label === t.label
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full sm:w-auto px-6 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-semibold rounded-lg transition-colors"
      >
        {isLoading ? 'Ricerca…' : 'Avvia ricerca'}
      </button>
    </form>
  )
}
