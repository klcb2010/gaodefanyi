#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android strings.txt 繁体 → 简体 转换工具
专门处理 string-zh-rHK.txt / string-zh-rTW.txt 这类文件
输出到同目录，文件名自动加 _sc 后缀，例如：
string-zh-rHK.txt → string-zh-rHK_sc.txt
"""

from opencc import OpenCC
import sys
import re
from pathlib import Path


def convert_text(content: str) -> str:
    """繁体中文 → 简体中文"""
    converter = OpenCC('t2s')
    return converter.convert(content)


def should_skip_line(line: str) -> bool:
    """判断是否为注释、空行或不需要转换的行"""
    stripped = line.strip()
    if not stripped:
        return True
    if stripped.startswith('<!--') and stripped.endswith('-->'):
        return True
    # Android 常见的 <xliff:g> 标记内容通常不翻译
    if '<xliff:g' in line and '</xliff:g>' in line:
        return 'example' in line.lower() or 'placeholder' in line.lower()
    return False


def convert_strings_file(input_path: Path):
    """处理单个 strings*.txt 文件，输出到同目录"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        converted_lines = []
        for line in lines:
            # 保留原始换行
            if should_skip_line(line):
                converted_lines.append(line)
                continue

            # 尝试匹配 <string name="xxx">繁体内容</string>
            match = re.match(r'^(\s*)<string\s+name="[^"]+"\s*>(.*?)</string>\s*$', line, re.DOTALL)
            if match:
                indent = match.group(1)
                content = match.group(2)
                # 只转换 string 标签内的文本内容
                converted_content = convert_text(content)
                # 重新拼接（保留原 name）
                name_part = line.split('name="')[1].split('"')[0]
                new_line = f'{indent}<string name="{name_part}">{converted_content}</string>\n'
                converted_lines.append(new_line)
            else:
                # 非标准 string 格式的行 → 整行转换（比较安全）
                converted_lines.append(convert_text(line))

        # 输出文件名：原文件名 + _sc
        output_filename = input_path.stem + "_sc" + input_path.suffix
        output_path = input_path.parent / output_filename

        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(converted_lines)

        print(f"✓ 转换完成: {input_path.name} → {output_filename}")

    except Exception as e:
        print(f"✗ 转换失败 {input_path.name}: {e}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="繁体中文 strings.txt 转简体工具（适用于 Android 资源文件）")
    parser.add_argument("path", nargs="?", default=".", 
                        help="文件或目录路径（默认：当前目录）")
    args = parser.parse_args()

    target = Path(args.path).resolve()

    if not target.exists():
        print(f"错误：路径不存在 → {target}")
        sys.exit(1)

    # 支持的文件名特征（可自行扩展）
    target_patterns = ("string-zh-rHK.txt", "string-zh-rTW.txt", "strings-zh-rHK.txt", "strings-zh-rTW.txt")

    if target.is_file():
        if target.name.lower().endswith(".txt") and any(p in target.name for p in target_patterns):
            convert_strings_file(target)
        else:
            print("错误：请输入以 string-zh-rHK.txt 或 string-zh-rTW.txt 结尾的文件")
            sys.exit(1)

    elif target.is_dir():
        print(f"扫描目录：{target}")
        found = False
        for file in target.glob("**/*"):
            if not file.is_file():
                continue
            if file.suffix.lower() != ".txt":
                continue
            if any(p in file.name for p in target_patterns):
                convert_strings_file(file)
                found = True

        if not found:
            print("在目录及其子目录中没有找到符合文件名的文件（string-zh-r*）")
    else:
        print("错误：无效的路径")
        sys.exit(1)


if __name__ == "__main__":
    main()
