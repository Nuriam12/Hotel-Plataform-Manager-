import { create } from 'zustand'
import type { AuthState, TokenPayload } from '../types/auth'

// Decodifica el payload del JWT (sección central, base64url → JSON)
function decodeJWT(token: string): TokenPayload {
  const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
  return JSON.parse(window.atob(base64))
}

interface AuthActions {
  setAuth: (token: string) => void
  logout: () => void
}

// Sin persist: el token vive solo en memoria.
// Si el usuario refresca la página, vuelve al login.
// Esto evita exponer el token en localStorage (vector XSS).
export const useAuthStore = create<AuthState & AuthActions>()((set) => ({
  token: null,
  userId: null,
  hotelId: null,
  role: null,
  username: null,

  setAuth: (token) => {
    const payload = decodeJWT(token)
    set({
      token,
      userId: Number(payload.sub),
      hotelId: payload.hotel_id,
      role: payload.role,
      username: payload.username,
    })
  },

  logout: () =>
    set({
      token: null,
      userId: null,
      hotelId: null,
      role: null,
      username: null,
    }),
}))
