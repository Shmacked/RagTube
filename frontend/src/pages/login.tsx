import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router'
import { useAuth } from '../context/auth_context'


const Login = () => {
    const [usernameOrEmail, setUsernameOrEmail] = useState('')
    const [password, setPassword] = useState('')

    const { login } = useAuth()

    const navigate = useNavigate()
    
    const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault()

        if (!usernameOrEmail || !password) {
            alert('Please fill in all fields')
            return
        }

        login({ username_or_email: usernameOrEmail, password: password })
        .then(() => {
            navigate('/chat')
        })
        .catch(error => {
            console.error(error)
        })
    }
    return (
        <div className="flex flex-col items-center justify-center h-screen">
            <form onSubmit={handleSubmit}>
                <div className="flex flex-col items-center justify-center gap-2">
                    <input className="w-full max-w-md p-2 rounded-md border border-gray-300" type="text" placeholder="Username or Email" value={usernameOrEmail} onChange={(e) => setUsernameOrEmail(e.target.value)} />
                    <input className="w-full max-w-md p-2 rounded-md border border-gray-300" type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
                    <button className="bg-blue-500 text-white p-2 rounded-md" type="submit">Login</button>
                    <p className="text-sm text-gray-500">Don't have an account? <Link className="text-blue-500" to="/register">Register</Link></p>
                </div>
            </form>
        </div>
    );
};

export default Login;