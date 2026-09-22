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

// 采样深度（米）与透明度（厘米）在表单里用字符串保存，空串表示未填，
// 配合 required 强制填写；提交时再转数值。
const empty = {
  pondId: 0,
  sampledAt: nowLocal(),
  tempC: 26,
  salinityPpt: 28,
  doMgL: 6.5,
  ph: 8.0,
  samplingDepthM: '',
  transparencyCm: '',
  notes: '',
}

export default function WaterSamples() {
  const [ponds, setPonds] = useState<Pond[]>([])
  const [rows, setRows] = useState<WaterSample[]>([])
  const [form, setForm] = useState(empty)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [minDepth, setMinDepth] = useState('')
  const [error, setError] = useState('')

  async function load() {
    const params = new URLSearchParams()
    const d = parseFloat(minDepth)
    // 仅在显式填写合法深度下限时带过滤参数；清空即恢复默认全量列表
    if (minDepth.trim() !== '' && !Number.isNaN(d)) {
      params.set('minDepth', String(d))
    }
    const qs = params.toString()
    const [ps, ws] = await Promise.all([
      api<Pond[]>('/api/ponds'),
      api<WaterSample[]>(`/api/water-samples${qs ? `?${qs}` : ''}`),
    ])
    setPonds(ps)
    setRows(ws)
    if (!form.pondId && ps[0]) {
      setForm((f) => ({ ...f, pondId: ps[0].id }))
    }
  }

  useEffect(() => {
    load().catch((e) => setError(e.message))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [minDepth])

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    const payload = {
      ...form,
      sampledAt: new Date(form.sampledAt).toISOString(),
      samplingDepthM: Number(form.samplingDepthM),
      transparencyCm: Number(form.transparencyCm),
    }
    try {
      if (editingId) {
        await api(`/api/water-samples/${editingId}`, {
          method: 'PUT',
          body: JSON.stringify(payload),
        })
      } else {
        await api('/api/water-samples', {
          method: 'POST',
          body: JSON.stringify(payload),
        })
      }
      setForm((f) => ({ ...empty, pondId: f.pondId, sampledAt: nowLocal() }))
      setEditingId(null)
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
      tempC: r.tempC,
      salinityPpt: r.salinityPpt,
      doMgL: r.doMgL,
      ph: r.ph,
      // 历史缺字段行载入为空，必须补齐两字段才能保存
      samplingDepthM: r.samplingDepthM == null ? '' : String(r.samplingDepthM),
      transparencyCm: r.transparencyCm == null ? '' : String(r.transparencyCm),
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

  const pondLabel = (id: number) => {
    const p = ponds.find((x) => x.id === id)
    return p ? `${p.pondCode} (${p.species})` : `#${id}`
  }

  // 与后端 complete_pair_condition 同一口径：两字段均非空即齐全
  const completeCount = rows.filter(
    (r) => r.samplingDepthM != null && r.transparencyCm != null,
  ).length

  return (
    <div>
      <header className="page-header">
        <h1>水质采样</h1>
        <p className="muted">
          校验：溶解氧 doMgL &gt; 0，pH ∈ [6, 9]；采样深度 0.2–3 米，透明度 1–200
          厘米（整数），两字段必须同时填写
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
        <label>
          采样深度 m（0.2–3）
          <input
            type="number"
            step="0.1"
            min="0.2"
            max="3"
            placeholder="如 0.5"
            value={form.samplingDepthM}
            onChange={(e) => setForm({ ...form, samplingDepthM: e.target.value })}
            required
          />
        </label>
        <label>
          透明度 cm（1–200 整数）
          <input
            type="number"
            step="1"
            min="1"
            max="200"
            placeholder="如 40"
            value={form.transparencyCm}
            onChange={(e) => setForm({ ...form, transparencyCm: e.target.value })}
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
        <button type="submit" className="btn primary">
          {editingId ? `保存修改 #${editingId}` : '登记水质样'}
        </button>
        {editingId && (
          <button type="button" className="btn ghost" onClick={cancelEdit}>
            取消编辑
          </button>
        )}
      </form>

      <div className="panel">
        <label>
          深度下限过滤（米，留空显示全部）
          <input
            type="number"
            step="0.1"
            min="0"
            placeholder="如 0.5"
            value={minDepth}
            onChange={(e) => setMinDepth(e.target.value)}
          />
        </label>
        <p className="muted">
          本页共 {rows.length} 条 · 两字段齐全 {completeCount} 条
        </p>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>塘口</th>
              <th>采样时间</th>
              <th>水温</th>
              <th>盐度</th>
              <th>DO</th>
              <th>pH</th>
              <th>深度(m)</th>
              <th>透明度(cm)</th>
              <th>备注</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td>{r.id}</td>
                <td>{pondLabel(r.pondId)}</td>
                <td>{new Date(r.sampledAt).toLocaleString()}</td>
                <td>{r.tempC}</td>
                <td>{r.salinityPpt}</td>
                <td>{r.doMgL}</td>
                <td>{r.ph}</td>
                <td>{r.samplingDepthM ?? '—'}</td>
                <td>{r.transparencyCm ?? '—'}</td>
                <td>{r.notes || '—'}</td>
                <td>
                  <button className="btn ghost" onClick={() => startEdit(r)}>
                    编辑
                  </button>
                  <button className="btn ghost" onClick={() => remove(r.id)}>
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
