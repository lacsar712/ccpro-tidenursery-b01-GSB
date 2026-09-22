from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _validate_do(v: Optional[float]) -> Optional[float]:
    if v is not None and v <= 0:
        raise ValueError("溶解氧 doMgL 必须大于 0")
    return v


def _validate_ph(v: Optional[float]) -> Optional[float]:
    if v is not None and (v < 6 or v > 9):
        raise ValueError("pH 必须在 6 到 9 之间")
    return v


class WaterSampleCreate(BaseModel):
    pond_id: int = Field(..., alias="pondId")
    sampled_at: datetime = Field(..., alias="sampledAt")
    temp_c: float = Field(..., alias="tempC")
    salinity_ppt: float = Field(..., alias="salinityPpt")
    do_mg_l: float = Field(..., alias="doMgL")
    ph: float
    # 采样深度（米）与透明度（厘米）：是否齐全/越界由路由层调用
    # app.services.water_samples.validate_depth_transparency 统一校验（与更新同一函数）
    sampling_depth_m: Optional[float] = Field(None, alias="samplingDepthM")
    transparency_cm: Optional[float] = Field(None, alias="transparencyCm")
    notes: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("do_mg_l")
    @classmethod
    def validate_do(cls, v: float) -> float:
        return _validate_do(v)  # type: ignore[return-value]

    @field_validator("ph")
    @classmethod
    def validate_ph(cls, v: float) -> float:
        return _validate_ph(v)  # type: ignore[return-value]


class WaterSampleUpdate(BaseModel):
    """局部更新：字段均可选；提交后由路由层合并现有值，

    并调用与新建相同的 validate_depth_transparency 校验，
    历史缺字段行必须补齐两字段才能保存。"""

    pond_id: Optional[int] = Field(None, alias="pondId")
    sampled_at: Optional[datetime] = Field(None, alias="sampledAt")
    temp_c: Optional[float] = Field(None, alias="tempC")
    salinity_ppt: Optional[float] = Field(None, alias="salinityPpt")
    do_mg_l: Optional[float] = Field(None, alias="doMgL")
    ph: Optional[float] = None
    sampling_depth_m: Optional[float] = Field(None, alias="samplingDepthM")
    transparency_cm: Optional[float] = Field(None, alias="transparencyCm")
    notes: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("do_mg_l")
    @classmethod
    def validate_do(cls, v: Optional[float]) -> Optional[float]:
        return _validate_do(v)

    @field_validator("ph")
    @classmethod
    def validate_ph(cls, v: Optional[float]) -> Optional[float]:
        return _validate_ph(v)


class WaterSampleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    pond_id: int = Field(serialization_alias="pondId")
    sampled_at: datetime = Field(serialization_alias="sampledAt")
    temp_c: float = Field(serialization_alias="tempC")
    salinity_ppt: float = Field(serialization_alias="salinityPpt")
    do_mg_l: float = Field(serialization_alias="doMgL")
    ph: float
    # 历史行读取可空
    sampling_depth_m: Optional[float] = Field(None, serialization_alias="samplingDepthM")
    transparency_cm: Optional[int] = Field(None, serialization_alias="transparencyCm")
    notes: Optional[str] = None
