"""建築確認申請書 生成メインスクリプト

使い方:
    python src/generator.py [YAMLファイルパス]

    YAMLファイルパスを省略した場合は input/sample_project.yaml を使用する。
"""

import sys
from pathlib import Path

# src/ から実行された場合も import できるよう親ディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

import yaml
import openpyxl
from calculator import calc_total_floor_area, calc_kenpei_ratio, calc_yoseki_ratio
from validator import validate


def load_yaml(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def format_result(data: dict, total_floor_area: float, kenpei: float, yoseki: float) -> str:
    lines = []
    meta = data.get("meta", {})
    site = data.get("敷地", {})

    lines.append("=" * 50)
    lines.append("建築確認申請書 計算結果")
    lines.append("=" * 50)
    lines.append(f"案件番号  : {meta.get('案件番号', '---')}")
    lines.append(f"担当者    : {meta.get('担当者', '---')}")
    lines.append("")
    lines.append("【敷地情報】")
    lines.append(f"  敷地面積      : {site.get('敷地面積', '---')} ㎡")
    lines.append(f"  指定建蔽率    : {site.get('指定建蔽率', '---')} %")
    lines.append(f"  指定容積率    : {site.get('指定容積率', '---')} %")
    lines.append("")
    lines.append("【建築面積・延べ床面積】")
    lines.append(f"  建築面積      : {data.get('建築面積', '---')} ㎡")
    lines.append(f"  延べ床面積    : {total_floor_area} ㎡")
    lines.append("")
    lines.append("【各階床面積】")
    for floor in data.get("各階", []):
        lines.append(f"  {floor['階']:<6}: {floor['床面積']} ㎡")
    lines.append("")
    lines.append("【計算結果】")
    lines.append(f"  建蔽率        : {kenpei} %  （指定: {site.get('指定建蔽率', '---')} %）")

    kenpei_ok = kenpei <= site.get("指定建蔽率", float("inf"))
    lines.append(f"  建蔽率チェック: {'OK' if kenpei_ok else 'NG - 指定建蔽率を超過しています'}")

    lines.append(f"  容積率        : {yoseki} %  （指定: {site.get('指定容積率', '---')} %）")
    yoseki_ok = yoseki <= site.get("指定容積率", float("inf"))
    lines.append(f"  容積率チェック: {'OK' if yoseki_ok else 'NG - 指定容積率を超過しています'}")

    lines.append("=" * 50)
    return "\n".join(lines)


def _resolve_key(data: dict, dotted_key: str):
    """ドット区切りキーでネストした辞書の値を取得する。

    例: "建築主.氏名" → data["建築主"]["氏名"]
    """
    keys = dotted_key.split(".")
    value = data
    for k in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(k)
    return value


def write_excel(
    data: dict,
    calc_values: dict,
    cell_map_path: Path,
    output_path: Path,
) -> None:
    """cell_map.yaml に従ってデータを Excel に書き込む。

    Args:
        data: YAMLから読み込んだ入力データ
        calc_values: 計算済み値の辞書（延べ床面積・建蔽率・容積率）
        cell_map_path: cell_map.yaml のパス
        output_path: 出力先 .xlsx のパス
    """
    cell_map = load_yaml(cell_map_path)
    sheet_name = cell_map.get("sheet", "Sheet1")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_name

    # --- 入力データの書き込み ---
    for entry in cell_map.get("fields", []):
        value = _resolve_key(data, entry["key"])
        if value is not None:
            ws[entry["cell"]] = value

    # --- 計算値の書き込み ---
    for entry in cell_map.get("calculated", []):
        value = calc_values.get(entry["key"])
        if value is not None:
            ws[entry["cell"]] = value

    # --- 各階の繰り返し書き込み ---
    floors_cfg = cell_map.get("floors", {})
    start_row = floors_cfg.get("start_row", 26)
    kai_col = floors_cfg.get("階_col", "B")
    area_col = floors_cfg.get("床面積_col", "C")

    for i, floor in enumerate(data.get("各階", [])):
        row = start_row + i
        ws[f"{kai_col}{row}"] = floor.get("階")
        ws[f"{area_col}{row}"] = floor.get("床面積")

    wb.save(output_path)


def main():
    # 入力ファイルパスの決定
    base_dir = Path(__file__).parent.parent
    if len(sys.argv) >= 2:
        input_path = sys.argv[1]
    else:
        input_path = base_dir / "input" / "sample_project.yaml"

    print(f"入力ファイル: {input_path}")

    # YAML読み込み
    try:
        data = load_yaml(input_path)
    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません: {input_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"エラー: YAMLの解析に失敗しました: {e}")
        sys.exit(1)

    # バリデーション
    errors = validate(data)
    if errors:
        print("バリデーションエラーが発生しました:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)

    # 計算
    floors = data["各階"]
    building_area = data["建築面積"]
    site_area = data["敷地"]["敷地面積"]

    total_floor_area = calc_total_floor_area(floors)
    kenpei = calc_kenpei_ratio(building_area, site_area)
    yoseki = calc_yoseki_ratio(total_floor_area, site_area)

    # 結果をテキストで出力
    result_text = format_result(data, total_floor_area, kenpei, yoseki)
    print(result_text)

    output_dir = base_dir / "output"
    output_dir.mkdir(exist_ok=True)

    # テキスト出力
    txt_path = output_dir / "result.txt"
    txt_path.write_text(result_text, encoding="utf-8")
    print(f"\n結果を保存しました: {txt_path}")

    # Excel 出力
    cell_map_path = output_dir / "cell_map.yaml"
    xlsx_path = output_dir / "result.xlsx"
    write_excel(
        data=data,
        calc_values={
            "延べ床面積": total_floor_area,
            "建蔽率": kenpei,
            "容積率": yoseki,
        },
        cell_map_path=cell_map_path,
        output_path=xlsx_path,
    )
    print(f"Excelを保存しました: {xlsx_path}")


if __name__ == "__main__":
    main()
