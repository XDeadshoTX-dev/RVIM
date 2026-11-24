import { Navigate, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { todoAPI } from '../api/api';

export default function ProtectedRoute({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(null);
  const location = useLocation();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        await todoAPI.getLists();
        setIsAuthenticated(true);
      } catch (error) {
        if (error.response?.status === 401 || error.response?.status === 403) {
          setIsAuthenticated(false);
        } else {
          setIsAuthenticated(false);
        }
      }
    };
    checkAuth();
  }, []);

  if (isAuthenticated === null) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '18px',
        color: '#666'
      }}>
        Завантаження...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/log-in" state={{ from: location }} replace />;
  }

  return children;
}