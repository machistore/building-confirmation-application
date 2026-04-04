"""XLS → PDF 変換モジュール（Excel COM 経由）

依存: pywin32（pip install pywin32）
Windows + Excel インストール済み環境のみで動作する。
"""

import os
from pathlib import Path


def convert_to_pdf(xls_path: str) -> str:
    """Excel ファイルを PDF に変換して保存し、生成した PDF のパスを返す。

    Args:
        xls_path: 変換元 XLS ファイルのパス（相対・絶対どちらでも可）

    Returns:
        生成された PDF ファイルの絶対パス（文字列）

    Raises:
        RuntimeError: Excel が見つからない場合
        Exception: PDF 変換に失敗した場合（内容を表示して再送出）
    """
    # COM 操作は絶対パスが必要
    xls_abs = str(Path(xls_path).resolve())
    pdf_abs = str(Path(xls_abs).with_suffix(".pdf"))

    try:
        import win32com.client as win32
    except ImportError:
        raise RuntimeError(
            "pywin32 がインストールされていません。"
            "pip install pywin32 を実行してください。"
        )

    excel = None
    wb = None
    try:
        excel = win32.DispatchEx("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False

        wb = excel.Workbooks.Open(xls_abs)

        # xlTypePDF = 0
        wb.ExportAsFixedFormat(
            Type=0,
            Filename=pdf_abs,
            Quality=0,          # xlQualityStandard
            IncludeDocProperties=True,
            IgnorePrintAreas=False,
            OpenAfterPublish=False,
        )
        return pdf_abs

    except Exception as e:
        if "Excel" in type(e).__module__ or "com_error" in type(e).__name__:
            print(f"Excelがインストールされていません（COMエラー: {e}）")
        else:
            print(f"PDF変換中にエラーが発生しました: {e}")
        raise

    finally:
        if wb is not None:
            try:
                wb.Close(SaveChanges=False)
            except Exception:
                pass
        if excel is not None:
            try:
                excel.Quit()
            except Exception:
                pass
