import apiClient from './client'

interface LoginPayload {
    username: string;
    password: string;
}

interface TokenResponse {
    access_token: string;
    token_type: string;
}

export async function login(payload: LoginPayload): Promise<TokenResponse> {   
    const hotelId = Number(import.meta.env.VITE_HOTEL_ID ?? 1) 
    const {data} = await apiClient.post<TokenResponse>('/auth/login', {
        hotel_id: hotelId,
        ...payload,
    })
    return data
}