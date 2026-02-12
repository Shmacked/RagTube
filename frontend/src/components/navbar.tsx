import { useAuth } from "../context/auth_context"
import { Home, User, UserPlus, LogOut, MessageCircle, Link2 } from "lucide-react"
import { NavLink } from 'react-router';

const Navbar = () => {
    const { user, loading, logout } = useAuth();

    return (
        <div className="sticky top-0 z-50 bg-gray-50">
            <nav className="max-w-7xl mx-auto">
                {loading ? (
                    <div className="flex items-center gap-2">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
                        <h1 className="text-4xl font-bold">RagTube</h1>
                    </div>
                ) : (
                <div className="flex items-center gap-2 p-4">
                    <div className="flex items-center gap-2 text-2xl font-bold">
                        <NavLink style={({ isActive }) => ({ color: isActive ? 'green' : 'black' })} to="/"><Home className="w-6 h-6" /></NavLink>
                        {user ? (
                            <>
                                <NavLink style={({ isActive }) => ({ color: isActive ? 'green' : 'black' })} to="/chat"><MessageCircle className="w-6 h-6" /></NavLink>
                                <NavLink style={({ isActive }) => ({ color: isActive ? 'green' : 'black' })} to="/my_links"><Link2 className="w-6 h-6" /></NavLink>
                                <span className="cursor-pointer" onClick={logout}><LogOut className="w-6 h-6" /></span>
                            </>
                        ) : (
                            <>
                                <NavLink style={({ isActive }) => ({ color: isActive ? 'green' : 'black' })} to="/login"><User className="w-6 h-6" /></NavLink>
                                <NavLink style={({ isActive }) => ({ color: isActive ? 'green' : 'black' })} to="/register"><UserPlus className="w-6 h-6" /></NavLink>
                            </>
                        )}
                    </div>
                </div>
                )}
            </nav>
            <hr className="border-gray-300 my-2" />
        </div>
    );
};

export default Navbar;