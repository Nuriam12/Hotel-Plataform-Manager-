export interface ConsumptionCreate {
    stay_id: number
    product_id: number
    quantity: number
    notes: string | null
}

export interface ConsumptionRead {
    id: number
    hotel_id: number
    stay_id: number
    product_id: number
    quantity: number
    unit_price: number
    created_at: string
    is_cancelled: boolean
    cancelled_at: string | null
    cancelled_by: number | null
}