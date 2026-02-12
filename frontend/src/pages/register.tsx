import { useAuth } from '../context/auth_context'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router'

const Register = () => {
    const [username, setUsername] = useState('')
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')

    const { register } = useAuth()

    const navigate = useNavigate()

    const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault()
        register({ username, email, password })
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
                    <input className="w-full max-w-md p-2 rounded-md border border-gray-300" type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
                    <input className="w-full max-w-md p-2 rounded-md border border-gray-300" type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
                    <input className="w-full max-w-md p-2 rounded-md border border-gray-300" type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
                    <button className="bg-blue-500 text-white p-2 rounded-md" type="submit">Register</button>
                    <p className="text-sm text-gray-500">Already have an account? <Link className="text-blue-500" to="/login">Login</Link></p>
                </div>
            </form>
        </div>
    );
};

export default Register;