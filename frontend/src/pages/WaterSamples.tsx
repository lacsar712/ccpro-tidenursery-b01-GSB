import { FormEvent, useEffect, useState } from 'react'
import { api } from '../api/client'
import type { Pond, WaterSample } from '../types'

function nowLocal() {
  const d = new Date()
  d.setMinutes(d.getMinutes() - d.getTimezoneOffset())
  return d.toISOString().slice(0, 16)
}

function toLocalInput(iso: string) {
  const d = new Date(iso)
  d.setMinutes(d.getMinutes() - d.getTimezoneOffset())
  return d.toISOString().slice(0, 16)
}

type FormState = {
  pondId: number
  sampledAt: string
  depthM: number | ''
  transparencyCm: number | ''
  tempC: number
  salinityPpt: number
  doMgL: number
  ph: number
  notes: string
}

const empty: FormState = {
  pondId: 0,
  sampledAt: nowLocal(),
  depthM: '',
  transparencyCm: '',
  tempC: 26,
  salinityPpt: 28,
  doMgL: 6.5,
  ph: 8.0,
  notes: '',
}

const isComplete = (r: WaterSample) =>
  r.depthM !== null && r.transparencyCm !== null

export default function WaterSamples() {
  const [ponds, setPonds] = useState<Pond[]>([])
  const [rows, setRows] = useState<WaterSample[]>([])
  const [form, setForm] = useState<FormState>(empty)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [minDepthInput, setMinDepthInput] = useState('')
  const [minDepth, setMinDepth] = useState('')
  const [error, setError] = useState('')

  async function load(depth = minDepth) {
    // 不带深度参数时必须拿到默认全量结果；带参数时由后端按
    // 「两字段齐全且 depth_m >= 下限」过滤。
    const query = depth !== '' ? `?minDepth=${encodeURIComponent(depth)}` : ''
    const [ps, ws] = await Promise.all([
      api<Pond[]>('/api/ponds'),
      api<WaterSample[]>(`/api/water-samples${query}`),
    ])
    setPonds(ps)
    setRows(ws)
    if (!form.pondId && ps[0]) {
      setForm((f) => ({ ...f, pondId: ps[0].id }))
    }
  }

  useEffect(() => {
    load('').catch((e) => setError(e.message))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    const path =
      editingId === null
        ? '/api/water-samples'
        : `/api/water-samples/${editingId}`
    try {
      await api(path, {
        method: editingId === null ? 'POST' : 'PUT',
        body: JSON.stringify({
          ...form,
          // 空值显式传 null，由后端统一校验函数返回中文 400
          depthM: form.depthM === '' ? null : form.depthM,
          transparencyCm:
            form.transparencyCm === '' ? null : form.transparencyCm,
          sampledAt: new Date(form.sampledAt).toISOString(),
        }),
      })
      cancelEdit()
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存失败')
    }
  }

  function startEdit(r: WaterSample) {
    setError('')
    setEditingId(r.id)
    setForm({
      pondId: r.pondId,
      sampledAt: toLocalInput(r.sampledAt),
      // 历史缺字段行进入编辑时两字段留空，必须补齐才能保存
      depthM: r.depthM ?? '',
      transparencyCm: r.transparencyCm ?? '',
      tempC: r.tempC,
      salinityPpt: r.salinityPpt,
      doMgL: r.doMgL,
      ph: r.ph,
      notes: r.notes ?? '',
    })
  }

  function cancelEdit() {
    setEditingId(null)
    setForm((f) => ({ ...empty, pondId: f.pondId, sampledAt: nowLocal() }))
  }

  async function remove(id: number) {
    if (!confirm('确认删除该水质样？')) return
    try {
      await api(`/api/water-samples/${id}`, { method: 'DELETE' })
      if (editingId === id) cancelEdit()
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : '删除失败')
    }
  }

  function applyFilter(e: FormEvent) {
    e.preventDefault()
    setError('')
    setMinDepth(minDepthInput)
    load(minDepthInput).catch((e) => setError(e.message))
  }

  function clearFilter() {
    setMinDepthInput('')
    setMinDepth('')
    load('').catch((e) => setError(e.message))
  }

  const pondLabel = (id: number) => {
    const p = ponds.find((x) => x.id === id)
    return p ? `${p.pondCode} (${p.species})` : `#${id}`
  }

  const completeCount = rows.filter(isComplete).length

  return (
    <div>
      <header className="page-header">
        <h1>水质采样</h1>
        <p className="muted">
          采样深度 0.2–3 米；透明度 1–200 厘米正整数；两字段必须同时填写。
          历史缺字段行须先补齐才能更新。
        </p>
      </header>
      {error && <div className="error">{error}</div>}

      <form className="panel form-grid" onSubmit={onSubmit}>
        <label>
          塘口
          <select
            value={form.pondId}
            onChange={(e) => setForm({ ...form, pondId: Number(e.target.value) })}
            required
          >
            {ponds.map((p) => (
              <option key={p.id} value={p.id}>
                {p.pondCode} · {p.species}
              </option>
            ))}
          </select>
        </label>
        <label>
          采样时间
          <input
            type="datetime-local"
            value={form.sampledAt}
            onChange={(e) => setForm({ ...form, sampledAt: e.target.value })}
            required
          />
        </label>
        <label>
          采样深度 (米，0.2–3)
          <input
            type="number"
            min={0.2}
            max={3}
            step={0.1}
            value={form.depthM}
            onChange={(e) =>
              setForm({
                ...form,
                depthM: e.target.value === '' ? '' : Number(e.target.value),
              })
            }
            required
          />
        </label>
        <label>
          透明度 (厘米，1–200 整数)
          <input
            type="number"
            min={1}
            max={200}
            step={1}
            value={form.transparencyCm}
            onChange={(e) =>
              setForm({
                ...form,
                transparencyCm: e.target.value === '' ? '' : Number(e.target.value),
              })
            }
            required
          />
        </label>
        <label>
          水温 °C
          <input
            type="number"
            step="0.1"
            value={form.tempC}
            onChange={(e) => setForm({ ...form, tempC: Number(e.target.value) })}
            required
          />
        </label>
        <label>
          盐度 ppt
          <input
            type="number"
            step="0.1"
            value={form.salinityPpt}
            onChange={(e) => setForm({ ...form, salinityPpt: Number(e.target.value) })}
            required
          />
        </label>
        <label>
          溶解氧 mg/L
          <input
            type="number"
            step="0.1"
            value={form.doMgL}
            onChange={(e) => setForm({ ...form, doMgL: Number(e.target.value) })}
            required
          />
        </label>
        <label>
          pH
          <input
            type="number"
            step="0.1"
            value={form.ph}
            onChange={(e) => setForm({ ...form, ph: Number(e.target.value) })}
            required
          />
        </label>
        <label className="span-2">
          备注
          <input
            value={form.notes}
            onChange={(e) => setForm({ ...form, notes: e.target.value })}
          />
        </label>
        <div className="form-actions">
          <button type="submit" className="btn primary">
            {editingId === null ? '登记水质样' : '保存修改（须两字段齐全）'}
          </button>
          {editingId !== null && (
            <button type="button" className="btn ghost" onClick={cancelEdit}>
              取消编辑
            </button>
          )}
        </div>
      </form>

      <form className="panel filter-bar" onSubmit={applyFilter}>
        <label>
          深度下限过滤 (米)
          <input
            type="number"
            min={0.2}
            max={3}
            step={0.1}
            placeholder="留空 = 全量"
            value={minDepthInput}
            onChange={(e) => setMinDepthInput(e.target.value)}
          />
        </label>
        <button type="submit" className="btn primary">
          应用筛选
        </button>
        {minDepth !== '' && (
          <button type="button" className="btn ghost" onClick={clearFilter}>
            清除（恢复全量）
          </button>
        )}
        <span className="hint">
          当前可见 {rows.length} 条 · 深度/透明度齐全 {completeCount} 条
          {minDepth !== '' ? `（已按深度 ≥ ${minDepth} 米过滤）` : ''}
        </span>
      </form>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>塘口</th>
              <th>采样时间</th>
              <th>深度 (m)</th>
              <th>透明度 (cm)</th>
              <th>水温</th>
              <th>盐度</th>
              <th>DO</th>
              <th>pH</th>
              <th>备注</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id} className={isComplete(r) ? '' : 'row-incomplete'}>
                <td>{r.id}</td>
                <td>{pondLabel(r.pondId)}</td>
                <td>{new Date(r.sampledAt).toLocaleString()}</td>
                <td>{r.depthM ?? <span className="missing">缺失</span>}</td>
                <td>{r.transparencyCm ?? <span className="missing">缺失</span>}</td>
                <td>{r.tempC}</td>
                <td>{r.salinityPpt}</td>
                <td>{r.doMgL}</td>
                <td>{r.ph}</td>
                <td>{r.notes || '—'}</td>
                <td className="row-actions">
                  <button className="btn ghost" onClick={() => startEdit(r)}>
                    {isComplete(r) ? '编辑' : '补齐字段'}
                  </button>
                  <button className="btn ghost danger" onClick={() => remove(r.id)}>
                    删除
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
