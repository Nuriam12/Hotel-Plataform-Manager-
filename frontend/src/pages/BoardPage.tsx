import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { fetchRoomBoard } from '../api/rooms'
import { useAuthStore } from '../stores/authStore'
import RoomCard from '../components/RoomCard'
import LoadingSpinner from '../components/LoadingSpinner'
import AccountModal from '../components/AccountModal'
import type { RoomBoardItem } from '../types/room'

// Pequeño componente para las estadísticas del encabezado
function StatBadge({
  label,
  value,
  color = 'gray',
}: {
  label: string
  value: number
  color?: 'gray' | 'green' | 'red'
}) {
  const colorClass = {
    gray: 'bg-gray-100 text-gray-700',
    green: 'bg-green-100 text-green-700',
    red: 'bg-red-100 text-red-700',
  }[color]

  return (
    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg ${colorClass}`}>
      <span className="text-lg font-bold leading-none">{value}</span>
      <span className="text-xs font-medium uppercase tracking-wide">{label}</span>
    </div>
  )
}

export default function BoardPage() {
  const { username, role, logout } = useAuthStore()
  const navigate = useNavigate()
  const [selectedStayId, setSelectedStayId] = useState<number | null>(null)

  const { data: rooms, isLoading, isError, refetch } = useQuery({
    queryKey: ['rooms', 'board'],
    queryFn: fetchRoomBoard,
    refetchInterval: 30_000, // refresca automáticamente cada 30 segundos
  })

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  // Agrupar habitaciones por piso para mostrarlas como el tablero físico
  const byFloor = (rooms ?? []).reduce<Record<string, RoomBoardItem[]>>((acc, room) => {
    if (!acc[room.floor]) acc[room.floor] = []
    acc[room.floor].push(room)
    return acc
  }, {})
  const floors = Object.keys(byFloor).sort()

  const totalOccupied = rooms?.filter((r) => r.status === 'occupied').length ?? 0
  const totalAvailable = rooms?.filter((r) => r.status === 'available').length ?? 0

  return (
    <div className="min-h-screen bg-gray-50">

      {/* ── Cabecera fija ── */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">

          {/* Logo + título */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center shrink-0">
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16" />
              </svg>
            </div>
            <div>
              <h1 className="text-base font-bold text-gray-800 leading-none">CONTROL DIARIO</h1>
              <p className="text-[11px] text-gray-400 mt-0.5">HPM · Hotel Platform Manager</p>
            </div>
          </div>

          {/* Estadísticas + usuario + salir */}
          <div className="flex items-center gap-3">
            {rooms && (
              <div className="hidden sm:flex items-center gap-2">
                <StatBadge label="Total" value={rooms.length} color="gray" />
                <StatBadge label="Libres" value={totalAvailable} color="green" />
                <StatBadge label="Ocupadas" value={totalOccupied} color="red" />
              </div>
            )}

            <div className="flex items-center gap-3 pl-3 border-l border-gray-200">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-semibold text-gray-700 leading-none">{username}</p>
                <p className="text-[11px] text-gray-400 mt-0.5">
                  {role === 'ADMINISTRADOR' ? 'Administrador' : 'Trabajador'}
                </p>
              </div>
              <button
                onClick={handleLogout}
                className="text-xs text-red-600 hover:text-red-800 font-medium
                           px-2 py-1 rounded hover:bg-red-50 transition-colors cursor-pointer"
              >
                Salir
              </button>
            </div>
          </div>

        </div>
      </header>

      {/* ── Contenido principal ── */}
      <main className="max-w-7xl mx-auto px-4 py-6">

        {isLoading && <LoadingSpinner text="Cargando tablero..." />}

        {isError && (
          <div className="text-center py-16">
            <p className="text-gray-500 mb-4">No se pudo cargar el tablero.</p>
            <button
              onClick={() => refetch()}
              className="text-sm text-blue-600 hover:underline cursor-pointer"
            >
              Reintentar
            </button>
          </div>
        )}

        {/* Grid de habitaciones agrupado por piso */}
        {floors.map((floor) => (
          <section key={floor} className="mb-8">

            {/* Separador de piso */}
            <div className="flex items-center gap-3 mb-3">
              <h2 className="text-xs font-bold text-gray-400 uppercase tracking-widest shrink-0">
                Piso {floor}
              </h2>
              <div className="flex-1 h-px bg-gray-200" />
              <span className="text-xs text-gray-400 shrink-0">
                {byFloor[floor].length} hab.
              </span>
            </div>

            {/* Tarjetas */}
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3">
              {byFloor[floor]
                .sort((a, b) => a.room_number.localeCompare(b.room_number))
                .map((room) => (
                  <RoomCard
                    key={room.id}
                    room={room}
                    onOpenAccount={(stayId) => setSelectedStayId(stayId)}
                  />
                ))}
            </div>

          </section>
        ))}

        {rooms && !isLoading && (
          <p className="text-center text-xs text-gray-400 mt-2">
            Tablero actualizado automáticamente cada 30 segundos.
          </p>
        )}

      </main>

      {selectedStayId != null && (
        <AccountModal
          stayId={selectedStayId}
          onClose={() => setSelectedStayId(null)}
        />
      )}
    </div>
  )
}