from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class WaterSample(Base):
    __tablename__ = "water_samples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    pond_id: Mapped[int] = mapped_column(ForeignKey("ponds.id"), nullable=False, index=True)
    sampled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    temp_c: Mapped[float] = mapped_column(Float, nullable=False)
    salinity_ppt: Mapped[float] = mapped_column(Float, nullable=False)
    do_mg_l: Mapped[float] = mapped_column(Float, nullable=False)
    ph: Mapped[float] = mapped_column(Float, nullable=False)
    # 采样深度（米，0.2–3）与透明度（厘米，1–200 正整数）必须同时有效。
    # 历史行允许为空，但任何更新都必须先补齐两字段。
    depth_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    transparency_cm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    pond: Mapped["Pond"] = relationship("Pond", back_populates="water_samples")
