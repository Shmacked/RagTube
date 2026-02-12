import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import axios from 'axios';

// 1. Define what the "broadcast" contains
interface AuthContextType {
  user: any;
  loading: boolean;
  login: (userData: any) => Promise<void>;
  register: (userData: any) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// 2. The Provider component
export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 3. Check the cookie on mount by calling your backend
    axios.get('http://localhost:9002/users/', { 
        withCredentials: true // This is the "Passport" for your cookie
      }) // Your "check auth" endpoint
      .then(response => response.data)
      .then(data => {
        // console.log(data)
        setUser(data);
        setLoading(false);
      })
      .catch(error => {
        // console.error(error)
        setLoading(false)
      });
  }, []);

  const login = async (userData: any) => {
    try {
      const response = await axios.post('http://localhost:9002/users/login', userData, { withCredentials: true, headers: { 'Content-Type': 'application/json' } });
      setUser(response.data);
    } catch (error) {
      console.error("Login failed:", error);
    }
  };

  const register = async (userData: any) => {
    try {
      const response = await axios.post('http://localhost:9002/users/', userData, { withCredentials: true, headers: { 'Content-Type': 'application/json' } });
      setUser(response.data);
    } catch (error) {
      console.error("Register failed:", error);
    }
  };

  const logout = async () => {
    try {
      // 1. Tell FastAPI to clear the cookie
      await axios.post('http://localhost:9002/users/logout', {}, { 
        withCredentials: true 
      });
    } catch (error) {
      console.error("Logout failed:", error);
    } finally {
      // 2. Clear the local state regardless of server success
      // This sends the user back to a logged-out state in the UI
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// 4. A custom hook for easy access
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
};