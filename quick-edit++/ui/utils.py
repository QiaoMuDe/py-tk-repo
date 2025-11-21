#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from loguru import logger


def get_supported_encodings():
    """获取支持的编码列表

    Returns:
        list: 支持的编码列表，常用编码在前
    """
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
