#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SQL语言处理器

提供SQL脚本的语法识别和高亮规则
"""

import re
from typing import Dict, List, Any

from .base import LanguageHandler


class SQLHandler(LanguageHandler):
    """
    SQL语言处理器

    提供SQL脚本的语法识别和高亮规则
    """

    # SQL文件扩展名
    file_extensions = [".sql", ".ddl", ".dml", ".dql", ".dcl", ".tcl"]

    @classmethod
    def get_language_name(cls) -> str:
        """
        获取语言处理器名称

        Returns:
            str: 语言处理器名称"sql"
        """
        return "sql"

    def _setup_language(self):
        """设置SQL语言的语法规则"""
        # 定义模式处理顺序，确保字符串和注释有正确的优先级
        self._pattern_order = [
            "strings",  # 字符串放在第一位，确保优先匹配
            "comments",  # 注释放在第二位
            "identifiers",  # 标识符
            "keywords",  # 关键字
            "data_types",  # 数据类型
            "numbers",  # 数字
            "functions",  # 函数
            "operators",  # 操作符
            "variables",  # 变量
            "placeholders",  # 占位符
        ]

        # SQL关键字
        self._keywords = [
            # DDL关键字 - 数据定义语言
            "CREATE",
            "ALTER",
            "DROP",
            "TRUNCATE",
            "RENAME",
            # DML关键字 - 数据操作语言
            "INSERT",
            "UPDATE",
            "DELETE",
            "MERGE",
            "CALL",
            "EXPLAIN",
            "LOCK",
            # DQL关键字 - 数据查询语言
            "SELECT",
            "WITH",
            # DCL关键字 - 数据控制语言
            "GRANT",
            "REVOKE",
            "COMMIT",
            "ROLLBACK",
            "SAVEPOINT",
            "SET",
            "TRANSACTION",
            # TCL关键字 - 事务控制语言
            "START",
            "BEGIN",
            "END",
            # 查询子句关键字
            "FROM",
            "WHERE",
            "GROUP",
            "BY",
            "HAVING",
            "ORDER",
            "LIMIT",
            "OFFSET",
            "UNION",
            "ALL",
            "INTERSECT",
            "MINUS",
            "EXCEPT",
            # 连接关键字
            "JOIN",
            "INNER",
            "OUTER",
            "LEFT",
            "RIGHT",
            "FULL",
            "CROSS",
            "NATURAL",
            "ON",
            "USING",
            # 条件表达式关键字
            "CASE",
            "WHEN",
            "THEN",
            "ELSE",
            "END",
            "EXISTS",
            "IN",
            "ANY",
            "SOME",
            "BETWEEN",
            "LIKE",
            "IS",
            "NULL",
            "TRUE",
            "FALSE",
            "UNKNOWN",
            "IS NULL",
            "IS NOT NULL",
            "NOT IN",
            "NOT LIKE",
            "ILIKE",
            "NOT ILIKE",
            "NOT BETWEEN",
            # 模式匹配关键字
            "SIMILAR",
            "TO",
            "REGEXP",
            "RLIKE",
            # 范围和包含关键字
            "OVERLAPS",
            "CONTAINS",
            "CONTAINED",
            "BY",
            # 数据库对象关键字
            "TABLE",
            "VIEW",
            "SEQUENCE",
            "TRIGGER",
            "PROCEDURE",
            "FUNCTION",
            "PACKAGE",
            "TYPE",
            "BODY",
            "INDEX",
            "SYNONYM",
            "MATERIALIZED",
            # 约束关键字
            "PRIMARY",
            "KEY",
            "FOREIGN",
            "REFERENCES",
            "CHECK",
            "DEFAULT",
            "CONSTRAINT",
            "UNIQUE",
            "DISTINCT",
            # 流程控制关键字
            "DECLARE",
            "CURSOR",
            "FOR",
            "LOOP",
            "WHILE",
            "IF",
            "ELSEIF",
            "RETURN",
            "CONTINUE",
            "BREAK",
            "GOTO",
            # 执行关键字
            "EXEC",
            "EXECUTE",
            "PERFORM",
            "DO",
            # 数据库管理关键字
            "ANALYZE",
            "OPTIMIZE",
            "REPAIR",
            "SHOW",
            "DESCRIBE",
            "DESC",
            "USE",
            "DATABASE",
            "SCHEMA",
            "USER",
            "ROLE",
            "PRIVILEGES",
            "OWNER",
            "TABLESPACE",
            # 会话和系统关键字
            "TEMPORARY",
            "TEMP",
            "LOCAL",
            "GLOBAL",
            "SESSION",
            "SYSTEM",
            "PUBLIC",
            # 存储和缓存关键字
            "LOG",
            "NOLOGGING",
            "CACHE",
            "NOCACHE",
            # 表空间和存储参数关键字
            "INITIAL",
            "NEXT",
            "MINEXTENTS",
            "MAXEXTENTS",
            "PCTINCREASE",
            "FREELISTS",
            "FREELIST",
            "GROUPS",
            "BUFFER_POOL",
            "KEEP",
            "RECYCLE",
            "SEGMENT",
            "EXTENT",
            "BLOCK",
            # 行和标识符关键字
            "ROW",
            "ROWID",
            "ROWNUM",
            "LEVEL",
            "PRIOR",
            "CONNECT",
            # 日期和时间关键字
            "SYSDATE",
            "CURRENT_DATE",
            "CURRENT_TIME",
            "CURRENT_TIMESTAMP",
            "LOCALTIME",
            "LOCALTIMESTAMP",
            "INTERVAL",
            "DATE",
            "TIME",
            "TIMESTAMP",
            "YEAR",
            "MONTH",
            "DAY",
            "HOUR",
            "MINUTE",
            "SECOND",
            # 数学函数关键字
            "EXTRACT",
            "ADD_MONTHS",
            "MONTHS_BETWEEN",
            "NEXT_DAY",
            "LAST_DAY",
            "ROUND",
            "TRUNC",
            "CEIL",
            "FLOOR",
            "ABS",
            "SIGN",
            "SQRT",
            "POWER",
            "EXP",
            "LN",
            "LOG",
            "MOD",
            "REMAINDER",
            "SIN",
            "COS",
            "TAN",
            "ASIN",
            "ACOS",
            "ATAN",
            "ATAN2",
            "SINH",
            "COSH",
            "TANH",
            "DEGREES",
            "RADIANS",
            # 转换函数关键字
            "BIN",
            "OCT",
            "HEX",
            "ASCII",
            "CHR",
            "CONCAT",
            "LOWER",
            "UPPER",
            "INITCAP",
            "LENGTH",
            "LENGTHB",
            "SUBSTR",
            "SUBSTRB",
            "INSTR",
            "INSTRB",
            "LPAD",
            "RPAD",
            "LTRIM",
            "RTRIM",
            "TRIM",
            "REPLACE",
            "TRANSLATE",
            "REGEXP_INSTR",
            "REGEXP_REPLACE",
            "REGEXP_SUBSTR",
            "REGEXP_LIKE",
            # 类型转换关键字
            "TO_CHAR",
            "TO_DATE",
            "TO_NUMBER",
            "TO_TIMESTAMP",
            "TO_TIMESTAMP_TZ",
            "TO_YMINTERVAL",
            "TO_DSINTERVAL",
            "NUMTODSINTERVAL",
            "NUMTOYMINTERVAL",
            "CAST",
            "CONVERT",
            # 条件函数关键字
            "DECODE",
            "NVL",
            "NVL2",
            "NULLIF",
            "COALESCE",
            "GREATEST",
            "LEAST",
            # 系统和环境函数关键字
            "USERENV",
            "SYS_CONTEXT",
            "SYS_GUID",
            "UID",
            "USER",
            "VSIZE",
            "DUMP",
            # 二进制转换关键字
            "RAWTOHEX",
            "HEXTORAW",
            "CHARTOROWID",
            "ROWIDTOCHAR",
            # 集合关键字
            "MULTISET",
            "CARDINALITY",
            "COLLECT",
            "SET",
            "POWERMULTISET",
            "POWERMULTISET_BY",
            # 对象类型关键字
            "TREAT",
            "VALUE",
            "REF",
            "DEREF",
            "INSTANCE",
            "MEMBER",
            "STATIC",
            "FINAL",
            "INSTANTIABLE",
            "OVERRIDING",
            # 函数特性关键字
            "NOT",
            "DETERMINISTIC",
            "PARALLEL_ENABLE",
            "PIPELINED",
            "AGGREGATE",
            "RESULT_CACHE",
            # 权限和安全关键字
            "AUTHID",
            "CURRENT_USER",
            "DEFINER",
            # 窗口函数关键字
            "OVER",
            "WINDOW",
            "ROWS",
            "RANGE",
            "UNBOUNDED",
            "PRECEDING",
            "FOLLOWING",
            "CURRENT",
            "FIRST",
            "LAST",
            # 分区关键字
            "PARTITION",
            # 其他关键字
            "INTO",
            "VALUES",
            "AS",
            "ACCESSIBLE",
            "CASCADE",
            "COLUMN",
            "COLUMNS",
            "DEFERRABLE",
            "DEFERRED",
            "DEPTH",
            "DOMAIN",
            "EACH",
            "ENCODING",
            "EXCLUDE",
            "EXCLUDING",
            "FORCE",
            "GRANTED",
            "HIERARCHY",
            "HOLD",
            "INCLUDE",
            "INCLUDING",
            "INHERIT",
            "INPUT",
            "LANGUAGE",
            "LOCATION",
            "MAP",
            "MATCHED",
            "NAME",
            "NAMES",
            "NO",
            "NOCYCLE",
            "NOMAXVALUE",
            "NOMINVALUE",
            "NONE",
            "NOWAIT",
            "OBJECT",
            "OFF",
            "OID",
            "OPERATOR",
            "OPTION",
            "OPTIONS",
            "ORDERING",
            "OTHERS",
            "PASSWORD",
            "READ",
            "RECURSIVE",
            "REFERENCING",
            "REPEATABLE",
            "RESET",
            "RESTART",
            "RESTRICT",
            "RETURNING",
            "ROLLUP",
            "RULE",
            "SCHEMAS",
            "SEARCH",
            "SECURITY",
            "SEQUENCES",
            "SETS",
            "SHARE",
            "SIMILAR",
            "SKIP",
            "SNAPSHOT",
            "STATEMENT",
            "STATISTICS",
            "STDIN",
            "STDOUT",
            "STORAGE",
            "STRICT",
            "STRUCTURE",
            "SUBSTRING",
            "TEMPLATE",
            "TRAILING",
            "UNDER",
            "UNENCRYPTED",
            "UNTIL",
            "USAGE",
            "VALID",
            "VALIDATOR",
            "VARYING",
            "WITHOUT",
            "WORK",
            "WRAPPER",
            "WRITE",
            "ZONE",
            "AND",
            "OR",
        ]

        # 数据类型
        data_types = [
            # 数值类型
            "INTEGER",
            "INT",
            "SMALLINT",
            "BIGINT",
            "TINYINT",
            "MEDIUMINT",
            "DECIMAL",
            "NUMERIC",
            "REAL",
            "DOUBLE",
            "PRECISION",
            "FLOAT",
            "MONEY",
            "SMALLMONEY",
            # 字符串类型
            "CHARACTER",
            "CHAR",
            "VARCHAR",
            "VARCHAR2",
            "NVARCHAR",
            "NVARCHAR2",
            "TEXT",
            "LONG",
            "CLOB",
            "NCLOB",
            # 二进制类型
            "BLOB",
            "BFILE",
            "RAW",
            "LONG RAW",
            "BYTEA",
            "VARBIT",
            "BIT VARYING",
            # 日期和时间类型
            "DATE",
            "TIME",
            "TIMESTAMP",
            "INTERVAL",
            "YEAR",
            "MONTH",
            "DAY",
            "HOUR",
            "MINUTE",
            "SECOND",
            # 布尔和位类型
            "BOOLEAN",
            "BIT",
            # 唯一标识类型
            "UUID",
            "SERIAL",
            "BIGSERIAL",
            # JSON和XML类型
            "JSON",
            "JSONB",
            "XML",
            # 几何类型
            "GEOMETRY",
            "POINT",
            "LINESTRING",
            "POLYGON",
            "MULTIPOINT",
            "MULTILINESTRING",
            "MULTIPOLYGON",
            "GEOMETRYCOLLECTION",
            # 枚举和集合类型
            "ENUM",
            "SET",
        ]

        # SQL操作符
        operators = [
            # 算术操作符
            "+",
            "-",
            "*",
            "/",
            "%",
            "**",
            # 比较操作符
            "=",
            "==",
            "!=",
            "<",
            ">",
            "<=",
            ">=",
            "<>",
            "<=>",
            # 位操作符
            "||",
            "&&",
            "|",
            "&",
            "!",
            "^",
            "<<",
            ">>",
            "~",
            # 数组操作符
            "@>",
            "<@",
            # JSON操作符
            "->",
            "->>",
            "#>",
            "#>>",
            "?",
            "?&",
            "?|",
            # 其他操作符
            "::",
            ":=",
            "=>",
            "::=",
            # 括号和分隔符
            "(",
            ")",
            "[",
            "]",
            "{",
            "}",
            ",",
            ";",
            ".",
        ]

        # 正则表达式模式
        self._regex_patterns = {
            # 关键字 - 使用单词边界确保匹配完整单词，并添加忽略大小写标志
            # 按长度降序排序，确保长关键字优先匹配，避免短关键字"截胡"
            "keywords": r"(?<![a-zA-Z0-9_])("
            + "|".join(
                re.escape(k) for k in sorted(self._keywords, key=len, reverse=True)
            )
            + r")(?![a-zA-Z0-9_])",
            # 数据类型 - 使用单词边界确保匹配完整单词，并添加忽略大小写标志
            "data_types": r"\b("
            + "|".join(re.escape(dt) for dt in data_types)
            + r")\b",
            # 注释 - 单行注释和多行注释
            "comments": r"(--.*$|/\*[\s\S]*?\*/)",
            # 字符串 - 包括单引号、双引号字符串
            "strings": r"'(?:[^']|'')*'|\"(?:[^\"\\]|\\.)*\"",
            # 数字 - 包括整数、浮点数、科学计数法
            "numbers": r"\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b",
            # 函数 - 函数名后的括号
            "functions": r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*(?=\()",
            # 表名和列名 - 使用反引号、方括号或双引号括起来的标识符
            "identifiers": r"(`[^`]*`|\[[^\]]*\]|\"[^\"]*\")",
            # 操作符 - 现在只有特殊字符操作符，直接转义
            "operators": "("
            + "|".join(
                # 所有剩余操作符都是特殊字符，都需要转义
                re.escape(op)
                for op in operators
            )
            + ")",
            # 变量 - @开头或:开头的变量
            "variables": r"@[a-zA-Z_][a-zA-Z0-9_]*|:[a-zA-Z_][a-zA-Z0-9_]*",
            # 占位符 - ?或:1格式
            "placeholders": r"\?|:\d+",
        }

        # 正则表达式编译标志 - 关键字和数据类型使用忽略大小写
        self._regex_flags = {
            "keywords": re.IGNORECASE,
            "data_types": re.IGNORECASE,
            "comments": 0,
            "strings": 0,
            "numbers": 0,
            "functions": 0,
            "identifiers": 0,
            "operators": re.IGNORECASE,  # 操作符也忽略大小写，如AND/OR/NOT等
            "variables": 0,
            "placeholders": 0,
        }

        # 标签样式 - 使用适度的配色方案
        self._tag_styles = {
            # 关键字 - 橙色
            "keywords": {
                "foreground": "#FF7F00",
            },
            # 数据类型 - 蓝色
            "data_types": {
                "foreground": "#0066CC",
            },
            # 注释 - 绿色
            "comments": {
                "foreground": "#008000",
            },
            # 字符串 - 红色
            "strings": {
                "foreground": "#CC0000",
            },
            # 数字 - 深红色
            "numbers": {
                "foreground": "#990000",
            },
            # 函数 - 品红色
            "functions": {
                "foreground": "#FF1493",
            },
            # 标识符 - 青色
            "identifiers": {
                "foreground": "#008B8B",
            },
            # 操作符 - 深灰色
            "operators": {
                "foreground": "#666666",
            },
            # 变量 - 深紫色
            "variables": {
                "foreground": "#663366",
            },
            # 占位符 - 橙色
            "placeholders": {
                "foreground": "#CC6600",
            },
        }

    def get_pattern_order(self) -> List[str]:
        """
        获取模式处理顺序

        Returns:
            List[str]: 模式处理顺序列表
        """
        return self._pattern_order
