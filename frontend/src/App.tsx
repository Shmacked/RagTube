import { BrowserRouter, Routes, Route, Link } from 'react-router'
import './App.css'
import Home from './pages/home'
import Login from './pages/login'
import Register from './pages/register'

function App() {

  return (
    <>
      <nav>
        <h1 className="text-4xl font-bold">
          RagTube
        </h1>
        <div className="flex items-center gap-2">
          <Link to="/">Home</Link>
          <Link to="/login">Login</Link>
          <Link to="/register">Register</Link>
        </div>
      </nav>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Routes>
      </BrowserRouter>
    </>
  )
}

export default App
