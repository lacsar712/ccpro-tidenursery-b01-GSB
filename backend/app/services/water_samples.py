"""水质样「采样深度 + 透明度」的共享规则。

三处口径同源：
1. 新建（POST）与更新（PUT）都调用同一个 validate_depth_transparency()；
2. 列表深度下限过滤复用本模块的深度列与齐全口径；
3. 仪表盘近 24h 平均透明度只统计 complete_pair_condition() 选出的行。
"""

from typing import Optional

from sqlalchemy import and_

from app.models.water_sample import WaterSample

# 采样深度（米）合法区间
MIN_DEPTH_M = 0.2
MAX_DEPTH_M = 3.0
# 透明度（厘米）合法区间：正整数且不超过 200
MIN_TRANSPARENCY_CM = 1
MAX_TRANSPARENCY_CM = 200


def validate_depth_transparency(
    sampling_depth_m: Optional[float],
    transparency_cm: Optional[float],
) -> None:
    """新建与更新共用的同一校验函数。

    两字段必须同时有效：缺一或越界都抛出中文 ValueError（由路由层转为 400）。
    """
    if sampling_depth_m is None or transparency_cm is None:
        raise ValueError("采样深度（米）与透明度（厘米）必须同时填写")
    if sampling_depth_m < MIN_DEPTH_M or sampling_depth_m > MAX_DEPTH_M:
        raise ValueError(
            f"采样深度必须在 {MIN_DEPTH_M} 到 {MAX_DEPTH_M:g} 米之间"
        )
    if int(transparency_cm) != transparency_cm:
        raise ValueError("透明度必须为整数厘米")
    if (
        transparency_cm < MIN_TRANSPARENCY_CM
        or transparency_cm > MAX_TRANSPARENCY_CM
    ):
        raise ValueError(
            f"透明度必须为 {MIN_TRANSPARENCY_CM} 到 {MAX_TRANSPARENCY_CM} 厘米的整数"
        )


def complete_pair_condition():
    """「两字段齐全」的唯一口径：列表筛选与仪表盘均值共用。"""
    return and_(
        WaterSample.sampling_depth_m.is_not(None),
        WaterSample.transparency_cm.is_not(None),
    )
