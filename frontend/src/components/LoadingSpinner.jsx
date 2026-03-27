export default function LoadingSpinner() {
  return (
    <div className="fixed inset-0 z-[9999] flex flex-col items-center justify-center bg-white/80 backdrop-blur-sm">
      <div className="w-14 h-14 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-4" />
      <p className="text-gray-600 font-medium">Ricerca in corso…</p>
      <p className="text-gray-400 text-sm mt-1">Potrebbe richiedere qualche secondo</p>
    </div>
  )
}
