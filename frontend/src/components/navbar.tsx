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
                <div className="flex items-center gap-2 py-4 px-0">
                    <div className="flex items-center gap-2 text-2xl font-bold">
                        <NavLink className="bg-blue-500/70 text-white px-6 py-2 rounded-lg shadow-lg 
                                    transition-all duration-150 
                                    hover:shadow-md hover:translate-y-0.5 
                                    active:shadow-none active:translate-y-1 cursor-pointer"
                                style={({ isActive }) => ({ color: isActive ? 'darkgreen' : 'black' })} to="/"><Home className="w-6 h-6" /></NavLink>
                        {user ? (
                            <>
                                <NavLink className="bg-blue-500/70 text-white px-6 py-2 rounded-lg shadow-lg 
                                    transition-all duration-150 
                                    hover:shadow-md hover:translate-y-0.5 
                                    active:shadow-none active:translate-y-1 cursor-pointer"
                                style={({ isActive }) => ({ color: isActive ? 'darkgreen' : 'black' })} to="/chat"><MessageCircle className="w-6 h-6" /></NavLink>
                                <NavLink className="bg-blue-500/70 text-white px-6 py-2 rounded-lg shadow-lg 
                                    transition-all duration-150 
                                    hover:shadow-md hover:translate-y-0.5 
                                    active:shadow-none active:translate-y-1 cursor-pointer"
                                style={({ isActive }) => ({ color: isActive ? 'darkgreen' : 'black' })} to="/my_links"><Link2 className="w-6 h-6" /></NavLink>
                                <span className="bg-red-500/70 text-white px-6 py-2 rounded-lg shadow-lg 
                                    transition-all duration-150 
                                    hover:shadow-md hover:translate-y-0.5 
                                    active:shadow-none active:translate-y-1 cursor-pointer"
                                onClick={logout}><LogOut className="w-6 h-6" /></span>
                            </>
                        ) : (
                            <>
                                <NavLink className="bg-blue-500/70 text-white px-6 py-2 rounded-lg shadow-lg 
                                    transition-all duration-150 
                                    hover:shadow-md hover:translate-y-0.5 
                                    active:shadow-none active:translate-y-1 cursor-pointer"
                                style={({ isActive }) => ({ color: isActive ? 'darkgreen' : 'black' })} to="/login"><User className="w-6 h-6" /></NavLink>
                                <NavLink className="bg-blue-500/70 text-white px-6 py-2 rounded-lg shadow-lg 
                                    transition-all duration-150 
                                    hover:shadow-md hover:translate-y-0.5 
                                    active:shadow-none active:translate-y-1 cursor-pointer"
                                style={({ isActive }) => ({ color: isActive ? 'darkgreen' : 'black' })} to="/register"><UserPlus className="w-6 h-6" /></NavLink>
                            </>
                        )}
                    </div>
                </div>
                )}
            </nav>
            <hr className="border-gray-300 mt-2 pb-0" />
        </div>
    );
};

export default Navbar;