#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android strings 檔案（.txt / .xml）繁轉簡 - 簡易強制版
- 無論結構，直接把整個檔案內容當純文字轉換
- 保證繁體 → 簡體一定發生
- 輸出為 原檔名.sc（例如 string-zh-rHK.xml → string-zh-rHK.xml.sc）
"""

from opencc import OpenCC
import sys
from pathlib import Path


def convert_text(content: str) -> str:
    """繁體 → 簡體"""
    converter = OpenCC('t2s')
    return converter.convert(content)


def convert_file(input_path: Path) -> Path | None:
    try:
        # 讀取整個檔案內容
        content = input_path.read_text(encoding='utf-8')

        # 直接整體轉換（最簡單可靠）
        converted_content = convert_text(content)

        # 輸出檔名
        output_path = input_path.with_suffix(input_path.suffix + '.sc')

        # 寫入
        output_path.write_text(converted_content, encoding='utf-8')

        # 簡單比較是否真的轉了
        if converted_content != content:
            print(f"完成（有變化）: {input_path} → {output_path}")
        else:
            print(f"完成（無變化）: {input_path} → {output_path} （原內容已為簡體或無可轉文字）")

        return output_path

    except Exception as e:
        print(f"錯誤 {input_path}: {e}")
        return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python converter.py <文件1> [文件2 ...]")
        sys.exit(1)

    success_count = 0
    for arg in sys.argv[1:]:
        path = Path(arg)
        if path.is_file():
            if convert_file(path):
                success_count += 1
        else:
            print(f"跳過: {arg}")

    print(f"\n轉換完成：成功處理 {success_count} 個文件")
