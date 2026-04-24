import apiClient from './client'
import type { ConsumptionCreate, ConsumptionRead } from '../types/consumption'

export async function createConsumption(consumption: ConsumptionCreate): Promise<ConsumptionRead> {
    const {data} = await apiClient.post('/consumptions', consumption)
    return data
}

export async function cancelConsumption(consumptionId: number): Promise<ConsumptionRead> {
    const {data} = await apiClient.post(`/consumptions/${consumptionId}/cancel`)
    return data
}
