from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DashboardStats(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    pond_total: int = Field(serialization_alias="pondTotal")
    quarantine_count: int = Field(serialization_alias="quarantineCount")
    samples_last_24h: int = Field(serialization_alias="samplesLast24h")
    feed_kg_last_7d: float = Field(serialization_alias="feedKgLast7d")
    # 近 24h 平均透明度（厘米）：只统计采样深度与透明度两字段齐全的行；
    # 无齐全行时为 null。transparency_rows_last_24h 为参与均值的行数。
    avg_transparency_cm_last_24h: Optional[float] = Field(
        None, serialization_alias="avgTransparencyCmLast24h"
    )
    transparency_rows_last_24h: int = Field(
        0, serialization_alias="transparencyRowsLast24h"
    )
