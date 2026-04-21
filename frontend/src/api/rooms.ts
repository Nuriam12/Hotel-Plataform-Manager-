import type { RoomBoardItem } from '../types/room';
import apiClient from './client'


export async function fetchRoomBoard(): Promise<RoomBoardItem[]> {
    const {data} = await apiClient.get<RoomBoardItem[]>('/rooms/board')
    return data
}