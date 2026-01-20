#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android strings 文件 繁体 → 简体 转换工具（支持多个文件）

用法：
  python converter.py file1.txt file2.txt
  python converter.py res/values-zh-rHK/*.txt
  python converter.py path/to/file1.txt another/path/file2.xml

转换后：
- 输出文件放在与输入文件相同目录
- 文件名后缀加 _sc （在原 stem 后加 _sc）
"""

from opencc import OpenCC
import sys
from pathlib import Path
import re


def convert_content(content: str) -> str:
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
            if not stripped or stripped.startswith('<!--') or stripped.startswith('<!--'):
                converted_lines.append(line)
                continue

            # 尝试匹配 <string name="xxx">内容</string> 这一行
            match = re.match(r'^(\s*<string\s+name="[^"]*">)(.*?)(</string>\s*)$', line.strip(), re.DOTALL)
            if match:
                prefix, text, suffix = match.groups()
                converted_text = convert_content(text)
                converted_lines.append(f"{prefix}{converted_text}{suffix}\n")
            else:
                # 其他行整体转换（注释、<resources> 等）
                converted_lines.append(convert_content(line))

        # 输出路径：同目录，文件名加 _sc
        output_path = input_path.with_stem(input_path.stem + '_sc')

        output_path.write_text(''.join(converted_lines), encoding='utf-8')
        print(f"完成: {input_path} → {output_path}")
        return output_path

    except Exception as e:
        print(f"错误 {input_path}: {e}")
        return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python converter.py <文件1> [文件2 文件3 ...]")
        print("      支持通配符，例如: python converter.py res/**/*-zh-r*.txt")
        sys.exit(1)

    success_count = 0
    for arg in sys.argv[1:]:
        path = Path(arg)
        if path.is_file():
            if convert_strings_file(path):
                success_count += 1
        elif path.is_dir():
            print(f"跳过目录（暂不支持递归）：{path}")
        else:
            print(f"路径不存在或不是文件：{arg}")

    print(f"\n转换完成：成功 {success_count} / 总计 {len(sys.argv)-1} 个文件")
