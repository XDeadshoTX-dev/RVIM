import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import SignUp from './pages/SignUp';
import LogIn from './pages/LogIn';
import Workspace from './pages/Workspace';
import ProtectedRoute from './components/ProtectedRoute';
import PublicRoute from './components/PublicRoute';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/log-in" replace />} />
        
        <Route 
          path="/sign-up" 
          element={
            <PublicRoute>
              <SignUp />
            </PublicRoute>
          } 
        />
        
        <Route 
          path="/log-in" 
          element={
            <PublicRoute>
              <LogIn />
            </PublicRoute>
          } 
        />
        
        <Route 
          path="/workspace" 
          element={
            <ProtectedRoute>
              <Workspace />
            </ProtectedRoute>
          } 
        />
        
        <Route path="*" element={<Navigate to="/log-in" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;