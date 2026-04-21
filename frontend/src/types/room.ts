export type RoomStatus = 'available' | 'occupied'

export interface ActiveStaySummary {
    stay_id: number
    account_number: number | null
    client_name: string
    client_dni: string
    checkin_datetime: string
    nights_so_far: number
    total_estimate: number
}

export interface RoomBoardItem {
    id: number
    room_number: string
    floor: string
    room_type: string
    price_per_night: number
    status: RoomStatus
    active_stay: ActiveStaySummary | null
}