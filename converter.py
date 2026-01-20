#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android strings 文件 繁体 → 简体 转换工具（支持多个文件）

用法：
  python converter.py file1.txt file2.txt
  python converter.py res/values-zh-rHK/strings.txt res/values-zh-rTW/strings.txt

特点：
- 只转换 <string name="..."> 标签内的文本内容
- 保留 XML 结构、注释、空行
- 输出文件放在原文件同目录，文件名后加 _sc
- 即使转换后内容相同，也强制覆盖写入文件（确保 git 能检测到变化）
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
            # 保留空行、注释、resources 标签等
            if not stripped or stripped.startswith('<!--') or stripped.startswith('<resources') or stripped.startswith('</resources'):
                converted_lines.append(line)
                continue

            # 匹配 <string name="xxx">内容</string>
            # 支持带转义字符的简单情况
            match = re.match(r'^(\s*<string\s+name="[^"]*">)(.*?)(</string>\s*)$', line.strip(), re.DOTALL)
            if match:
                prefix, text, suffix = match.groups()
                # 只转译标签内的文本
                converted_text = convert_text(text)
                # 重新拼接，保持原缩进
                indent = line[:line.find('<string')] if '<string' in line else ''
                new_line = f"{indent}{prefix}{converted_text}{suffix}\n"
                converted_lines.append(new_line)
            else:
                # 其他行（如 plurals、注释等）整体转换
                converted_lines.append(convert_text(line))

        # 输出路径：同目录 + _sc 后缀
        output_path = input_path.with_stem(input_path.stem + '_sc')
        
        # 强制写入（即使内容相同）
        output_path.write_text(''.join(converted_lines), encoding='utf-8')
        print(f"完成: {input_path} → {output_path} (强制写入)")
        return output_path

    except Exception as e:
        print(f"错误 {input_path}: {e}")
        return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python converter.py <文件1> [文件2 文件3 ...]")
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
