#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from loguru import logger

# 常用编码选项（优先显示）
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

# 系统支持的所有编码（硬编码列表）
all_encodings = [
    "aliases",
    "base64_codec",
    "big5hkscs",
    "bz2_codec",
    "charmap",
    "cp037",
    "cp1006",
    "cp1026",
    "cp1125",
    "cp1140",
    "cp1250",
    "cp1251",
    "cp1252",
    "cp1253",
    "cp1254",
    "cp1255",
    "cp1256",
    "cp1257",
    "cp1258",
    "cp273",
    "cp424",
    "cp437",
    "cp500",
    "cp720",
    "cp737",
    "cp775",
    "cp850",
    "cp852",
    "cp855",
    "cp856",
    "cp857",
    "cp858",
    "cp860",
    "cp861",
    "cp862",
    "cp863",
    "cp864",
    "cp865",
    "cp866",
    "cp869",
    "cp874",
    "cp875",
    "cp932",
    "cp949",
    "cp950",
    "euc_jisx0213",
    "euc_jis_2004",
    "euc_jp",
    "euc_kr",
    "hex_codec",
    "hp_roman8",
    "hz",
    "idna",
    "iso2022_jp",
    "iso2022_jp_1",
    "iso2022_jp_2",
    "iso2022_jp_2004",
    "iso2022_jp_3",
    "iso2022_jp_ext",
    "iso2022_kr",
    "iso8859_1",
    "iso8859_10",
    "iso8859_11",
    "iso8859_13",
    "iso8859_14",
    "iso8859_15",
    "iso8859_16",
    "iso8859_2",
    "iso8859_3",
    "iso8859_4",
    "iso8859_5",
    "iso8859_6",
    "iso8859_7",
    "iso8859_8",
    "iso8859_9",
    "johab",
    "koi8_r",
    "koi8_t",
    "koi8_u",
    "kz1048",
    "latin_1",
    "mac_arabic",
    "mac_croatian",
    "mac_cyrillic",
    "mac_farsi",
    "mac_greek",
    "mac_iceland",
    "mac_latin2",
    "mac_roman",
    "mac_romanian",
    "mac_turkish",
    "mbcs",
    "oem",
    "palmos",
    "ptcp154",
    "punycode",
    "quopri_codec",
    "raw_unicode_escape",
    "rot_13",
    "shift_jisx0213",
    "shift_jis_2004",
    "tis_620",
    "undefined",
    "unicode_escape",
    "utf_16",
    "utf_16_be",
    "utf_16_le",
    "utf_32",
    "utf_32_be",
    "utf_32_le",
    "utf_7",
    "utf_8",
    "utf_8_sig",
    "uu_codec",
    "zlib_codec",
]


def truncate_string(text, max_length, suffix="..."):
    """
    通用字符串截断函数，智能处理文件路径

    Args:
        text (str): 要截断的字符串或文件路径
        max_length (int): 最大显示长度
        suffix (str): 截断后添加的后缀，默认为"..."

    Returns:
        str: 截断后的字符串，路径分隔符统一为当前平台格式
    """
    from pathlib import Path
    import os

    if not text or len(text) <= max_length:
        return text

    # 使用pathlib处理路径，自动处理平台分隔符
    path = Path(text)
    basename = path.name
    parent = path.parent

    # 如果只有文件名没有路径，根据是否有扩展名决定截断方式
    if parent == Path("."):
        # 如果文件名长度在限制内，直接返回
        if len(basename) <= max_length:
            return basename

        # 检查是否有扩展名 - 使用更准确的方法
        # 只有当最后一个点后面有字符且不在开头时，才认为是扩展名
        last_dot_index = basename.rfind(".")
        has_extension = last_dot_index > 0 and last_dot_index < len(basename) - 1

        # 确保max_length至少能容纳suffix
        if max_length <= len(suffix):
            return suffix[:max_length]

        if has_extension:
            # 有扩展名：分离文件名和扩展名
            name_without_ext = basename[:last_dot_index]
            ext = basename[last_dot_index:]  # 包含点

            # 计算可用长度（减去扩展名和"..."）
            available_name_length = max_length - len(ext) - len(suffix)

            if available_name_length <= 1:
                # 如果可用长度太短，只保留扩展名
                return (
                    suffix + ext
                    if len(suffix) + len(ext) <= max_length
                    else ext[:max_length]
                )

            # 截断前面，保留结尾和扩展名
            # 从末尾开始截取文件名，保留足够长度
            return suffix + name_without_ext[-available_name_length:] + ext
        else:
            # 没有扩展名：截断后面，保留前面
            available_name_length = max_length - len(suffix)
            if available_name_length <= 1:
                return suffix[:max_length]
            return basename[:available_name_length] + suffix

    # 计算可用长度
    available_length = max_length - len(suffix)

    # 确保max_length至少能容纳suffix
    if max_length <= len(suffix):
        return suffix[:max_length]

    # 检查文件名是否有扩展名 - 使用更准确的方法
    last_dot_index = basename.rfind(".")
    has_extension = last_dot_index > 0 and last_dot_index < len(basename) - 1

    # 如果文件名本身就超过可用长度的一半，优先保留文件名的关键部分
    if len(basename) > available_length // 2:
        if has_extension:
            # 有扩展名：截断文件名前面部分，保留结尾和扩展名
            name_without_ext = basename[:last_dot_index]
            ext = basename[last_dot_index:]  # 包含点

            # 计算文件名部分的可用长度（减去扩展名和"..."）
            available_name_length = available_length - len(ext) - len(suffix)

            if available_name_length <= 1:
                # 如果可用长度太短，只保留扩展名
                return (
                    suffix + ext
                    if len(suffix) + len(ext) <= max_length
                    else ext[:max_length]
                )

            # 截断前面，保留结尾和扩展名
            truncated_name = suffix + name_without_ext[-available_name_length:] + ext
            return truncated_name
        else:
            # 没有扩展名：截断文件名后面部分，保留前面
            available_name_length = available_length - len(suffix)
            if available_name_length <= 1:
                return suffix[:max_length]
            truncated_basename = basename[:available_name_length] + suffix
            return truncated_basename

    # 文件名较短，保留完整文件名，截断目录路径
    # 计算目录路径的可用长度（减去文件名和分隔符）
    remaining_length = available_length - len(basename) - 1  # 1 是路径分隔符的长度

    if remaining_length <= 0:
        # 连文件名都放不下，只能截断文件名
        if has_extension:
            # 有扩展名：截断前面，保留结尾和扩展名
            name_without_ext = basename[:last_dot_index]
            ext = basename[last_dot_index:]  # 包含点

            # 计算文件名部分的可用长度（减去扩展名和"..."）
            available_name_length = max_length - len(ext) - len(suffix)

            if available_name_length <= 1:
                # 如果可用长度太短，只保留扩展名
                return (
                    suffix + ext
                    if len(suffix) + len(ext) <= max_length
                    else ext[:max_length]
                )

            # 截断前面，保留结尾和扩展名
            return suffix + name_without_ext[-available_name_length:] + ext
        else:
            # 没有扩展名：截断后面，保留前面
            available_name_length = max_length - len(suffix)
            if available_name_length <= 1:
                return suffix[:max_length]
            return basename[:available_name_length] + suffix

    # 将父目录转换为字符串
    parent_str = str(parent)

    # 截断目录路径，保留末尾部分
    if len(parent_str) > remaining_length:
        # 从末尾开始截取目录路径，保留足够长度
        truncated_parent = suffix + parent_str[-(remaining_length - len(suffix)) :]
        # 确保不包含多余的路径分隔符
        if truncated_parent.startswith(os.sep):
            truncated_parent = truncated_parent[1:]
    else:
        truncated_parent = parent_str

    # 组合截断后的路径，使用pathlib自动处理分隔符
    return str(Path(truncated_parent)) + os.sep + basename


def get_supported_encodings():
    """获取支持的编码列表

    Returns:
        list: 支持的编码列表，常用编码在前
    """
    try:
        # 合并常用编码和所有支持的编码，保持常用编码在前
        supported_encodings = common_encodings[:]  # 常用编码已经是大写的，无需转换
        for enc in all_encodings:
            # 转换为大写格式，并将下划线替换为横杠
            formatted_enc = enc.replace("_", "-").upper()

            # 添加编码（统一使用横杠格式）
            if formatted_enc not in [e.upper() for e in supported_encodings]:
                supported_encodings.append(formatted_enc)

        return supported_encodings
    except Exception as e:
        logger.error(f"获取支持的编码列表失败: {e}")
        # 如果获取所有编码失败，返回常用编码列表（已经是大写）
        return common_encodings
