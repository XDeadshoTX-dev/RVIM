import { Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { todoAPI } from '../api/api';

export default function PublicRoute({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(null);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        await todoAPI.getLists();
        setIsAuthenticated(true);
      } catch (error) {
        setIsAuthenticated(false);
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

  if (isAuthenticated) {
    return <Navigate to="/workspace" replace />;
  }

  return children;
}