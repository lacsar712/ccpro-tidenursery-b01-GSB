from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DashboardStats(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    pond_total: int = Field(serialization_alias="pondTotal")
    quarantine_count: int = Field(serialization_alias="quarantineCount")
    samples_last_24h: int = Field(serialization_alias="samplesLast24h")
    feed_kg_last_7d: float = Field(serialization_alias="feedKgLast7d")
    # 近一天平均透明度（厘米），仅统计深度/透明度两字段齐全的行；
    # 无齐全行时为 None。sample_count 为参与均值的行数，
    # 必须与水质样列表中两字段齐全的可见行数一致。
    avg_transparency_last_24h: Optional[float] = Field(
        None, serialization_alias="avgTransparencyLast24h"
    )
    transparency_sample_count: int = Field(
        0, serialization_alias="transparencySampleCount"
    )
