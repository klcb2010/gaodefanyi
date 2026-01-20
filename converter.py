#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android strings 文件（.txt / .xml）繁体 → 简体 转换工具（支持多个文件）

用法：
  python converter.py string-zh-rHK.xml string-zh-rTW.xml
  python converter.py res/values-zh-rHK/strings.xml res/values-zh-rTW/strings.xml

输出规则：
- 输出文件放在原文件同目录
- 文件名 = 原文件名 + .sc（例如 string-zh-rTW.xml → string-zh-rTW.xml.sc）
"""

from opencc import OpenCC
import sys
import re
from pathlib import Path


def convert_text(content: str) -> str:
    """繁体 → 简体"""
    converter = OpenCC('t2s')
    return converter.convert(content)


def convert_strings_file(input_path: Path) -> Path | None:
    """转换单个文件，返回输出路径（失败返回 None）"""
    try:
        lines = input_path.read_text(encoding='utf-8').splitlines(keepends=True)

        converted_lines = []
        for line in lines:
            stripped = line.strip()
            # 保留空行、注释、<resources>、</resources> 等結構行
            if not stripped or stripped.startswith('<!--') or \
               stripped.startswith('<resources') or stripped.startswith('</resources>'):
                converted_lines.append(line)
                continue

            # 匹配單行 <string name="xxx">內容</string>
            match = re.match(r'^(\s*<string\s+name="[^"]*">)(.*?)(</string>\s*)$', line.strip(), re.DOTALL)
            if match:
                prefix, text, suffix = match.groups()
                converted_text = convert_text(text)
                # 保持原縮進
                indent_match = re.match(r'^(\s*)<string', line)
                indent = indent_match.group(1) if indent_match else ''
                new_line = f"{indent}{prefix}{converted_text}{suffix}\n"
                converted_lines.append(new_line)
            else:
                # 其他行（如 plurals、註釋、<item> 等）整體轉換
                converted_lines.append(convert_text(line))

        # 輸出檔名：原檔名 + .sc
        output_path = input_path.with_suffix(input_path.suffix + '.sc')

        # 強制寫入（即使內容相同）
        output_path.write_text(''.join(converted_lines), encoding='utf-8')
        print(f"完成: {input_path} → {output_path} (强制写入)")
        return output_path

    except Exception as e:
        print(f"错误 {input_path}: {e}")
        return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python converter.py <文件1> [文件2 文件3 ...]")
        print("支持 .xml 和 .txt 檔，例如: python converter.py string-zh-rHK.xml string-zh-rTW.xml")
        sys.exit(1)

    success_count = 0
    for arg in sys.argv[1:]:
        path = Path(arg)
        if not path.is_file():
            print(f"跳过（不是文件）: {arg}")
            continue
        if convert_strings_file(path):
            success_count += 1

    print(f"\n转换完成：成功 {success_count} / 总计 {len(sys.argv)-1} 个文件")
