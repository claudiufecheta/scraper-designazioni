export default function FilterBar({ filters, setFilters, categories, dates, ruoli }) {
  function handleChange(key, value) {
    setFilters((prev) => ({ ...prev, [key]: value }))
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 flex flex-wrap gap-3 items-end">
      <div className="flex flex-col gap-1 min-w-[140px]">
        <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Categoria</label>
        <select
          value={filters.categoria}
          onChange={(e) => handleChange('categoria', e.target.value)}
          className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Tutte</option>
          {categories.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>

      <div className="flex flex-col gap-1 min-w-[140px]">
        <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Data</label>
        <select
          value={filters.data}
          onChange={(e) => handleChange('data', e.target.value)}
          className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Tutte</option>
          {dates.map((d) => <option key={d} value={d}>{d}</option>)}
        </select>
      </div>

      <div className="flex flex-col gap-1 min-w-[140px]">
        <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Ruolo</label>
        <select
          value={filters.ruolo}
          onChange={(e) => handleChange('ruolo', e.target.value)}
          className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Tutti</option>
          {ruoli.map((r) => <option key={r} value={r}>{r}</option>)}
        </select>
      </div>

      {(filters.categoria || filters.data || filters.ruolo) && (
        <button
          onClick={() => setFilters({ categoria: '', data: '', ruolo: '' })}
          className="px-3 py-2 text-sm text-gray-500 hover:text-gray-700 underline"
        >
          Reset filtri
        </button>
      )}
    </div>
  )
}
