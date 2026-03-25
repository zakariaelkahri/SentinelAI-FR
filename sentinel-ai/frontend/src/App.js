import React, { useState } from 'react';
import { BrowserRouter as Router, Navigate, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Predictions from './pages/Predictions';
import LiveStreams from './pages/LiveStreams';
import UsersManagement from './pages/UsersManagement';
import ManageCameras from './pages/ManageCameras';
import Params from './pages/Params';
import Login from './pages/Login';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import { AuthProvider } from './context/AuthContext';

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const toggleSidebar = () => {
    setIsSidebarOpen((previous) => !previous);
  };

  return (
    <AuthProvider>
      <Router>
        <div className={`app${isSidebarOpen ? '' : ' sidebar-hidden'}`}>
          <Navbar isSidebarOpen={isSidebarOpen} onToggleSidebar={toggleSidebar} />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Navigate to="/login" replace />} />
              <Route path="/login" element={<Login />} />
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute allowedRoles={['admin']} redirectTo="/live-streams">
                    <Dashboard />
                  </ProtectedRoute>
                }
              />
              <Route element={<ProtectedRoute />}>
                <Route path="/predictions" element={<Predictions />} />
                <Route path="/live-streams" element={<LiveStreams />} />
                <Route path="/users-management" element={<UsersManagement />} />
                <Route path="/manage-cameras" element={<ManageCameras />} />
                <Route path="/params" element={<Params />} />
              </Route>
              <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
