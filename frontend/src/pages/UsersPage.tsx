import React from 'react'
import { Alert, Box, Button, Dialog, DialogActions, DialogContent, DialogTitle, FormControlLabel, Switch, Stack, TextField, Typography, Checkbox, FormGroup } from '@mui/material'
import { api, Dataset } from '../api'

interface User { id: number; email: string; full_name?: string; is_active: boolean; is_admin: boolean }

const UsersPage: React.FC = () => {
  const [users, setUsers] = React.useState<User[]>([])
  const [datasets, setDatasets] = React.useState<Dataset[]>([])
  const [open, setOpen] = React.useState(false)
  const [form, setForm] = React.useState({ email: '', full_name: '', password: '', is_admin: false, is_active: true, dataset_ids: [] as number[] })
  const [error, setError] = React.useState<string | null>(null)

  const load = () => {
    Promise.all([api.get('/users'), api.get('/datasets')]).then(([u, d]) => { setUsers(u.data); setDatasets(d.data) }).catch(e => setError(e?.response?.data?.detail || 'Failed to load'))
  }
  React.useEffect(() => { load() }, [])

  const createUser = async () => {
    setError(null)
    try {
      await api.post('/users', form)
      setOpen(false)
      setForm({ email: '', full_name: '', password: '', is_admin: false, is_active: true, dataset_ids: [] })
      load()
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Create failed')
    }
  }

  const toggleDataset = (id: number) => {
    setForm(f => ({ ...f, dataset_ids: f.dataset_ids.includes(id) ? f.dataset_ids.filter(x => x !== id) : [...f.dataset_ids, id] }))
  }

  return (
    <Stack spacing={2}>
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h6">Users</Typography>
        <Button variant="contained" onClick={() => setOpen(true)}>Add User</Button>
      </Box>
      {error && <Alert severity="error">{error}</Alert>}
      <Stack spacing={1}>
        {users.map(u => (
          <Box key={u.id} sx={{ border: '1px solid #eee', borderRadius: 1, p: 2 }}>
            <Typography variant="subtitle1">{u.email}</Typography>
            <Typography variant="body2" color="text.secondary">{u.full_name || '—'} | {u.is_admin ? 'Admin' : 'User'} | {u.is_active ? 'Active' : 'Inactive'}</Typography>
          </Box>
        ))}
      </Stack>

      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>New User</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField label="Email" value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} fullWidth />
            <TextField label="Full name" value={form.full_name} onChange={e => setForm(f => ({ ...f, full_name: e.target.value }))} fullWidth />
            <TextField label="Password" type="password" value={form.password} onChange={e => setForm(f => ({ ...f, password: e.target.value }))} fullWidth />
            <FormControlLabel control={<Switch checked={form.is_admin} onChange={e => setForm(f => ({ ...f, is_admin: e.target.checked }))} />} label="Admin" />
            <FormControlLabel control={<Switch checked={form.is_active} onChange={e => setForm(f => ({ ...f, is_active: e.target.checked }))} />} label="Active" />
            <Typography variant="subtitle2">Dataset access</Typography>
            <FormGroup>
              {datasets.map(d => (
                <FormControlLabel key={d.id} control={<Checkbox checked={form.dataset_ids.includes(d.id)} onChange={() => toggleDataset(d.id)} />} label={d.name} />
              ))}
            </FormGroup>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={createUser}>Create</Button>
        </DialogActions>
      </Dialog>
    </Stack>
  )
}

export default UsersPage
