import { Navigate, Outlet } from 'react-router';
import { useAuth } from '../context/auth_context';

const ProtectedRoute = () => {
  const { user, loading } = useAuth();

  // 1. The Loading State:
  // While we wait for the backend cookie check, we render nothing (or a spinner)
  // This prevents the "flash" of the login screen on refresh.
  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        <p className="ml-4">Verifying session...</p>
      </div>
    );
  }

  // 2. The Auth Check:
  // If loading is done and there is no user, redirect to login.
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // 3. Success:
  // If the user exists, render the nested route.
  return <Outlet />;
};

export default ProtectedRoute;