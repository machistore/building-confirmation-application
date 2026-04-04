"""新規案件 対話入力スクリプト

使い方:
    python src/new_project.py

実行すると対話形式で質問が表示され、
input/{案件番号}.yaml が生成される。
生成後に python src/generator.py {案件番号} を実行するか確認する。
"""

import re
import sys
import subprocess
from pathlib import Path

import yaml


BASE_DIR = Path(__file__).parent.parent
INPUT_DIR = BASE_DIR / "input"


# ============================================================
# 入力ユーティリティ
# ============================================================

def ask(prompt: str, required: bool = False, default: str = None) -> str | None:
    """テキスト入力を求める。required=True かつ空の場合は再入力を促す。"""
    while True:
        suffix = f"（デフォルト: {default}）" if default is not None else ""
        answer = input(f"  {prompt}{suffix}: ").strip()
        if not answer:
            if required:
                print("    ※ この項目は必須です。入力してください。")
                continue
            return default
        return answer


def ask_float(prompt: str, required: bool = False, default: float = None) -> float | None:
    """数値（小数可）の入力を求める。"""
    while True:
        suffix = f"（デフォルト: {default}）" if default is not None else ""
        answer = input(f"  {prompt}{suffix}: ").strip()
        if not answer:
            if required:
                print("    ※ この項目は必須です。数値を入力してください。")
                continue
            return default
        try:
            return float(answer)
        except ValueError:
            print("    ※ 数値を入力してください（例: 165.00）。")


def ask_int(prompt: str, required: bool = False, default: int = None) -> int | None:
    """整数の入力を求める。"""
    while True:
        suffix = f"（デフォルト: {default}）" if default is not None else ""
        answer = input(f"  {prompt}{suffix}: ").strip()
        if not answer:
            if required:
                print("    ※ この項目は必須です。整数を入力してください。")
                continue
            return default
        try:
            return int(answer)
        except ValueError:
            print("    ※ 整数を入力してください（例: 40）。")


def ask_postal(prompt: str, required: bool = False) -> str | None:
    """郵便番号（XXX-XXXX 形式）の入力を求める。"""
    while True:
        answer = input(f"  {prompt}（例: 150-0001）: ").strip()
        if not answer:
            if required:
                print("    ※ この項目は必須です。")
                continue
            return None
        if re.fullmatch(r"\d{3}-\d{4}", answer):
            return answer
        print("    ※ XXX-XXXX 形式で入力してください（例: 150-0001）。")


def ask_yesno(prompt: str, default_yes: bool = True) -> bool:
    """Y/n または y/N の入力を求める。"""
    suffix = "[Y/n]" if default_yes else "[y/N]"
    while True:
        answer = input(f"  {prompt} {suffix}: ").strip().lower()
        if not answer:
            return default_yes
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("    ※ y または n を入力してください。")


def ask_choice(prompt: str, choices: list, default_key: str = None) -> str:
    """選択肢から選ばせる。choices は [(キー, 表示名), ...] のリスト。"""
    for key, label in choices:
        marker = " ← デフォルト" if key == default_key else ""
        print(f"    {key}: {label}{marker}")
    choice_map = dict(choices)
    while True:
        answer = input(f"  {prompt}: ").strip()
        if not answer and default_key:
            return choice_map[default_key]
        if answer in choice_map:
            return choice_map[answer]
        keys = "/".join(k for k, _ in choices)
        print(f"    ※ {keys} のいずれかを入力してください。")


def section(title: str) -> None:
    print(f"\n── {title} ──")


# ============================================================
# 建築士情報（設計者・代理者・工事監理者 共通）
# ============================================================

ARCHITECT_TYPES = [
    ("1", "一級建築士"),
    ("2", "二級建築士"),
    ("3", "木造建築士"),
]


def ask_architect_info() -> dict:
    """建築士情報（種別・登録番号・氏名・事務所など）を対話入力する。"""
    print("  建築士種別:")
    kind = ask_choice("  番号を入力", ARCHITECT_TYPES)
    reg_no = ask("登録番号", required=True)
    name = ask("氏名", required=True)
    office = ask("建築士事務所名", required=True)
    office_reg = ask("事務所の都道府県知事登録番号")
    postal = ask_postal("郵便番号")
    address = ask("所在地")
    phone = ask("電話番号")
    return {
        "建築士種別": kind,
        "登録番号": reg_no,
        "氏名": name,
        "建築士事務所名": office,
        "事務所知事登録番号": office_reg,
        "郵便番号": postal,
        "所在地": address,
        "電話番号": phone,
    }


# ============================================================
# メイン処理
# ============================================================

def main():
    print("=" * 50)
    print("建築確認申請書 新規案件入力")
    print("=" * 50)

    # ---- 案件情報 ----
    section("案件情報")
    while True:
        case_no = ask("案件番号（例: 2026-002）", required=True)
        yaml_path = INPUT_DIR / f"{case_no}.yaml"
        if yaml_path.exists():
            overwrite = ask_yesno(
                f"{yaml_path.name} はすでに存在します。上書きしますか？",
                default_yes=False,
            )
            if not overwrite:
                print("  別の案件番号を入力してください。")
                continue
        break
    tanto = ask("担当者名（例: 山田 設計子）")

    # ---- 建築主 ----
    section("建築主の情報")
    owner_kana = ask("フリガナ（例: タナカ タロウ）")
    owner_name = ask("氏名", required=True)
    owner_postal = ask_postal("郵便番号")
    owner_address = ask("住所", required=True)
    owner_phone = ask("電話番号")

    # ---- 代理者 ----
    section("代理者の情報")
    has_agent = ask_yesno("代理者はいますか？", default_yes=False)
    agent = None
    if has_agent:
        agent = ask_architect_info()
        agent["担当図書"] = ask("担当図書", default="建築物全般")

    # ---- 設計者 ----
    section("設計者の情報")
    designer = ask_architect_info()

    # ---- 工事監理者 ----
    section("工事監理者の情報")
    same_as_designer = ask_yesno("設計者と同一ですか？", default_yes=True)
    if same_as_designer:
        supervisor = dict(designer)
    else:
        supervisor = ask_architect_info()

    # ---- 敷地情報 ----
    section("敷地情報")
    site_chiban = ask("地名地番", required=True)
    site_jukyo = ask("住居表示（Enter でスキップ）")

    print("  都市計画区域:")
    toshi_keikaku = ask_choice("  番号を入力", [
        ("1", "市街化区域"),
        ("2", "市街化調整区域"),
        ("3", "区域区分非設定"),
        ("4", "準都市計画区域内"),
        ("5", "都市計画区域および準都市計画区域外"),
    ], default_key="1")

    print("  防火地域:")
    bouka = ask_choice("  番号を入力", [
        ("1", "防火地域"),
        ("2", "準防火地域"),
        ("3", "指定なし"),
    ], default_key="2")

    yoto_chiiki = ask("用途地域（例: 第一種低層住居専用地域）")
    road_width = ask_float("道路幅員（m）")
    road_length = ask_float("道路との接する長さ（m）")
    site_area = ask_float("敷地面積（m2）", required=True)
    kenpei_rate = ask_int("指定建蔽率（%）", required=True)
    yoseki_rate = ask_int("指定容積率（%）", required=True)

    # ---- 建物情報 ----
    section("建物情報")
    main_use = ask("主要用途", default="一戸建ての住宅")
    use_code = ask("用途区分コード", default="08010")

    print("  工事種別:")
    koji_shubetsu = ask_choice("  番号を入力", [
        ("1", "新築"),
        ("2", "増築"),
        ("3", "改築"),
        ("4", "移転"),
    ], default_key="1")

    structure = ask("構造", default="木造")
    roof = ask("屋根の種類（例: 瓦葺）")
    outer_wall = ask("外壁の種類（例: モルタル塗り）")
    eave_back = ask("軒裏の種類（例: 石膏ボード）")
    above_floors = ask_int("地上階数", required=True)
    below_floors = ask_int("地下階数", default=0)
    max_height = ask_float("最高の高さ（m）", required=True)
    eave_height = ask_float("軒高（m）", required=True)
    building_area = ask_float("建築面積（m2）", required=True)

    # ---- 各階の床面積 ----
    section("各階の床面積")
    floors = []
    floor_summaries = []
    for i in range(1, above_floors + 1):
        floor_label = f"{i}階"
        print(f"\n  {floor_label}の情報:")
        fa = ask_float(f"{floor_label} 床面積（m2）", required=True)
        fu = ask(f"{floor_label} 用途", default=main_use)
        fc = ask(f"{floor_label} 用途区分コード", default=use_code)
        floors.append({
            "階": floor_label,
            "床面積": fa,
        })
        floor_summaries.append({
            "建築物番号": 1,
            "階": i,
            "柱の小径": None,
            "横架材間垂直距離": None,
            "階高": None,
            "天井高_居室": None,
            "特定天井": False,
            "用途区分コード": fc,
            "具体的用途": fu,
            "床面積": fa,
        })

    # 延べ床面積を計算
    total_area = round(sum(f["床面積"] for f in floors), 2)

    # ---- 工事日程 ----
    section("工事日程")
    start_date = ask("工事着手予定日（例: 2026-07-01）")
    end_date = ask("工事完了予定日（例: 2027-03-31）")

    # ============================================================
    # YAML データ構築
    # ============================================================
    output: dict = {}

    output["meta"] = {
        "案件番号": case_no,
        "担当者": tanto,
    }

    output["建築主"] = {
        "フリガナ": owner_kana,
        "氏名": owner_name,
        "郵便番号": owner_postal,
        "住所": owner_address,
        "電話番号": owner_phone,
    }

    if agent:
        output["代理者"] = agent

    output["設計者"] = designer
    output["工事監理者"] = supervisor

    output["敷地"] = {
        "地名地番": site_chiban,
        "住居表示": site_jukyo,
        "都市計画区域": toshi_keikaku,
        "防火地域": bouka,
        "用途地域": yoto_chiiki,
        "道路幅員": road_width,
        "道路との接する長さ": road_length,
        "敷地面積": site_area,
        "指定建蔽率": kenpei_rate,
        "指定容積率": yoseki_rate,
    }

    output["建物"] = {
        "主要用途": main_use,
        "用途区分コード": use_code,
        "工事種別": koji_shubetsu,
        "構造": structure,
        "屋根の種類": roof,
        "外壁の種類": outer_wall,
        "軒裏の種類": eave_back,
        "最高の高さ": max_height,
        "最高の軒の高さ": eave_height,
        "階数_地上": above_floors,
        "階数_地下": below_floors,
    }

    output["建築面積"] = building_area
    output["各階"] = floors
    output["階別概要"] = floor_summaries

    output["建築物独立部分"] = [{
        "番号": 1,
        "延べ面積": total_area,
        "最高の高さ": max_height,
        "最高の軒の高さ": eave_height,
        "階数_地上": above_floors,
        "階数_地下": below_floors,
        "構造": structure,
        "特定構造計算基準": "申請不要",
        "構造計算区分": None,
    }]

    if start_date or end_date:
        output["工事日程"] = {
            "着手予定日": start_date,
            "完了予定日": end_date,
        }

    # ============================================================
    # YAML 保存
    # ============================================================
    INPUT_DIR.mkdir(exist_ok=True)
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(
            output,
            f,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )

    print(f"\ninput/{yaml_path.name} を保存しました")

    # ============================================================
    # 申請書生成の確認
    # ============================================================
    gen = ask_yesno("\nそのまま申請書を生成しますか？", default_yes=True)
    if gen:
        gen_script = Path(__file__).parent / "generator.py"
        subprocess.run([sys.executable, str(gen_script), case_no], check=False)
    else:
        print(f"  python src/generator.py {case_no} で生成できます")


if __name__ == "__main__":
    main()
