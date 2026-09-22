"""水质样「采样深度 / 透明度」统一口径。

新建与更新必须共用 validate_depth_transparency；
列表筛选与仪表盘均值必须共用 complete_sample_conditions，
避免三处各算各的。
"""
from typing import Tuple

from app.models.water_sample import WaterSample

DEPTH_MIN_M = 0.2
DEPTH_MAX_M = 3.0
TRANSPARENCY_MIN_CM = 1
TRANSPARENCY_MAX_CM = 200


def validate_depth_transparency(depth_m, transparency_cm) -> Tuple[float, int]:
    """校验采样深度（米）与透明度（厘米）必须同时有效。

    - 采样深度：0.2 到 3 米之间
    - 透明度：1 到 200 之间的正整数
    - 缺任一字段或越界均抛 ValueError（中文），由路由转 400

    返回归一化后的 (depth_m, transparency_cm)。
    """
    if depth_m is None or transparency_cm is None:
        raise ValueError(
            "采样深度（米，0.2–3）与透明度（厘米，1–200 的正整数）必须同时填写"
        )

    try:
        depth = float(depth_m)
    except (TypeError, ValueError):
        raise ValueError("采样深度须为 0.2 到 3 米之间的数值")
    if not (DEPTH_MIN_M <= depth <= DEPTH_MAX_M):
        raise ValueError("采样深度须在 0.2 到 3 米之间")

    try:
        transparency = float(transparency_cm)
    except (TypeError, ValueError):
        raise ValueError("透明度须为 1 到 200 厘米之间的正整数")
    if not transparency.is_integer():
        raise ValueError("透明度须为正整数（厘米），不接受小数")
    if not (TRANSPARENCY_MIN_CM <= transparency <= TRANSPARENCY_MAX_CM):
        raise ValueError("透明度须为 1 到 200 厘米之间的正整数")

    return depth, int(transparency)


def complete_sample_conditions():
    """两字段齐全（均非空）的 SQLAlchemy 条件。

    列表深度过滤后的齐全判定与仪表盘均值统计共用此口径。
    """
    return (
        WaterSample.depth_m.isnot(None),
        WaterSample.transparency_cm.isnot(None),
    )
