import React, { useState } from 'react';
import { BrowserRouter as Router, Navigate, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import LiveStreams from './pages/LiveStreams';
import UsersManagement from './pages/UsersManagement';
import ManageCameras from './pages/ManageCameras';
import Params from './pages/Params';
import SecurityAssistant from './pages/SecurityAssistant';
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
                  <ProtectedRoute allowedRoles={['admin', 'supervisor']} redirectTo="/live-streams">
                    <Dashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/assistant"
                element={
                  <ProtectedRoute allowedRoles={['operator', 'supervisor']} redirectTo="/live-streams">
                    <SecurityAssistant />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/users-management"
                element={
                  <ProtectedRoute allowedRoles={['admin']} redirectTo="/live-streams">
                    <UsersManagement />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/manage-cameras"
                element={
                  <ProtectedRoute allowedRoles={['admin', 'supervisor']} redirectTo="/live-streams">
                    <ManageCameras />
                  </ProtectedRoute>
                }
              />
              <Route element={<ProtectedRoute />}>
                <Route path="/live-streams" element={<LiveStreams />} />
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
