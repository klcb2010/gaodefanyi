#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android strings 文件（.txt / .xml）繁体 → 简体 转换工具

嚴格原則：只轉換真正的繁體中文文字內容，其他部分（XML 結構、prolog、註解、標籤屬性等）完全不動
輸出檔名：原檔名 + .sc
"""

from opencc import OpenCC
import sys
import re
from pathlib import Path


def convert_text(content: str) -> str:
    """只在內容看起來是繁體中文時才轉換"""
    converter = OpenCC('t2s')
    # 簡單判斷：如果有中文字符且包含繁體特徵（如 '麼'、'體' 等），才轉
    if re.search(r'[\u4e00-\u9fff]', content) and any(c in content for c in '麼體臺灣裡'):
        return converter.convert(content)
    return content  # 不符合就原樣返回


def convert_strings_file(input_path: Path) -> Path | None:
    try:
        content = input_path.read_text(encoding='utf-8')
        lines = content.splitlines(keepends=True)
        converted_lines = []

        in_string = False
        current_string = ""

        for line in lines:
            stripped = line.strip()

            # 完全不碰的行（直接保留）
            if (
                not stripped or
                stripped.startswith('<?xml') or           # prolog
                stripped.startswith('<!--') or           # 註解開始
                stripped.startswith('<resources') or
                stripped.startswith('</resources>') or
                stripped.startswith('<') and 'name="' in stripped and not stripped.endswith('>')  # 開標籤但沒結束
            ):
                converted_lines.append(line)
                continue

            # 處理 <string name="..."> ... </string>
            if '<string ' in line and 'name="' in line:
                # 提取前綴、內容、後綴
                match = re.match(r'^(\s*<string\s+name="[^"]*">)(.*)(</string>\s*)$', line.strip(), re.DOTALL)
                if match:
                    prefix, text, suffix = match.groups()
                    converted_text = convert_text(text)
                    indent = line[:line.find('<string')] if '<string' in line else '  '
                    new_line = f"{indent}{prefix}{converted_text}{suffix}\n"
                    converted_lines.append(new_line)
                else:
                    # 不標準的 string 行，整行不轉
                    converted_lines.append(line)
            else:
                # 其他行（如 plurals 的 <item>、註解內文字等），保守起見不轉
                # 如果你確定 <item> 也要轉，可以加類似 string 的處理
                converted_lines.append(line)

        # 輸出檔名
        output_path = input_path.with_suffix(input_path.suffix + '.sc')
        output_path.write_text(''.join(converted_lines), encoding='utf-8')
        print(f"完成: {input_path} → {output_path}")
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
        if path.is_file() and path.suffix.lower() in {'.txt', '.xml'}:
            if convert_strings_file(path):
                success_count += 1
        else:
            print(f"跳過: {arg}")

    print(f"\n轉換完成：成功 {success_count} 個文件")
