import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { DashboardStats } from '../types'

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api<DashboardStats>('/api/dashboard/stats')
      .then(setStats)
      .catch((e) => setError(e.message))
  }, [])

  return (
    <div>
      <header className="page-header">
        <h1>运行看板</h1>
        <p className="muted">塘口状态 · 近 24h 采样 · 近 7 日投喂 · 近一天平均透明度</p>
      </header>
      {error && <div className="error">{error}</div>}
      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-label">塘口总数</div>
          <div className="stat-value">{stats?.pondTotal ?? '—'}</div>
        </div>
        <div className="stat-card warn">
          <div className="stat-label">隔离塘 (quarantine)</div>
          <div className="stat-value">{stats?.quarantineCount ?? '—'}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">近 24h 采样数</div>
          <div className="stat-value">{stats?.samplesLast24h ?? '—'}</div>
        </div>
        <div className="stat-card accent">
          <div className="stat-label">近 7 日投喂总量 (kg)</div>
          <div className="stat-value">
            {stats ? stats.feedKgLast7d.toFixed(2) : '—'}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">近一天平均透明度 (cm)</div>
          <div className="stat-value">
            {stats && stats.avgTransparencyLast24h !== null
              ? stats.avgTransparencyLast24h.toFixed(2)
              : '—'}
          </div>
          <div className="hint">
            参与均值 {stats?.transparencySampleCount ?? 0} 行（深度/透明度齐全）
          </div>
        </div>
      </div>
    </div>
  )
}
