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
from app.services.water_quality import (
    complete_sample_conditions,
    validate_depth_transparency,
)

router = APIRouter(prefix="/api/water-samples", tags=["water-samples"])


def _validate_depth_transparency_or_400(depth_m, transparency_cm):
    """调用统一校验函数，ValueError 统一转 400 中文。"""
    try:
        return validate_depth_transparency(depth_m, transparency_cm)
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
        # 仅对两字段齐全的行参与深度比较，历史缺字段行不会因过滤而
        # 把默认全量结果污染为空（它们仍按非齐全行正常展示/排除口径一致）。
        depth_ok, transparency_ok = complete_sample_conditions()
        q = q.filter(depth_ok, transparency_ok, WaterSample.depth_m >= min_depth)
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
    # 新建与更新共用同一校验函数。
    depth_m, transparency_cm = _validate_depth_transparency_or_400(
        payload.depth_m, payload.transparency_cm
    )
    item = WaterSample(
        pond_id=payload.pond_id,
        sampled_at=payload.sampled_at,
        temp_c=payload.temp_c,
        salinity_ppt=payload.salinity_ppt,
        do_mg_l=payload.do_mg_l,
        ph=payload.ph,
        depth_m=depth_m,
        transparency_cm=transparency_cm,
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

    data = payload.model_dump(exclude_unset=True)
    if "pond_id" in data:
        pond = db.query(Pond).filter(Pond.id == data["pond_id"]).first()
        if not pond:
            raise HTTPException(status_code=400, detail="塘口不存在")

    # 更新路径同样必须两字段齐全：先与历史行现值合并，再调用同一校验函数。
    # 历史行缺字段、且本次未补齐时，这里直接 400，不允许以可空状态落库。
    effective_depth = data["depth_m"] if "depth_m" in data else item.depth_m
    effective_transparency = (
        data["transparency_cm"]
        if "transparency_cm" in data
        else item.transparency_cm
    )
    depth_m, transparency_cm = _validate_depth_transparency_or_400(
        effective_depth, effective_transparency
    )
    data["depth_m"] = depth_m
    data["transparency_cm"] = transparency_cm

    for k, v in data.items():
        setattr(item, k, v)
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
