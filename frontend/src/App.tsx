import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import PrivateRoute from './components/PrivateRoute'
import LoginPage from './pages/LoginPage'
import BoardPage from './pages/BoardPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 1000 * 60, // datos frescos por 1 minuto antes de refetch
    },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          {/* Rutas protegidas: redirigen a /login si no hay token en memoria */}
          <Route element={<PrivateRoute />}>
            <Route path="/board" element={<BoardPage />} />
          </Route>

          {/* Cualquier ruta desconocida va al tablero (que a su vez redirige a login si no autenticado) */}
          <Route path="*" element={<Navigate to="/board" replace />} />
        </Routes>
      </BrowserRouter>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}
