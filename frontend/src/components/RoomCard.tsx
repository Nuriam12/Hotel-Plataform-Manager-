import type { RoomBoardItem } from '../types/room'

const TIPO_LABEL: Record<string, string> = {
  individual: 'Individual',
  doble: 'Doble',
  suite: 'Suite',
  matrimonial: 'Matrimonial',
  familiar: 'Familiar',
}

interface Props {
  room: RoomBoardItem
  onOpenAccount: (stayId: number) => void
}

export default function RoomCard({ room, onOpenAccount }: Props) {
  const ocupada = room.status === 'occupied'
  const stay = room.active_stay

  return (
    <div
      onClick={() => ocupada && stay && onOpenAccount(stay.stay_id)}
      className={`
        rounded-xl border-2 p-3 transition-all select-none
        ${ocupada
          ? 'bg-red-50 border-red-300 hover:bg-red-100 cursor-pointer'
          : 'bg-green-50 border-green-200 cursor-default'
        }
      `}
    >
      {/* Cabecera de la tarjeta */}
      <div className="flex justify-between items-start mb-1">
        <span className="text-base font-bold text-gray-800 leading-none">
          {room.room_number}
        </span>
        <span className={`
          text-[10px] font-bold px-1.5 py-0.5 rounded-full uppercase tracking-wide
          ${ocupada ? 'bg-red-200 text-red-800' : 'bg-green-200 text-green-800'}
        `}>
          {ocupada ? 'OCUPADA' : 'LIBRE'}
        </span>
      </div>

      {/* Tipo de habitación */}
      <p className="text-[11px] text-gray-400 uppercase tracking-wide">
        {TIPO_LABEL[room.room_type] ?? room.room_type} · Piso {room.floor}
      </p>

      {/* Info de la estadía activa */}
      {ocupada && stay && (
        <div className="mt-2 pt-2 border-t border-red-200 space-y-0.5">
          <p className="text-sm font-semibold text-gray-700 truncate">{stay.client_name}</p>
          <p className="text-[11px] text-gray-500">DNI: {stay.client_dni}</p>
          <div className="flex justify-between items-center pt-1">
            <span className="text-[11px] text-gray-500">
              {stay.nights_so_far} noche{stay.nights_so_far !== 1 ? 's' : ''}
            </span>
            <span className="text-xs font-bold text-red-700">
              S/ {Number(stay.total_estimate).toFixed(2)}
            </span>
          </div>
          {stay.account_number != null && (
            <p className="text-[10px] text-gray-400">
              Cta. N° {String(stay.account_number).padStart(6, '0')}
            </p>
          )}
        </div>
      )}

      {!ocupada && (
        <p className="text-xs text-gray-400 mt-2">
          S/ {Number(room.price_per_night).toFixed(2)} / noche
        </p>
      )}
    </div>
  )
}