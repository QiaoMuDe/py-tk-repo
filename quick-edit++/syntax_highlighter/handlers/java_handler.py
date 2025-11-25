#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Java语言处理器

提供.java文件的语法高亮支持
"""

import re
from typing import Dict, List, Any

from .base import LanguageHandler


class JavaHandler(LanguageHandler):
    """
    Java语言处理器

    提供.java文件的语法高亮支持
    """

    # Java文件扩展名
    file_extensions = [".java", ".class", ".jar"]  # .class和.jar是Java编译后的文件

    @classmethod
    def get_language_name(cls) -> str:
        """
        获取语言处理器名称

        Returns:
            str: 语言处理器名称"java"
        """
        return "java"

    def get_pattern_order(self):
        """
        获取模式处理顺序

        Returns:
            list: 模式处理顺序列表
        """
        return self._pattern_order

    def _setup_language(self):
        """
        设置Java语言的语法高亮规则
        """
        # 定义模式处理顺序，确保字符串和注释有正确的优先级
        self._pattern_order = [
            "string",  # 字符串放在第一位，确保优先匹配
            "char",  # 字符放在第二位
            "comment",  # 单行注释放在第三位
            "multiline_comment",  # 多行注释放在第四位
            "javadoc_comment",  # JavaDoc注释放在第五位
            "number",  # 数字
            "hex_number",  # 十六进制数字
            "binary_number",  # 二进制数字
            "octal_number",  # 八进制数字
            "boolean",  # 布尔值
            "null",  # null值
            "builtin",  # 内置类和方法
            "annotation",  # 注解
            "package_decl",  # 包声明
            "import_decl",  # 导入声明
            "class_def",  # 类定义
            "method_def",  # 方法定义
            "method_call",  # 方法调用
            "property_access",  # 属性访问
            "variable_decl",  # 变量声明
            "generic",  # 泛型
            "lambda",  # Lambda表达式
            "method_ref",  # 方法引用
            "operator",  # 操作符
        ]
        # Java关键字
        self._keywords = [
            # 基本关键字
            "abstract",
            "assert",
            "boolean",
            "break",
            "byte",
            "case",
            "catch",
            "char",
            "class",
            "const",
            "continue",
            "default",
            "do",
            "double",
            "else",
            "enum",
            "extends",
            "final",
            "finally",
            "float",
            "for",
            "goto",
            "if",
            "implements",
            "import",
            "instanceof",
            "int",
            "interface",
            "long",
            "native",
            "new",
            "package",
            "private",
            "protected",
            "public",
            "return",
            "short",
            "static",
            "strictfp",
            "super",
            "switch",
            "synchronized",
            "this",
            "throw",
            "throws",
            "transient",
            "try",
            "void",
            "volatile",
            "while",
            # Java 8+ 关键字
            "var",
            "yield",
            "record",
            "sealed",
            "non-sealed",
            "permits",
            # 保留字
            "true",
            "false",
            "null",
        ]

        # Java操作符 - 按类型分类组织
        self._operators = [
            # 算术操作符
            "+",
            "-",
            "*",
            "/",
            "%",
            # 比较操作符
            "==",
            "!=",
            "<",
            ">",
            "<=",
            ">=",
            # 逻辑操作符
            "&&",
            "||",
            "!",
            # 位操作符
            "&",
            "|",
            "^",
            "~",
            "<<",
            ">>",
            ">>>",
            # 赋值操作符
            "=",
            "+=",
            "-=",
            "*=",
            "/=",
            "%=",
            "&=",
            "|=",
            "^=",
            "<<=",
            ">>=",
            ">>>=",
            # 三元操作符
            "?",
            ":",
            # 其他操作符
            "++",
            "--",
            "instanceof",
        ]

        # Java访问修饰符
        self._access_modifiers = [
            "public",
            "private",
            "protected",
        ]

        # Java非访问修饰符
        self._non_access_modifiers = [
            "abstract",
            "final",
            "static",
            "synchronized",
            "native",
            "strictfp",
            "transient",
            "volatile",
        ]

        # Java类/接口/枚举类型
        self._class_types = [
            "class",
            "interface",
            "enum",
            "record",
        ]

        # Java内置类和方法
        self._builtins = [
            # 基本类型包装类
            "Boolean",
            "Byte",
            "Character",
            "Short",
            "Integer",
            "Long",
            "Float",
            "Double",
            # 字符串相关
            "String",
            "StringBuilder",
            "StringBuffer",
            "StringTokenizer",
            # 集合框架
            "List",
            "ArrayList",
            "LinkedList",
            "Vector",
            "Stack",
            "Set",
            "HashSet",
            "TreeSet",
            "LinkedHashSet",
            "Map",
            "HashMap",
            "TreeMap",
            "LinkedHashMap",
            "Hashtable",
            "Properties",
            "Dictionary",
            "Queue",
            "Deque",
            "ArrayDeque",
            "PriorityQueue",
            "Collection",
            "Collections",
            "Iterator",
            "ListIterator",
            "Enumeration",
            "Comparator",
            "Comparable",
            # IO相关
            "File",
            "InputStream",
            "OutputStream",
            "Reader",
            "Writer",
            "FileInputStream",
            "FileOutputStream",
            "FileReader",
            "FileWriter",
            "BufferedReader",
            "BufferedWriter",
            "PrintStream",
            "PrintWriter",
            "DataInputStream",
            "DataOutputStream",
            "ObjectInputStream",
            "ObjectOutputStream",
            "Serializable",
            "Externalizable",
            # 网络相关
            "URL",
            "URLConnection",
            "HttpURLConnection",
            "Socket",
            "ServerSocket",
            "DatagramSocket",
            "DatagramPacket",
            "InetAddress",
            "URI",
            # 线程相关
            "Thread",
            "Runnable",
            "ThreadLocal",
            "Executor",
            "ExecutorService",
            "ScheduledExecutorService",
            "ThreadPoolExecutor",
            "ForkJoinPool",
            "Future",
            "Callable",
            "CompletableFuture",
            "Semaphore",
            "CountDownLatch",
            "CyclicBarrier",
            "ReentrantLock",
            "Condition",
            "Lock",
            "ReadWriteLock",
            "AtomicInteger",
            "AtomicLong",
            "AtomicBoolean",
            "AtomicReference",
            # 反射相关
            "Class",
            "Method",
            "Field",
            "Constructor",
            "Modifier",
            "Array",
            "Proxy",
            # 异常相关
            "Exception",
            "RuntimeException",
            "Error",
            "Throwable",
            "IOException",
            "FileNotFoundException",
            "ClassNotFoundException",
            "NoSuchMethodException",
            "IllegalAccessException",
            "InstantiationException",
            "NumberFormatException",
            "NullPointerException",
            "ArrayIndexOutOfBoundsException",
            "StringIndexOutOfBoundsException",
            "ArithmeticException",
            "ClassCastException",
            "IllegalArgumentException",
            "IllegalStateException",
            "UnsupportedOperationException",
            # 时间日期相关
            "Date",
            "Time",
            "Timestamp",
            "Calendar",
            "GregorianCalendar",
            "SimpleDateFormat",
            "LocalDate",
            "LocalTime",
            "LocalDateTime",
            "ZonedDateTime",
            "Instant",
            "Duration",
            "Period",
            "DateTimeFormatter",
            "TimeZone",
            "Locale",
            # 数学相关
            "Math",
            "BigInteger",
            "BigDecimal",
            "Random",
            "SecureRandom",
            "RoundingMode",
            # 系统相关
            "System",
            "Runtime",
            "Process",
            "ProcessBuilder",
            "SecurityManager",
            "ClassLoader",
            "Package",
            "Module",
            "ModuleLayer",
            # 注解相关
            "Annotation",
            "RetentionPolicy",
            "ElementType",
            "Target",
            "Retention",
            "Documented",
            "Inherited",
            "Repeatable",
            "Deprecated",
            "Override",
            "SuppressWarnings",
            # 泛型相关
            "Type",
            "ParameterizedType",
            "TypeVariable",
            "GenericArrayType",
            "WildcardType",
            # JavaFX相关
            "Application",
            "Stage",
            "Scene",
            "Node",
            "Parent",
            "Group",
            "Pane",
            "HBox",
            "VBox",
            "BorderPane",
            "GridPane",
            "FlowPane",
            "StackPane",
            "Button",
            "Label",
            "TextField",
            "TextArea",
            "CheckBox",
            "RadioButton",
            "ToggleButton",
            "ComboBox",
            "ListView",
            "TableView",
            "TreeView",
            "ImageView",
            "Canvas",
            "GraphicsContext",
            "Color",
            "Font",
            "Image",
            "MediaPlayer",
            "Media",
            # Swing相关
            "JFrame",
            "JDialog",
            "JPanel",
            "JButton",
            "JLabel",
            "JTextField",
            "JTextArea",
            "JCheckBox",
            "JRadioButton",
            "JComboBox",
            "JList",
            "JTable",
            "JTree",
            "JMenuBar",
            "JMenu",
            "JMenuItem",
            "JOptionPane",
            "JScrollPane",
            "JSplitPane",
            "JTabbedPane",
            "JToolBar",
            "JProgressBar",
            "JSlider",
            "JColorChooser",
            "JFileChooser",
            # 常用方法
            "println",
            "print",
            "printf",
            "format",
            "valueOf",
            "toString",
            "equals",
            "hashCode",
            "compareTo",
            "clone",
            "finalize",
            "getClass",
            "notify",
            "notifyAll",
            "wait",
            "add",
            "remove",
            "get",
            "set",
            "put",
            "contains",
            "isEmpty",
            "size",
            "clear",
            "iterator",
            "toArray",
            "stream",
            "parallelStream",
            "filter",
            "map",
            "reduce",
            "collect",
            "forEach",
            "sorted",
            "distinct",
            "limit",
            "skip",
            "count",
            "anyMatch",
            "allMatch",
            "noneMatch",
            "findFirst",
            "findAny",
            "min",
            "max",
            "average",
            "sum",
            "join",
            "split",
            "substring",
            "replace",
            "replaceAll",
            "matches",
            "startsWith",
            "endsWith",
            "toLowerCase",
            "toUpperCase",
            "trim",
            "length",
            "charAt",
            "getBytes",
            "toCharArray",
            "indexOf",
            "lastIndexOf",
            "substring",
            "concat",
            "format",
        ]

        # 正则表达式模式
        self._regex_patterns = {
            # 单行注释
            "comment": r"//.*$",
            # 多行注释
            "multiline_comment": r"/\*.*?\*/",
            # JavaDoc注释
            "javadoc_comment": r"/\*\*.*?\*/",
            # 字符串
            "string": r'"(?:[^"\\]|\\.)*"',
            # 字符
            "char": r"'(?:[^'\\]|\\.)'",
            # 数字
            "number": r"\b\d+\.?\d*([eE][+-]?\d+)?[fFdDlL]?\b",
            # 十六进制数字
            "hex_number": r"0[xX][0-9a-fA-F]+\.?[0-9a-fA-F]*([pP][+-]?\d+)?[fFdDlL]?\b",
            # 二进制数字
            "binary_number": r"0[bB][01]+\.?[01]*[fFdDlL]?\b",
            # 八进制数字
            "octal_number": r"0[0-7]+\.?[0-7]*[fFdDlL]?\b",
            # 布尔值
            "boolean": r"\b(true|false)\b",
            # null值
            "null": r"\bnull\b",
            # 内置类和方法 - 使用属性数组并转义展开
            "builtin": r"\b(" + "|".join(re.escape(b) for b in self._builtins) + r")\b",
            # 类定义 - 使用属性数组并转义展开
            "class_def": r"\b(?:"
            + "|".join(re.escape(mod) for mod in self._access_modifiers)
            + r")?\s*(?:"
            + "|".join(re.escape(mod) for mod in self._non_access_modifiers)
            + r")?\s*(?:"
            + "|".join(re.escape(cls) for cls in self._class_types)
            + r")\s+[a-zA-Z_][a-zA-Z0-9_]*",
            # 方法定义 - 只匹配方法名部分，不包括括号
            "method_def": r"\b(?:"
            + "|".join(re.escape(mod) for mod in self._access_modifiers)
            + r")?\s*(?:"
            + "|".join(re.escape(mod) for mod in self._non_access_modifiers)
            + r")?\s*(?:[a-zA-Z_][a-zA-Z0-9_]*\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*(?=\s*\()",
            # 方法调用 - 只匹配方法名部分，不包括括号
            "method_call": r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*(?=\s*\()",
            # 属性访问
            "property_access": r"[a-zA-Z_][a-zA-Z0-9_]*\s*\.\s*[a-zA-Z_][a-zA-Z0-9_]*",
            # 变量声明
            "variable_decl": r"\b(?:final|static)?\s*[a-zA-Z_][a-zA-Z0-9_]*\s+[a-zA-Z_][a-zA-Z0-9_]*(?:\s*=\s*[^;,]+)?",
            # 注解
            "annotation": r"@[a-zA-Z_][a-zA-Z0-9_]*(?:\([^)]*\))?",
            # 包声明
            "package_decl": r"\bpackage\s+[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*",
            # 导入声明
            "import_decl": r"\bimport\s+(?:static\s+)?[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*(?:\.\*)?",
            # 操作符 - 使用属性数组并转义展开
            "operator": r"(" + "|".join(re.escape(op) for op in self._operators) + r")",
            # 泛型
            "generic": r"<[a-zA-Z_][a-zA-Z0-9_]*(?:\s*,\s*[a-zA-Z_][a-zA-Z0-9_]*)*(?:\s+extends\s+[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)?>",
            # Lambda表达式
            "lambda": r"\([^)]*\)\s*->|[^,=<>]+\s*->",
            # 方法引用
            "method_ref": r"[a-zA-Z_][a-zA-Z0-9_]*::[a-zA-Z_][a-zA-Z0-9_]*",
        }

        # 标签样式 - 使用更鲜明、更深邃的颜色方案以提高可读性
        self._tag_styles = {
            "comment": {
                "foreground": "#008000",
            },  # 深绿色用于单行注释
            "multiline_comment": {
                "foreground": "#008000",
            },  # 深绿色用于多行注释
            "javadoc_comment": {
                "foreground": "#008000",
            },  # 深绿色用于JavaDoc注释
            "string": {"foreground": "#A31515"},  # 深红色用于字符串
            "char": {"foreground": "#A31515"},  # 深红色用于字符
            "number": {"foreground": "#098658"},  # 深绿色用于数字
            "hex_number": {"foreground": "#098658"},  # 深绿色用于十六进制数字
            "binary_number": {"foreground": "#098658"},  # 深绿色用于二进制数字
            "octal_number": {"foreground": "#098658"},  # 深绿色用于八进制数字
            "boolean": {"foreground": "#0000FF"},  # 纯蓝色用于布尔值
            "null": {"foreground": "#0000FF"},  # 纯蓝色用于null值
            "builtin": {"foreground": "#008080"},  # 深青色用于内置类和方法
            "class_def": {
                "foreground": "#0000FF",
            },  # 纯蓝色用于类定义
            "method_def": {
                "foreground": "#795E26",
            },  # 深棕色用于方法定义
            "method_call": {"foreground": "#795E26"},  # 深棕色用于方法调用
            "property_access": {"foreground": "#001080"},  # 深蓝色用于属性访问
            "variable_decl": {"foreground": "#800080"},  # 深紫色用于变量声明
            "annotation": {"foreground": "#800080"},  # 深紫色用于注解
            "package_decl": {"foreground": "#800080"},  # 深紫色用于包声明
            "import_decl": {"foreground": "#800080"},  # 深紫色用于导入声明
            "operator": {"foreground": "#000000"},  # 黑色用于操作符
            "generic": {"foreground": "#008080"},  # 深青色用于泛型
            "lambda": {"foreground": "#FF4500"},  # 深橙色用于Lambda表达式
            "method_ref": {"foreground": "#FF4500"},  # 深橙色用于方法引用
        }
