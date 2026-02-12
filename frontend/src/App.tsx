import { BrowserRouter, Routes, Route } from 'react-router'
import './App.css'
import Navbar from './components/navbar'
import ProtectedRoute from './components/protected_route'
import Home from './pages/home'
import Login from './pages/login'
import Register from './pages/register'
import Chat from './pages/chat'
import MyLinks from './pages/my_links'
import { AuthProvider } from './context/auth_context'

function App() {

  return (
      <AuthProvider>
        <BrowserRouter>
        <div className="flex flex-col h-full w-full overflow-hidden">
          <Navbar />
          <main className="flex-1 flex flex-col overflow-hidden">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route element={<ProtectedRoute />}>
                <Route path="/chat" element={<Chat />} />
              </Route>
              <Route element={<ProtectedRoute />}>
                <Route path="/my_links" element={<MyLinks />} />
              </Route>
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
