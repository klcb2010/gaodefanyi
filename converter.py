#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android strings.txt 繁体 → 简体 转换工具（支持多个文件）
用法示例：
  python converter.py file1.txt file2.txt
  python converter.py res/values-zh-rHK/strings.txt res/values-zh-rTW/strings.txt
"""

from opencc import OpenCC
import sys
import re
from pathlib import Path


def convert_text(content: str) -> str:
    """繁体 → 简体"""
    converter = OpenCC('t2s')
    return converter.convert(content)


def convert_file(input_path: Path):
    """转换单个文件，输出到同目录 + _sc 后缀"""
    try:
        content = input_path.read_text(encoding='utf-8')
        
        # 这里简单整文件转换（如果你的文件是标准 xml，建议后面改成逐 string 转换）
        converted = convert_text(content)
        
        # 输出路径：同目录 + _sc 后缀
        output_path = input_path.with_stem(input_path.stem + '_sc')
        output_path.write_text(converted, encoding='utf-8')
        
        print(f"完成: {input_path.name} → {output_path.name}")
        
    except Exception as e:
        print(f"失败 {input_path.name}: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python converter.py 文件1 [文件2 文件3 ...]")
        sys.exit(1)

    for arg in sys.argv[1:]:
        path = Path(arg)
        if path.is_file():
            convert_file(path)
        else:
            print(f"跳过（不是文件）: {arg}")
