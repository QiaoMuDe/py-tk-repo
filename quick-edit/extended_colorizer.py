"""
扩展idlelib.colorizer支持多种编程语言的语法高亮
"""

import re
from idlelib.colorizer import ColorDelegator
from idlelib.configHandler import idleConf


class LanguageColorDelegator(ColorDelegator):
    """
    扩展的语言语法高亮基类
    """

    def __init__(self, language="python"):
        super().__init__()
        self.language = language
        self._setup_language_patterns()

    def _setup_language_patterns(self):
        """设置语言特定的正则表达式模式"""
        patterns = self._get_language_patterns()
        self.prog = re.compile(self._build_pattern(patterns), re.S)

    def _get_language_patterns(self):
        """获取语言特定的模式定义"""
        language_map = {
            "python": self._python_patterns,
            "javascript": self._javascript_patterns,
            "html": self._html_patterns,
            "css": self._css_patterns,
            "json": self._json_patterns,
            "sql": self._sql_patterns,
        }
        return language_map.get(self.language, self._python_patterns)()

    def _build_pattern(self, patterns):
        """构建完整的正则表达式模式"""
        return "|".join(patterns)

    def _python_patterns(self):
        """Python语法模式"""
        import keyword
        import __builtin__

        kw = r"\b" + self.any("KEYWORD", keyword.kwlist) + r"\b"

        builtinlist = [
            str(name) for name in dir(__builtin__) if not name.startswith("_")
        ]
        if "print" in builtinlist:
            builtinlist.remove("print")
        builtin = r"([^.'\"\\#]\b|^)" + self.any("BUILTIN", builtinlist) + r"\b"

        comment = self.any("COMMENT", [r"#[^\n]*"])

        stringprefix = r"(\br|u|ur|R|U|UR|Ur|uR|b|B|br|Br|bR|BR)?"
        sqstring = stringprefix + r"'[^'\\\n]*(\\.[^'\\\n]*)*'?"
        dqstring = stringprefix + r'"[^"\\\n]*(\\.[^"\\\n]*)*"?'
        sq3string = stringprefix + r"'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?"
        dq3string = stringprefix + r'"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?'
        string = self.any("STRING", [sq3string, dq3string, sqstring, dqstring])

        return [kw, builtin, comment, string, self.any("SYNC", [r"\n"])]

    def _javascript_patterns(self):
        """JavaScript语法模式"""
        js_keywords = [
            "break",
            "case",
            "catch",
            "class",
            "const",
            "continue",
            "debugger",
            "default",
            "delete",
            "do",
            "else",
            "export",
            "extends",
            "finally",
            "for",
            "function",
            "if",
            "import",
            "in",
            "instanceof",
            "new",
            "return",
            "super",
            "switch",
            "this",
            "throw",
            "try",
            "typeof",
            "var",
            "void",
            "while",
            "with",
            "yield",
            "let",
            "static",
            "async",
            "await",
        ]

        js_builtins = [
            "Array",
            "Boolean",
            "Date",
            "Error",
            "Function",
            "Math",
            "Number",
            "Object",
            "RegExp",
            "String",
            "Symbol",
            "Promise",
            "Set",
            "Map",
            "console",
            "alert",
            "prompt",
            "confirm",
            "document",
            "window",
        ]

        kw = r"\b" + self.any("KEYWORD", js_keywords) + r"\b"
        builtin = r"\b" + self.any("BUILTIN", js_builtins) + r"\b"

        comment = self.any("COMMENT", [r"//[^\n]*", r"/\*.*?\*/"])

        string = self.any(
            "STRING",
            [
                r'"[^"\\]*(\\.[^"\\]*)*"',
                r"'[^'\\]*(\\.[^'\\]*)*'",
                r"`[^`\\]*(\\.[^`\\]*)*`",
            ],
        )

        regex = self.any("REGEX", [r"/[^/\\]*(\\.[^/\\]*)*/[gimuy]*"])

        return [kw, builtin, comment, string, regex, self.any("SYNC", [r"\n"])]

    def _html_patterns(self):
        """HTML语法模式"""
        html_tags = [
            "html",
            "head",
            "title",
            "meta",
            "link",
            "script",
            "body",
            "div",
            "span",
            "p",
            "a",
            "img",
            "ul",
            "ol",
            "li",
            "table",
            "tr",
            "td",
            "th",
            "form",
            "input",
            "button",
            "select",
            "option",
            "textarea",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "br",
            "hr",
            "iframe",
        ]

        tag_name = self.any("TAG", [r"<\/?\b" + "|".join(html_tags) + r"\b"])
        attribute = self.any("ATTRIBUTE", [r"\b\w+\s*="])
        attribute_value = self.any("STRING", [r'"[^"]*"', r"'[^']*'"])
        comment = self.any("COMMENT", [r"<!--.*?-->"])

        return [
            tag_name,
            attribute,
            attribute_value,
            comment,
            self.any("SYNC", [r"\n"]),
        ]

    def _css_patterns(self):
        """CSS语法模式"""
        css_properties = [
            "color",
            "background",
            "font",
            "margin",
            "padding",
            "border",
            "width",
            "height",
            "display",
            "position",
            "top",
            "right",
            "bottom",
            "left",
            "float",
            "clear",
            "overflow",
            "text-align",
            "vertical-align",
            "font-size",
            "font-weight",
            "font-family",
            "line-height",
        ]

        css_keywords = [
            "color",
            "background",
            "font",
            "margin",
            "padding",
            "border",
            "width",
            "height",
            "display",
            "position",
            "top",
            "right",
            "bottom",
            "left",
            "float",
            "clear",
            "overflow",
            "text-align",
            "vertical-align",
            "font-size",
            "font-weight",
            "font-family",
            "line-height",
            "important",
            "inherit",
            "initial",
            "unset",
        ]

        property_name = self.any("PROPERTY", [r"\b" + "|".join(css_properties) + r"\b"])
        keyword = self.any("KEYWORD", [r"\b" + "|".join(css_keywords) + r"\b"])
        value = self.any("STRING", [r'"[^"]*"', r"'[^']*'"])
        number = self.any("NUMBER", [r"\b\d+(\.\d+)?(px|em|rem|%|vh|vw|deg)?\b"])
        comment = self.any("COMMENT", [r"/\*.*?\*/"])

        return [
            property_name,
            keyword,
            value,
            number,
            comment,
            self.any("SYNC", [r"\n"]),
        ]

    def _json_patterns(self):
        """JSON语法模式"""
        keyword = self.any("KEYWORD", ["true", "false", "null"])
        string = self.any("STRING", [r'"[^"\\]*(\\.[^"\\]*)*"'])
        number = self.any("NUMBER", [r"-?\d+(\.\d+)?([eE][+-]?\d+)?"])

        return [keyword, string, number, self.any("SYNC", [r"\n"])]

    def _sql_patterns(self):
        """SQL语法模式"""
        sql_keywords = [
            "SELECT",
            "INSERT",
            "UPDATE",
            "DELETE",
            "FROM",
            "WHERE",
            "JOIN",
            "ON",
            "GROUP",
            "BY",
            "HAVING",
            "ORDER",
            "LIMIT",
            "OFFSET",
            "INNER",
            "LEFT",
            "RIGHT",
            "OUTER",
            "FULL",
            "CREATE",
            "ALTER",
            "DROP",
            "TABLE",
            "DATABASE",
            "INDEX",
            "PRIMARY",
            "KEY",
            "FOREIGN",
            "REFERENCES",
            "NULL",
            "NOT",
            "AND",
            "OR",
            "IN",
            "BETWEEN",
            "LIKE",
            "IS",
            "AS",
        ]

        kw = self.any("KEYWORD", sql_keywords)
        string = self.any("STRING", [r"'[^']*'", r'"[^"]*"'])
        number = self.any("NUMBER", [r"\b\d+(\.\d+)?\b"])
        comment = self.any("COMMENT", [r"--[^\n]*", r"/\*.*?\*/"])

        return [kw, string, number, comment, self.any("SYNC", [r"\n"])]

    def any(self, name, alternates):
        """创建命名组的正则表达式"""
        if not alternates:
            return ""
        return "(?P<%s>" % name + "|".join(alternates) + ")"

    def set_language(self, language):
        """切换语言"""
        self.language = language
        self._setup_language_patterns()
        # 重新应用语法高亮
        if self.delegate:
            self.notify_range("1.0", "end")


class SyntaxHighlighter:
    """
    语法高亮管理器，支持多种语言切换
    """

    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.current_language = None
        self.color_delegator = None
        self.percolator = None

    def set_language(self, language="python"):
        """设置当前语言"""
        if self.current_language == language:
            return

        # 移除现有的语法高亮
        if self.color_delegator and self.percolator:
            self.percolator.removefilter(self.color_delegator)

        # 创建新的语言专用ColorDelegator
        self.color_delegator = LanguageColorDelegator(language)

        # 创建或获取Percolator
        if not self.percolator:
            from idlelib.percolator import Percolator

            self.percolator = Percolator(self.text_widget)

        # 插入新的过滤器
        self.percolator.insertfilter(self.color_delegator)
        self.current_language = language

        # 应用颜色配置
        self._configure_colors()

    def _configure_colors(self):
        """配置颜色主题"""
        theme = idleConf.GetOption("main", "Theme", "name")

        # 定义颜色映射
        color_map = {
            "KEYWORD": idleConf.GetHighlight(
                theme, "keyword", default={"foreground": "#0000FF"}
            ),
            "BUILTIN": idleConf.GetHighlight(
                theme, "builtin", default={"foreground": "#7F7F00"}
            ),
            "STRING": idleConf.GetHighlight(
                theme, "string", default={"foreground": "#008000"}
            ),
            "COMMENT": idleConf.GetHighlight(
                theme, "comment", default={"foreground": "#808080"}
            ),
            "TAG": {"foreground": "#0000FF"},  # HTML标签
            "ATTRIBUTE": {"foreground": "#7F007F"},  # HTML属性
            "PROPERTY": {"foreground": "#0000FF"},  # CSS属性
            "NUMBER": {"foreground": "#FF0000"},  # 数字
            "REGEX": {"foreground": "#FF8000"},  # 正则表达式
            "SYNC": {"background": None, "foreground": None},
        }

        # 应用颜色配置
        for tag, cnf in color_map.items():
            if cnf:
                self.text_widget.tag_configure(tag, **cnf)

        # 确保选择高亮在最上层
        self.text_widget.tag_raise("sel")

    def get_supported_languages(self):
        """获取支持的语言列表"""
        return ["python", "javascript", "html", "css", "json", "sql"]
