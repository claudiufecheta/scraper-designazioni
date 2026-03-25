import { useState } from 'react'

const PRESET_URLS = [
  { label: 'Emilia-Romagna (tutte)', value: 'https://www.aia-figc.it/designazioni/emiliaromagna/' },
  { label: 'Emilia-Romagna (4-117)', value: 'https://www.aia-figc.it/designazioni/emiliaromagna/default.asp?gare=4-117' },
  { label: 'CAN C', value: 'https://www.aia-figc.it/designazioni/canc/' },
  { label: 'CAN D', value: 'https://www.aia-figc.it/designazioni/cand/' },
]

export default function UrlSelector({ onScrape, isLoading }) {
  const [url, setUrl] = useState(PRESET_URLS[1].value)

  function handleSubmit(e) {
    e.preventDefault()
    if (!url.trim()) return
    onScrape(url.trim())
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-4">
      <h2 className="text-lg font-semibold text-gray-800">Seleziona la categoria</h2>

      {/* Preset buttons */}
      <div className="flex flex-wrap gap-2">
        {PRESET_URLS.map((p) => (
          <button
            key={p.value}
            type="button"
            onClick={() => { setUrl(p.value) }}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              url === p.value
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {p.label}
          </button>
        ))}
      </div>

      <button
        type="submit"
        disabled={isLoading || !url.trim()}
        className="w-full sm:w-auto px-6 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-semibold rounded-lg transition-colors"
      >
        {isLoading ? 'Ricerca…' : 'Avvia ricerca'}
      </button>
    </form>
  )
}
