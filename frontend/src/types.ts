export type User = {
  id: number
  username: string
  role: string
  display_name: string
}

export type Hatchery = {
  id: number
  name: string
  seawaterSource: string
  notes?: string | null
}

export type Pond = {
  id: number
  hatcheryId: number
  pondCode: string
  species: string
  volumeM3: number
  status: 'stocked' | 'dry' | 'quarantine'
}

export type WaterSample = {
  id: number
  pondId: number
  sampledAt: string
  tempC: number
  salinityPpt: number
  doMgL: number
  ph: number
  /** 采样深度（米，0.2–3）；历史行可空 */
  depthM: number | null
  /** 透明度（厘米，1–200 正整数）；历史行可空 */
  transparencyCm: number | null
  notes?: string | null
}

export type FeedEvent = {
  id: number
  pondId: number
  fedAt: string
  feedType: string
  amountKg: number
  operatorName: string
}

export type DashboardStats = {
  pondTotal: number
  quarantineCount: number
  samplesLast24h: number
  feedKgLast7d: number
  /** 近一天平均透明度（厘米），仅两字段齐全的行参与；无齐全行为 null */
  avgTransparencyLast24h: number | null
  /** 参与均值的行数，与列表两字段齐全行数同源 */
  transparencySampleCount: number
}
