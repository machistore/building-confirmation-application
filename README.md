# 建築確認申請書 自動生成システム

## 概要
入力YAMLに案件情報を記述するだけで、建築確認申請書（別記第二号様式）の
XLSおよびPDFを自動生成するPythonツールです。四号建築物（木造2階建て住宅）を対象とします。

## 必要環境
- Python 3.x
- Microsoft Excel（win32com経由のPDF変換に必要）

## セットアップ

```bash
pip install pyyaml xlrd xlwt xlutils pywin32
```

## 使い方

1. `shinsei-generator/input/sample_project.yaml` を案件の情報に合わせて編集する
2. 以下を実行する

```bash
cd shinsei-generator
python src/generator.py
```

3. `output/` に以下のファイルが生成される
   - `申請書_出力.xls`：セル書き込み済みのExcelファイル
   - `申請書_出力.pdf`：PDF変換済みの申請書

## ファイル構成

```
building-confirmation-application/
├── README.md
└── shinsei-generator/
    ├── CLAUDE.md                      # プロジェクト説明・ドメイン知識（AI向け）
    ├── input/
    │   └── sample_project.yaml        # 案件ごとの入力データ
    ├── templates/
    │   └── BPR003_260323.xls          # 申請書テンプレート（編集禁止）
    ├── src/
    │   ├── generator.py               # メイン処理
    │   ├── calculator.py              # 建蔽率・容積率・延べ床面積の計算
    │   ├── validator.py               # 入力値の検証
    │   └── pdf_converter.py           # PDF変換（win32com）
    └── output/
        ├── cell_map.yaml              # セルマッピング定義
        ├── 申請書_出力.xls            # 生成物
        └── 申請書_出力.pdf            # 生成物
```

## 入力YAMLの項目説明

```yaml
meta:
  案件番号: "2026-001"       # 管理用の番号
  担当者: "山田 設計子"      # 担当者名

建築主:
  フリガナ: "タナカ タロウ"
  氏名: "田中 太郎"
  郵便番号: "150-0001"
  住所: "東京都渋谷区..."
  電話番号: "03-1234-5678"

敷地:
  敷地面積: 165.00            # ㎡
  指定建蔽率: 40              # %
  指定容積率: 80              # %

建築面積: 55.00               # ㎡（申請部分）

各階:                         # 第四面：階別床面積
  - 階: "1階"
    床面積: 55.00
  - 階: "2階"
    床面積: 43.10

階別概要:                     # 第五面：柱径・天井高・用途
  - 建築物番号: 1
    階: 1
    柱の小径: 0.105           # m
    横架材間垂直距離: 2.85    # m
    階高: 2.90                # m
    天井高_居室: 2.40         # m
    特定天井: false
    用途区分コード: "08010"
    具体的用途: "一戸建ての住宅"
    床面積: 55.00

建築物独立部分:               # 第六面：高さ・階数・構造
  - 番号: 1
    延べ面積: 98.10
    最高の高さ: 8.20          # m
    最高の軒の高さ: 5.80      # m
    階数_地上: 2
    階数_地下: 0
    構造: "木造"
```

## 注意事項
- `templates/` 以下のファイルは編集しないこと（書式・セル結合が崩れるため）
- Excelがインストールされていない環境ではPDF変換がスキップされ、XLSのみ生成される
- 建蔽率・容積率・延べ床面積は入力値から自動計算されるため、YAMLへの手入力は不要
- `output/cell_map.yaml` のセル座標（row/col）は0始まり
