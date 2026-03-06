import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Login from './components/Login'
import Layout from './components/Layout'
import Clients from './pages/Clients'
import Settings from './pages/Settings'
import Users from './pages/settings/Users'
import Groups from './pages/settings/Groups'
import Roles from './pages/settings/Roles'
import Tasks from './pages/Tasks'
import TaskTypes from './pages/settings/TaskTypes'
import ClientStatuses from './pages/settings/ClientStatuses'

function PrivateRoute({ children }) {
  const { user, loading } = useAuth()
  
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }
  
  return user ? children : <Navigate to="/login" />
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }
      >
        <Route index element={<Navigate to="/clients" replace />} />
        <Route path="clients" element={<Clients />} />
        <Route path="tasks" element={<Tasks />} />
        <Route path="settings" element={<Settings />}>
          <Route path="users" element={<Users />} />
          <Route path="groups" element={<Groups />} />
          <Route path="roles" element={<Roles />} />
          <Route path="task-types" element={<TaskTypes />} />
          <Route path="client-statuses" element={<ClientStatuses />} />
        </Route>
      </Route>
    </Routes>
  )
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppRoutes />
      </Router>
    </AuthProvider>
  )
}

export default App
