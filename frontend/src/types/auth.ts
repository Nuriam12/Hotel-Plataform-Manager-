export interface TokenPayload {
    sub: string; //id del usuario
    hotel_id: number;
    role: "ADMINISTRADOR" | "TRABAJADOR";
    username: string;
    exp: number;
}

export interface AuthState {
    token: string | null;
    userId: number | null;
    hotelId: number | null;
    role: "ADMINISTRADOR" | "TRABAJADOR" | null;
    username: string | null;
}
