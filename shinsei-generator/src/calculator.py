"""建築面積・比率の計算モジュール"""


def calc_total_floor_area(floors: list) -> float:
    """延べ床面積を計算する。

    Args:
        floors: 各階データのリスト。各要素は {"階": str, "床面積": float} の形式。

    Returns:
        延べ床面積（㎡）
    """
    return sum(floor["床面積"] for floor in floors)


def calc_kenpei_ratio(building_area: float, site_area: float) -> float:
    """建蔽率を計算する（建築面積 ÷ 敷地面積 × 100）。

    Args:
        building_area: 建築面積（㎡）
        site_area: 敷地面積（㎡）

    Returns:
        建蔽率（%）、小数点以下2桁
    """
    return round(building_area / site_area * 100, 2)


def calc_yoseki_ratio(total_floor_area: float, site_area: float) -> float:
    """容積率を計算する（延べ床面積 ÷ 敷地面積 × 100）。

    Args:
        total_floor_area: 延べ床面積（㎡）
        site_area: 敷地面積（㎡）

    Returns:
        容積率（%）、小数点以下2桁
    """
    return round(total_floor_area / site_area * 100, 2)
