"""入力データのバリデーションモジュール"""


def validate(data: dict) -> list[str]:
    """入力データを検証し、エラーメッセージのリストを返す。

    Args:
        data: YAMLから読み込んだ辞書データ

    Returns:
        エラーメッセージのリスト。空リストの場合はバリデーション通過。
    """
    errors = []

    # 必須チェック：建築主.氏名
    owner = data.get("建築主", {})
    if not owner.get("氏名"):
        errors.append("建築主.氏名 は必須です")

    # 必須チェック：敷地.敷地面積
    site = data.get("敷地", {})
    site_area = site.get("敷地面積")
    if site_area is None:
        errors.append("敷地.敷地面積 は必須です")
    elif not isinstance(site_area, (int, float)) or site_area <= 0:
        errors.append("敷地.敷地面積 は正の数である必要があります")

    # 必須チェック：建築面積
    building_area = data.get("建築面積")
    if building_area is None:
        errors.append("建築面積 は必須です")
    elif not isinstance(building_area, (int, float)) or building_area <= 0:
        errors.append("建築面積 は正の数である必要があります")

    # 必須チェック：各階
    floors = data.get("各階")
    if not floors:
        errors.append("各階 は必須です（少なくとも1階分が必要）")
    else:
        for i, floor in enumerate(floors):
            floor_area = floor.get("床面積")
            floor_name = floor.get("階", f"{i+1}階目")
            if floor_area is None:
                errors.append(f"各階[{floor_name}].床面積 は必須です")
            elif not isinstance(floor_area, (int, float)) or floor_area <= 0:
                errors.append(f"各階[{floor_name}].床面積 は正の数である必要があります")

    return errors
