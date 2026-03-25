export default function Summary({ results }) {
  const ruoliCount = results.reduce((acc, r) => {
    acc[r.ruolo] = (acc[r.ruolo] || 0) + 1
    return acc
  }, {})

  return (
    <div className="bg-blue-50 border border-blue-100 rounded-2xl p-4 flex flex-wrap gap-4 items-center">
      <div className="text-center">
        <div className="text-2xl font-bold text-blue-700">{results.length}</div>
        <div className="text-xs text-blue-500 font-medium uppercase tracking-wide">Designazioni totali</div>
      </div>
      <div className="w-px h-10 bg-blue-200 hidden sm:block" />
      <div className="flex flex-wrap gap-3">
        {Object.entries(ruoliCount).sort((a, b) => b[1] - a[1]).map(([ruolo, count]) => (
          <div key={ruolo} className="bg-white border border-blue-100 rounded-lg px-3 py-1.5 text-center min-w-[80px]">
            <div className="text-lg font-bold text-blue-600">{count}</div>
            <div className="text-xs text-gray-500">{ruolo}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
