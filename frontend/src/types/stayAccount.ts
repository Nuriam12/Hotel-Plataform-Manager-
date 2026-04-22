/** Contrato alineado con `StayAccountResponse` en `app/schemas/stay.py` */

export interface StayInfo {
    id: number
    status: string
    checkin_datetime: string
    checkout_datetime: string | null
    price_per_night: number
    notes: string | null
    additional_charge: number | null
    additional_charge_notes: string | null
  }
  
  export interface RoomInfo {
    id: number
    room_number: string
    room_type: string
    floor: string
  }
  
  export interface ClientInfo {
    id: number
    name: string
    dni: string
    phone: string | null
  }
  
  export interface ConsumptionLine {
    id: number
    product_id: number
    product_name: string
    quantity: number
    unit_price: number
    subtotal: number
    created_at: string
    is_cancelled: boolean
  }
  
  export interface AccountTotals {
    nights: number
    nights_cost: number
    consumptions_total: number
    additional_charge: number
    grand_total: number
  }
  
  export interface StayAccountResponse {
    account_number: number | null
    stay: StayInfo
    room: RoomInfo
    client: ClientInfo
    consumptions: ConsumptionLine[]
    totals: AccountTotals
  }