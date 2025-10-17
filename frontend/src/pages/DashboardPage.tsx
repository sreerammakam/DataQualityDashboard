import React from 'react'
import { Alert, Box, Card, CardContent, FormControl, InputLabel, MenuItem, Select, Stack, Typography } from '@mui/material'
import { api, Dataset, DimensionSummary, Timeseries } from '../api'
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const DashboardPage: React.FC = () => {
  const [datasets, setDatasets] = React.useState<Dataset[]>([])
  const [datasetId, setDatasetId] = React.useState<number | ''>('' as any)
  const [summary, setSummary] = React.useState<DimensionSummary[] | null>(null)
  const [series, setSeries] = React.useState<Timeseries[] | null>(null)
  const [error, setError] = React.useState<string | null>(null)

  React.useEffect(() => {
    api.get('/datasets').then(r => setDatasets(r.data)).catch(e => setError(e?.response?.data?.detail || 'Failed to load datasets'))
  }, [])

  React.useEffect(() => {
    if (!datasetId) return
    setError(null)
    Promise.all([
      api.get('/metrics/latest', { params: { dataset_id: datasetId } }),
      api.get('/metrics/timeseries', { params: { dataset_id: datasetId } })
    ]).then(([s, t]) => {
      setSummary(s.data)
      setSeries(t.data)
    }).catch(e => setError(e?.response?.data?.detail || 'Failed to load metrics'))
  }, [datasetId])

  return (
    <Stack spacing={3}>
      <FormControl sx={{ minWidth: 240 }}>
        <InputLabel>Dataset</InputLabel>
        <Select label="Dataset" value={datasetId} onChange={e => setDatasetId(Number(e.target.value))}>
          {datasets.map(d => <MenuItem key={d.id} value={d.id}>{d.name}</MenuItem>)}
        </Select>
      </FormControl>

      {error && <Alert severity="error">{error}</Alert>}

      {summary && (
        <Box display="grid" gridTemplateColumns={{ xs: '1fr', md: 'repeat(3, 1fr)'}} gap={2}>
          {summary.map(s => (
            <Card key={s.dimension}>
              <CardContent>
                <Typography variant="subtitle2">{s.dimension}</Typography>
                <Typography variant="h5">{s.latest_value == null ? '—' : s.latest_value.toFixed(3)}</Typography>
                <Typography color="text.secondary" variant="caption">{s.latest_at ? new Date(s.latest_at).toLocaleString() : 'No data'}</Typography>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}

      {series && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Metrics over time</Typography>
            <Box sx={{ width: '100%', height: 360 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart>
                  <CartesianGrid stroke="#eee" strokeDasharray="5 5" />
                  <XAxis dataKey="recorded_at" type="category" allowDuplicatedCategory={false} />
                  <YAxis domain={[0, 1]} />
                  <Tooltip />
                  <Legend />
                  {series.map(s => (
                    <Line key={s.metric_name} name={s.metric_name} data={s.points.map(p => ({...p, recorded_at: new Date(p.recorded_at).toLocaleString()}))} dataKey="value" type="monotone" dot={false} />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </CardContent>
        </Card>
      )}
    </Stack>
  )
}

export default DashboardPage
