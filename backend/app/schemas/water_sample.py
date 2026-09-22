from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WaterSampleCreate(BaseModel):
    pond_id: int = Field(..., alias="pondId")
    sampled_at: datetime = Field(..., alias="sampledAt")
    temp_c: float = Field(..., alias="tempC")
    salinity_ppt: float = Field(..., alias="salinityPpt")
    do_mg_l: float = Field(..., alias="doMgL")
    ph: float
    # 声明为可空仅为承接缺字段请求；范围与「同时有效」统一交给
    # app.services.water_quality.validate_depth_transparency 校验，
    # 新建与更新共用同一函数。
    depth_m: Optional[float] = Field(None, alias="depthM")
    # 用 float 承接，小数/越界也交由统一校验函数返回中文 400，
    # 避免 Pydantic 先抛英文类型错误。
    transparency_cm: Optional[float] = Field(None, alias="transparencyCm")
    notes: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("do_mg_l")
    @classmethod
    def validate_do(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("溶解氧 doMgL 必须大于 0")
        return v

    @field_validator("ph")
    @classmethod
    def validate_ph(cls, v: float) -> float:
        if v < 6 or v > 9:
            raise ValueError("pH 必须在 6 到 9 之间")
        return v


class WaterSampleUpdate(BaseModel):
    pond_id: Optional[int] = Field(None, alias="pondId")
    sampled_at: Optional[datetime] = Field(None, alias="sampledAt")
    temp_c: Optional[float] = Field(None, alias="tempC")
    salinity_ppt: Optional[float] = Field(None, alias="salinityPpt")
    do_mg_l: Optional[float] = Field(None, alias="doMgL")
    ph: Optional[float] = None
    depth_m: Optional[float] = Field(None, alias="depthM")
    # 用 float 承接，小数/越界也交由统一校验函数返回中文 400，
    # 避免 Pydantic 先抛英文类型错误。
    transparency_cm: Optional[float] = Field(None, alias="transparencyCm")
    notes: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("do_mg_l")
    @classmethod
    def validate_do(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("溶解氧 doMgL 必须大于 0")
        return v

    @field_validator("ph")
    @classmethod
    def validate_ph(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (v < 6 or v > 9):
            raise ValueError("pH 必须在 6 到 9 之间")
        return v


class WaterSampleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    pond_id: int = Field(serialization_alias="pondId")
    sampled_at: datetime = Field(serialization_alias="sampledAt")
    temp_c: float = Field(serialization_alias="tempC")
    salinity_ppt: float = Field(serialization_alias="salinityPpt")
    do_mg_l: float = Field(serialization_alias="doMgL")
    ph: float
    depth_m: Optional[float] = Field(None, serialization_alias="depthM")
    transparency_cm: Optional[int] = Field(None, serialization_alias="transparencyCm")
    notes: Optional[str] = None
