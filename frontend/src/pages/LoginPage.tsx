import React from 'react'
import { Box, Button, Paper, Stack, TextField, Typography, Alert } from '@mui/material'
import { api } from '../api'

const LoginPage: React.FC<{ onLogin: (token: string) => void }> = ({ onLogin }) => {
  const [email, setEmail] = React.useState('admin@example.com')
  const [password, setPassword] = React.useState('admin123')
  const [error, setError] = React.useState<string | null>(null)

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    try {
      const res = await api.post('/auth/login', { email, password })
      onLogin(res.data.access_token)
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Login failed')
    }
  }

  return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
      <Paper sx={{ p: 4, minWidth: 360 }}>
        <Typography variant="h6" gutterBottom>Login</Typography>
        <form onSubmit={submit}>
          <Stack spacing={2}>
            <TextField label="Email" value={email} onChange={e => setEmail(e.target.value)} fullWidth />
            <TextField label="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} fullWidth />
            {error && <Alert severity="error">{error}</Alert>}
            <Button type="submit" variant="contained">Sign in</Button>
          </Stack>
        </form>
      </Paper>
    </Box>
  )
}

export default LoginPage
