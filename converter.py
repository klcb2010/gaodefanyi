#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android strings 文件（.txt / .xml）繁体 → 简体 转换工具

输出规则：原文件名 + .sc（例如 string-zh-rTW.xml → string-zh-rTW.xml.sc）
"""

from opencc import OpenCC
import sys
import re
from pathlib import Path


def convert_text(content: str) -> str:
    converter = OpenCC('t2s')
    return converter.convert(content)


def convert_strings_file(input_path: Path) -> Path | None:
    try:
        lines = input_path.read_text(encoding='utf-8').splitlines(keepends=True)
        converted_lines = []

        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('<!--') or \
               stripped.startswith('<resources') or stripped.startswith('</resources>'):
                converted_lines.append(line)
                continue

            match = re.match(r'^(\s*<string\s+name="[^"]*">)(.*?)(</string>\s*)$', line.strip(), re.DOTALL)
            if match:
                prefix, text, suffix = match.groups()
                converted_text = convert_text(text)
                indent_match = re.match(r'^(\s*)<string', line)
                indent = indent_match.group(1) if indent_match else ''
                new_line = f"{indent}{prefix}{converted_text}{suffix}\n"
                converted_lines.append(new_line)
            else:
                converted_lines.append(convert_text(line))

        output_path = input_path.with_suffix(input_path.suffix + '.sc')
        output_path.write_text(''.join(converted_lines), encoding='utf-8')
        print(f"完成: {input_path} → {output_path}")
        return output_path

    except Exception as e:
        print(f"错误 {input_path}: {e}")
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
            print(f"跳过: {arg}")

    print(f"\n转换完成：成功 {success_count} 个文件")
