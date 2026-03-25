const RUOLO_COLORS = {
  Arbitro: 'bg-green-100 text-green-700',
  AA1: 'bg-blue-100 text-blue-700',
  AA2: 'bg-blue-100 text-blue-700',
  IV: 'bg-purple-100 text-purple-700',
  VAR: 'bg-orange-100 text-orange-700',
  AVAR: 'bg-orange-100 text-orange-700',
}

function getRuoloClass(ruolo) {
  return RUOLO_COLORS[ruolo] || 'bg-gray-100 text-gray-600'
}

export default function MatchCard({ match }) {
  return (
    <div className="bg-white border border-gray-100 rounded-2xl shadow-sm p-4 hover:shadow-md transition-shadow">
      {/* Header: categoria + data */}
      <div className="flex justify-between items-start mb-3 gap-2">
        <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-1 rounded-full">
          {match.categoria}
        </span>
        {match.data && (
          <span className="text-xs text-gray-400 whitespace-nowrap">{match.data}</span>
        )}
      </div>

      {/* Partita */}
      <div className="text-center mb-3">
        <div className="flex items-center justify-center gap-2">
          <span className="font-semibold text-gray-800 text-sm text-right flex-1">{match.squadra1}</span>
          <span className="text-xs font-bold text-gray-400 shrink-0">vs</span>
          <span className="font-semibold text-gray-800 text-sm text-left flex-1">{match.squadra2}</span>
        </div>
      </div>

      {/* Designato */}
      <div className="flex items-center justify-between gap-2 pt-3 border-t border-gray-50">
        <div>
          <div className="text-sm font-medium text-gray-800">{match.nome}</div>
          <div className="text-xs text-gray-400">Sez. {match.sezione}</div>
        </div>
        <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${getRuoloClass(match.ruolo)}`}>
          {match.ruolo}
        </span>
      </div>
    </div>
  )
}
