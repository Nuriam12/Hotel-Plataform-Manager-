import apiClient from './client'
import type { StayAccountResponse } from '../types/stayAccount'

export async function fetchStayAccount(stayId: number): Promise<StayAccountResponse> {
    const response = await apiClient.get<StayAccountResponse>(`/stays/${stayId}/account`)
    return response.data
}