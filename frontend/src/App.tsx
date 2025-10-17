import React from 'react'
import { Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom'
import { AppBar, Toolbar, Typography, Button, Container } from '@mui/material'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import UsersPage from './pages/UsersPage'

function useAuth() {
  const [token, setToken] = React.useState<string | null>(() => localStorage.getItem('token'))
  const navigate = useNavigate()
  const login = (t: string) => { localStorage.setItem('token', t); setToken(t); navigate('/') }
  const logout = () => { localStorage.removeItem('token'); setToken(null); navigate('/login') }
  return { token, login, logout }
}

const Layout: React.FC<{ children: React.ReactNode, logout: () => void }> = ({ children, logout }) => (
  <>
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>Data Quality Dashboard</Typography>
        <Button color="inherit" component={Link} to="/">Dashboard</Button>
        <Button color="inherit" component={Link} to="/users">Users</Button>
        <Button color="inherit" onClick={logout}>Logout</Button>
      </Toolbar>
    </AppBar>
    <Container sx={{ mt: 3 }}>
      {children}
    </Container>
  </>
)

const App: React.FC = () => {
  const { token, login, logout } = useAuth()
  return (
    <Routes>
      <Route path="/login" element={<LoginPage onLogin={login} />} />
      <Route path="/" element={token ? <Layout logout={logout}><DashboardPage/></Layout> : <Navigate to="/login" />} />
      <Route path="/users" element={token ? <Layout logout={logout}><UsersPage/></Layout> : <Navigate to="/login" />} />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  )
}

export default App
