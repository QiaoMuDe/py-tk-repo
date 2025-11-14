#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 从encodings模块获取所有支持的编码
import encodings
import os


def get_supported_encodings():
    """获取支持的编码列表

    Returns:
        list: 支持的编码列表，常用编码在前
    """
    # 常用编码选项
    common_encodings = [
        "UTF-8",
        "UTF-16",
        "UTF-32",
        "ASCII",
        "GB2312",
        "GBK",
        "GB18030",
        "BIG5",
        "ISO-8859-1",
        "ISO-8859-2",
        "ISO-8859-15",
        "Windows-1252",
        "Windows-1251",
        "Windows-1256",
        "Shift_JIS",
        "EUC-JP",
        "KOI8-R",
        "KOI8-U",
    ]

    try:
        all_encodings = [
            f[:-3]  # 移除.py扩展名
            for f in os.listdir(os.path.dirname(encodings.__file__))
            if f.endswith(".py") and not f.startswith("_")
        ]

        # 合并常用编码和所有支持的编码，保持常用编码在前
        supported_encodings = common_encodings[:]
        for enc in all_encodings:
            if enc.upper() not in [e.upper() for e in supported_encodings]:
                supported_encodings.append(enc)

        return supported_encodings
    except:
        # 如果获取所有编码失败，返回常用编码列表
        return common_encodings
