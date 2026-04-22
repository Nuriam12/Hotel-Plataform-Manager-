import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchStayAccount } from '../api/stay'
import LoadingSpinner from './LoadingSpinner'

function money(n: number) {
  return `S/ ${Number(n).toFixed(2)}`
}

function formatDateTime(iso: string) {
  try {
    return new Date(iso).toLocaleString('es-PE', {
      dateStyle: 'short',
      timeStyle: 'short',
    })
  } catch {
    return iso
  }
}

interface Props {
  stayId: number
  onClose: () => void
}

export default function AccountModal({ stayId, onClose }: Props) {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['stays', stayId, 'account'],
    queryFn: () => fetchStayAccount(stayId),
  })

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  const completed = data?.stay.status === 'completed'

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
      role="dialog"
      aria-modal="true"
      aria-labelledby="account-modal-title"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col border border-gray-200"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-4 px-5 py-4 border-b border-gray-100 bg-slate-50 shrink-0">
          <div>
            <h2 id="account-modal-title" className="text-lg font-bold text-slate-800">
              Cuenta corriente
            </h2>
            {data?.account_number != null && (
              <p className="text-xs text-slate-500 mt-0.5">
                Nº {String(data.account_number).padStart(6, '0')}
              </p>
            )}
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-2 text-slate-500 hover:bg-white hover:text-slate-800 transition-colors"
            aria-label="Cerrar"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="overflow-y-auto flex-1 px-5 py-4">
          {isLoading && <LoadingSpinner text="Cargando cuenta..." />}

          {isError && (
            <div className="text-center py-8">
              <p className="text-gray-600 text-sm mb-3">No se pudo cargar la cuenta.</p>
              <button
                type="button"
                onClick={() => refetch()}
                className="text-sm text-blue-600 hover:underline"
              >
                Reintentar
              </button>
            </div>
          )}

          {data && (
            <div className="space-y-5">
              {completed && (
                <p className="text-xs font-medium text-amber-800 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
                  Estadía finalizada — cuenta de solo lectura.
                </p>
              )}

              <div className="grid sm:grid-cols-2 gap-4 text-sm">
                <div className="rounded-xl border border-gray-200 p-3">
                  <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1">Cliente</p>
                  <p className="font-semibold text-gray-900">{data.client.name}</p>
                  <p className="text-gray-600 mt-1">DNI: {data.client.dni}</p>
                  {data.client.phone && (
                    <p className="text-gray-600">Tel: {data.client.phone}</p>
                  )}
                </div>
                <div className="rounded-xl border border-gray-200 p-3">
                  <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1">Habitación</p>
                  <p className="font-semibold text-gray-900">Hab. {data.room.room_number}</p>
                  <p className="text-gray-600 mt-1 capitalize">{data.room.room_type}</p>
                  <p className="text-gray-500 text-xs">Piso {data.room.floor}</p>
                </div>
              </div>

              <div className="rounded-xl border border-gray-200 p-3 text-sm">
                <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2">Estadía</p>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-gray-500">Ingreso</span>
                    <p className="font-medium text-gray-800">{formatDateTime(data.stay.checkin_datetime)}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Salida</span>
                    <p className="font-medium text-gray-800">
                      {data.stay.checkout_datetime
                        ? formatDateTime(data.stay.checkout_datetime)
                        : '—'}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-500">Tarifa / noche</span>
                    <p className="font-medium text-gray-800">{money(data.stay.price_per_night)}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Estado</span>
                    <p className="font-medium text-gray-800 capitalize">{data.stay.status}</p>
                  </div>
                </div>
                {data.stay.additional_charge != null && data.stay.additional_charge > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-100 text-xs">
                    <span className="text-gray-500">Cargo ADIC</span>
                    <p className="font-semibold text-gray-900">{money(data.stay.additional_charge)}</p>
                    {data.stay.additional_charge_notes && (
                      <p className="text-gray-600 mt-1">{data.stay.additional_charge_notes}</p>
                    )}
                  </div>
                )}
              </div>

              <div>
                <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2">Consumos</p>
                {data.consumptions.length === 0 ? (
                  <p className="text-sm text-gray-500 italic">Sin consumos registrados.</p>
                ) : (
                  <div className="border border-gray-200 rounded-xl overflow-hidden text-xs">
                    <table className="w-full text-left">
                      <thead className="bg-gray-50 text-gray-500 font-medium">
                        <tr>
                          <th className="px-3 py-2">Producto</th>
                          <th className="px-2 py-2 w-10 text-center">Q</th>
                          <th className="px-2 py-2 text-right">P</th>
                          <th className="px-3 py-2 text-right">Total</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100">
                        {data.consumptions.map((c) => (
                          <tr
                            key={c.id}
                            className={c.is_cancelled ? 'bg-gray-50 text-gray-400 line-through' : ''}
                          >
                            <td className="px-3 py-2 font-medium text-gray-800">{c.product_name}</td>
                            <td className="px-2 py-2 text-center">{c.quantity}</td>
                            <td className="px-2 py-2 text-right tabular-nums">{money(c.unit_price)}</td>
                            <td className="px-3 py-2 text-right font-medium tabular-nums">{money(c.subtotal)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>

              <div className="rounded-xl bg-slate-900 text-white p-4 text-sm space-y-1.5">
                <div className="flex justify-between">
                  <span className="text-slate-400">Noches ({data.totals.nights})</span>
                  <span className="tabular-nums">{money(data.totals.nights_cost)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Consumos</span>
                  <span className="tabular-nums">{money(data.totals.consumptions_total)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">ADIC</span>
                  <span className="tabular-nums">{money(data.totals.additional_charge)}</span>
                </div>
                <div className="flex justify-between pt-2 border-t border-slate-700 font-bold text-base">
                  <span>Total</span>
                  <span className="tabular-nums">{money(data.totals.grand_total)}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="px-5 py-3 border-t border-gray-100 bg-gray-50 shrink-0">
          <button
            type="button"
            onClick={onClose}
            className="w-full sm:w-auto px-4 py-2 rounded-lg bg-white border border-gray-300 text-sm font-medium text-gray-700 hover:bg-gray-100"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  )
}