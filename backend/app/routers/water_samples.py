from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.pond import Pond
from app.models.user import User
from app.models.water_sample import WaterSample
from app.schemas.water_sample import (
    WaterSampleCreate,
    WaterSampleOut,
    WaterSampleUpdate,
)
from app.services.water_samples import validate_depth_transparency

router = APIRouter(prefix="/api/water-samples", tags=["water-samples"])


def _check_depth_transparency(depth: Optional[float], transparency: Optional[float]) -> None:
    """新建与更新共用的同一校验入口：缺一或越界一律 400 中文。"""
    try:
        validate_depth_transparency(depth, transparency)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("", response_model=List[WaterSampleOut])
def list_samples(
    pond_id: Optional[int] = Query(None, alias="pondId"),
    min_depth: Optional[float] = Query(None, alias="minDepth"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(WaterSample)
    if pond_id is not None:
        q = q.filter(WaterSample.pond_id == pond_id)
    if min_depth is not None:
        # 深度下限过滤只在显式传参时启用；缺字段的历史行（NULL）自然被排除，
        # 不传 minDepth 时仍返回默认全量结果。
        q = q.filter(WaterSample.sampling_depth_m >= min_depth)
    return q.order_by(WaterSample.sampled_at.desc()).all()


@router.post("", response_model=WaterSampleOut, status_code=status.HTTP_201_CREATED)
def create_sample(
    payload: WaterSampleCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    pond = db.query(Pond).filter(Pond.id == payload.pond_id).first()
    if not pond:
        raise HTTPException(status_code=400, detail="塘口不存在")
    _check_depth_transparency(payload.sampling_depth_m, payload.transparency_cm)
    item = WaterSample(
        pond_id=payload.pond_id,
        sampled_at=payload.sampled_at,
        temp_c=payload.temp_c,
        salinity_ppt=payload.salinity_ppt,
        do_mg_l=payload.do_mg_l,
        ph=payload.ph,
        sampling_depth_m=payload.sampling_depth_m,
        transparency_cm=int(payload.transparency_cm),
        notes=payload.notes,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{sample_id}", response_model=WaterSampleOut)
def update_sample(
    sample_id: int,
    payload: WaterSampleUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    item = db.query(WaterSample).filter(WaterSample.id == sample_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="水质样不存在")
    updates = payload.model_dump(exclude_unset=True)
    if "pond_id" in updates:
        pond = db.query(Pond).filter(Pond.id == updates["pond_id"]).first()
        if not pond:
            raise HTTPException(status_code=400, detail="塘口不存在")
    for field, value in updates.items():
        setattr(item, field, value)
    # 与新建调用同一校验函数：合并后的结果必须两字段齐全且合法，
    # 历史缺字段行不补齐、或把任一字段置空，都不允许保存。
    _check_depth_transparency(item.sampling_depth_m, item.transparency_cm)
    item.transparency_cm = int(item.transparency_cm)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{sample_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sample(
    sample_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    item = db.query(WaterSample).filter(WaterSample.id == sample_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="水质样不存在")
    db.delete(item)
    db.commit()
