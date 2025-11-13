#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PowerShell语言处理器

提供PowerShell脚本的语法识别和高亮规则
"""

import re
from typing import Dict, List, Any

from .base import LanguageHandler


class PowerShellHandler(LanguageHandler):
    """
    PowerShell语言处理器

    提供PowerShell脚本的语法识别和高亮规则
    """

    # PowerShell文件扩展名
    file_extensions = [".ps1", ".psm1", ".psd1"]

    def _setup_language(self):
        """设置PowerShell语言的语法规则"""
        # PowerShell关键字
        self._keywords = [
            # 控制流关键字
            "if",
            "else",
            "elseif",
            "for",
            "foreach",
            "while",
            "do",
            "until",
            "switch",
            "break",
            "continue",
            "return",
            "exit",
            "throw",
            "trap",
            # 函数相关
            "function",
            "filter",
            "workflow",
            "param",
            "begin",
            "process",
            "end",
            "dynamicparam",
            # 作用域
            "global",
            "local",
            "script",
            "private",
            # 其他关键字
            "class",
            "enum",
            "using",
            "module",
            "namespace",
            "in",
            "where",
            "select",
            "format",
            "try",
            "catch",
            "finally",
            "data",
            "inlinescript",
            "parallel",
            "sequence",
        ]

        # 内置命令和函数
        builtins = [
            # 常用命令
            "Write-Host",
            "Write-Output",
            "Write-Error",
            "Write-Warning",
            "Write-Verbose",
            "Write-Debug",
            "Write-Information",
            "Read-Host",
            "Get-Content",
            "Set-Content",
            "Add-Content",
            "Out-File",
            "Out-String",
            "Out-Null",
            "Out-Default",
            "Out-GridView",
            "Out-Printer",
            # 对象操作
            "Get-Item",
            "Set-Item",
            "New-Item",
            "Remove-Item",
            "Copy-Item",
            "Move-Item",
            "Rename-Item",
            "Get-ChildItem",
            "Get-ItemProperty",
            "Set-ItemProperty",
            "Get-Location",
            "Set-Location",
            "Push-Location",
            "Pop-Location",
            # 变量操作
            "Get-Variable",
            "Set-Variable",
            "New-Variable",
            "Remove-Variable",
            "Clear-Variable",
            # 环境变量
            "Get-ChildItem",
            "Get-EnvironmentVariable",
            "Set-EnvironmentVariable",
            # 进程和服务
            "Get-Process",
            "Stop-Process",
            "Start-Process",
            "Wait-Process",
            "Get-Service",
            "Start-Service",
            "Stop-Service",
            "Restart-Service",
            "Suspend-Service",
            "Resume-Service",
            # 注册表
            "Get-Item",
            "New-Item",
            "Remove-Item",
            "Set-Item",
            "Get-ItemProperty",
            "Set-ItemProperty",
            "New-ItemProperty",
            "Remove-ItemProperty",
            # 其他常用命令
            "Get-Command",
            "Get-Help",
            "Get-Member",
            "Select-Object",
            "Where-Object",
            "ForEach-Object",
            "Sort-Object",
            "Group-Object",
            "Measure-Object",
            "Compare-Object",
            "Format-Table",
            "Format-List",
            "Format-Wide",
            "Format-Custom",
            "Export-Csv",
            "Import-Csv",
            "ConvertTo-Json",
            "ConvertFrom-Json",
            "ConvertTo-Xml",
            "ConvertFrom-Xml",
            "ConvertTo-Html",
            "Invoke-Expression",
            "Invoke-Command",
            "Invoke-WebRequest",
            "Invoke-RestMethod",
            "Start-Sleep",
            "Test-Path",
            "Test-Connection",
            "Join-Path",
            "Split-Path",
            "Resolve-Path",
            "Get-Date",
            "Get-Random",
        ]

        # 正则表达式模式
        self._regex_patterns = {
            # 关键字 - 使用单词边界确保匹配完整单词
            "keywords": r"\b("
            + "|".join(re.escape(k) for k in self._keywords)
            + r")\b",
            # 内置命令
            "builtins": r"\b(" + "|".join(re.escape(b) for b in builtins) + r")\b",
            # 注释 - 从#开始到行尾
            "comments": r"#.*$",
            # 块注释 - <# ... #>
            "block_comments": r"<#[\s\S]*?#>",
            # 字符串 - 包括单引号、双引号、here字符串
            "strings": r'(@"[\s\S]*?"|@\'[\s\S]*?\'|"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')',
            # 数字 - 包括整数、浮点数、科学计数法
            "numbers": r"\b\d+\.?\d*(?:[eE][+-]?\d+)?\b",
            # 变量 - $开头
            "variables": r"\$[a-zA-Z_][a-zA-Z0-9_]*|\$\{[^}]*\}|\$\$|\$[0-9]+|\$[?^]",
            # 类型 - [TypeName]格式
            "types": r"\[[a-zA-Z_][a-zA-Z0-9_.\[\]]*\]",
            # 函数定义 - function关键字或函数名后的括号
            "functions": r"\b([a-zA-Z_][a-zA-Z0-9_-]*)\s*(?=\()|\bfunction\s+([a-zA-Z_][a-zA-Z0-9_-]*)",
            # 操作符
            "operators": r"(\+|\-|\*|\/|%|=|==|!=|<|>|<=|>=|\-eq|\-ne|\-lt|\-le|\-gt|\-ge|\-like|\-notlike|\-match|\-notmatch|\-replace|\-contains|\-notcontains|\-in|\-notin|\-and|\-or|\-not|\-band|\-bor|\-bxor|\-bnot|\-f|\-shl|\-shr|\-is|\-isnot|\-as|\-join|\-split|\-replace|\-creplace)",
            # 路径 - 以/开头或包含/的字符串
            "paths": r"(\\[a-zA-Z0-9_\-\.\\]+|[a-zA-Z]:\\[a-zA-Z0-9_\-\.\\]*|[a-zA-Z0-9_\-\.\\]+\\[a-zA-Z0-9_\-\.\\]*|/[a-zA-Z0-9_\-\.\/]+)",
            # 参数 - -开头的参数
            "parameters": r"\-[a-zA-Z_][a-zA-Z0-9_]*",
        }

        # 标签样式 - 使用适合PowerShell的配色方案
        self._tag_styles = {
            # 关键字 - 深蓝色
            "keywords": {
                "foreground": "#000080",
            },
            # 内置命令 - 蓝色
            "builtins": {
                "foreground": "#0000FF",
            },
            # 注释 - 绿色
            "comments": {
                "foreground": "#00AA00",
            },
            # 块注释 - 绿色
            "block_comments": {
                "foreground": "#00AA00",
            },
            # 字符串 - 棕色
            "strings": {
                "foreground": "#8B4513",
            },
            # 数字 - 深红色
            "numbers": {
                "foreground": "#8B0000",
            },
            # 变量 - 紫色
            "variables": {
                "foreground": "#800080",
            },
            # 类型 - 深青色
            "types": {
                "foreground": "#008B8B",
            },
            # 函数 - 深紫色
            "functions": {
                "foreground": "#4B0082",
            },
            # 操作符 - 黑色
            "operators": {
                "foreground": "#000000",
            },
            # 路径 - 深绿色
            "paths": {
                "foreground": "#006400",
            },
            # 参数 - 深橙色
            "parameters": {
                "foreground": "#FF8C00",
            },
        }
