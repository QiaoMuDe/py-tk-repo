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
    
    def _setup_language(self):
        """
        设置Java语言的语法高亮规则
        """
        # Java关键字
        self._keywords = [
            # 基本关键字
            "abstract", "assert", "boolean", "break", "byte", "case", "catch", "char", 
            "class", "const", "continue", "default", "do", "double", "else", "enum", 
            "extends", "final", "finally", "float", "for", "goto", "if", "implements", 
            "import", "instanceof", "int", "interface", "long", "native", "new", "package", 
            "private", "protected", "public", "return", "short", "static", "strictfp", 
            "super", "switch", "synchronized", "this", "throw", "throws", "transient", 
            "try", "void", "volatile", "while",
            
            # Java 8+ 关键字
            "var", "yield", "record", "sealed", "non-sealed", "permits",
            
            # 保留字
            "true", "false", "null"
        ]
        
        # Java内置类和方法
        self._builtins = [
            # 基本类型包装类
            "Boolean", "Byte", "Character", "Short", "Integer", "Long", "Float", "Double",
            
            # 字符串相关
            "String", "StringBuilder", "StringBuffer", "StringTokenizer",
            
            # 集合框架
            "List", "ArrayList", "LinkedList", "Vector", "Stack", "Set", "HashSet", 
            "TreeSet", "LinkedHashSet", "Map", "HashMap", "TreeMap", "LinkedHashMap", 
            "Hashtable", "Properties", "Dictionary", "Queue", "Deque", "ArrayDeque", 
            "PriorityQueue", "Collection", "Collections", "Iterator", "ListIterator", 
            "Enumeration", "Comparator", "Comparable",
            
            # IO相关
            "File", "InputStream", "OutputStream", "Reader", "Writer", "FileInputStream", 
            "FileOutputStream", "FileReader", "FileWriter", "BufferedReader", "BufferedWriter", 
            "PrintStream", "PrintWriter", "DataInputStream", "DataOutputStream", 
            "ObjectInputStream", "ObjectOutputStream", "Serializable", "Externalizable",
            
            # 网络相关
            "URL", "URLConnection", "HttpURLConnection", "Socket", "ServerSocket", 
            "DatagramSocket", "DatagramPacket", "InetAddress", "URI",
            
            # 线程相关
            "Thread", "Runnable", "ThreadLocal", "Executor", "ExecutorService", 
            "ScheduledExecutorService", "ThreadPoolExecutor", "ForkJoinPool", "Future", 
            "Callable", "CompletableFuture", "Semaphore", "CountDownLatch", "CyclicBarrier", 
            "ReentrantLock", "Condition", "Lock", "ReadWriteLock", "AtomicInteger", 
            "AtomicLong", "AtomicBoolean", "AtomicReference",
            
            # 反射相关
            "Class", "Method", "Field", "Constructor", "Modifier", "Array", "Proxy",
            
            # 异常相关
            "Exception", "RuntimeException", "Error", "Throwable", "IOException", 
            "FileNotFoundException", "ClassNotFoundException", "NoSuchMethodException", 
            "IllegalAccessException", "InstantiationException", "NumberFormatException", 
            "NullPointerException", "ArrayIndexOutOfBoundsException", "StringIndexOutOfBoundsException", 
            "ArithmeticException", "ClassCastException", "IllegalArgumentException", 
            "IllegalStateException", "UnsupportedOperationException",
            
            # 时间日期相关
            "Date", "Time", "Timestamp", "Calendar", "GregorianCalendar", "SimpleDateFormat", 
            "LocalDate", "LocalTime", "LocalDateTime", "ZonedDateTime", "Instant", "Duration", 
            "Period", "DateTimeFormatter", "TimeZone", "Locale",
            
            # 数学相关
            "Math", "BigInteger", "BigDecimal", "Random", "SecureRandom", "RoundingMode",
            
            # 系统相关
            "System", "Runtime", "Process", "ProcessBuilder", "SecurityManager", 
            "ClassLoader", "Package", "Module", "ModuleLayer",
            
            # 注解相关
            "Annotation", "RetentionPolicy", "ElementType", "Target", "Retention", 
            "Documented", "Inherited", "Repeatable", "Deprecated", "Override", "SuppressWarnings",
            
            # 泛型相关
            "Type", "ParameterizedType", "TypeVariable", "GenericArrayType", "WildcardType",
            
            # JavaFX相关
            "Application", "Stage", "Scene", "Node", "Parent", "Group", "Pane", "HBox", 
            "VBox", "BorderPane", "GridPane", "FlowPane", "StackPane", "Button", "Label", 
            "TextField", "TextArea", "CheckBox", "RadioButton", "ToggleButton", "ComboBox", 
            "ListView", "TableView", "TreeView", "ImageView", "Canvas", "GraphicsContext", 
            "Color", "Font", "Image", "MediaPlayer", "Media",
            
            # Swing相关
            "JFrame", "JDialog", "JPanel", "JButton", "JLabel", "JTextField", "JTextArea", 
            "JCheckBox", "JRadioButton", "JComboBox", "JList", "JTable", "JTree", "JMenuBar", 
            "JMenu", "JMenuItem", "JOptionPane", "JScrollPane", "JSplitPane", "JTabbedPane", 
            "JToolBar", "JProgressBar", "JSlider", "JColorChooser", "JFileChooser",
            
            # 常用方法
            "println", "print", "printf", "format", "valueOf", "toString", "equals", 
            "hashCode", "compareTo", "clone", "finalize", "getClass", "notify", "notifyAll", 
            "wait", "add", "remove", "get", "set", "put", "contains", "isEmpty", "size", 
            "clear", "iterator", "toArray", "stream", "parallelStream", "filter", "map", 
            "reduce", "collect", "forEach", "sorted", "distinct", "limit", "skip", "count", 
            "anyMatch", "allMatch", "noneMatch", "findFirst", "findAny", "min", "max", "average", 
            "sum", "join", "split", "substring", "replace", "replaceAll", "matches", "startsWith", 
            "endsWith", "toLowerCase", "toUpperCase", "trim", "length", "charAt", "getBytes", 
            "toCharArray", "indexOf", "lastIndexOf", "substring", "concat", "format"
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
            
            # 类定义
            "class_def": r"\b(?:public|private|protected)?\s*(?:abstract|final|static)?\s*(?:class|interface|enum|record)\s+[a-zA-Z_][a-zA-Z0-9_]*",
            
            # 方法定义
            "method_def": r"\b(?:public|private|protected)?\s*(?:abstract|final|static|synchronized|native)?\s*(?:[a-zA-Z_][a-zA-Z0-9_]*\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*(?:throws\s+[a-zA-Z_][a-zA-Z0-9_]*(?:\s*,\s*[a-zA-Z_][a-zA-Z0-9_]*)*)?",
            
            # 方法调用
            "method_call": r"\b[a-zA-Z_][a-zA-Z0-9_]*\s*\(",
            
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
            
            # 操作符
            "operator": r"[+\-*/%=<>!&|^~?:]+",
            
            # 泛型
            "generic": r"<[a-zA-Z_][a-zA-Z0-9_]*(?:\s*,\s*[a-zA-Z_][a-zA-Z0-9_]*)*(?:\s+extends\s+[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)?>",
            
            # Lambda表达式
            "lambda": r"\([^)]*\)\s*->|[^,=<>]+\s*->",
            
            # 方法引用
            "method_ref": r"[a-zA-Z_][a-zA-Z0-9_]*::[a-zA-Z_][a-zA-Z0-9_]*",
        }
        
        # 标签样式 - 使用适合Java语言的配色方案
        self._tag_styles = {
            "comment": {"foreground": "#6A9955", "font": "italic"},  # 绿色斜体用于单行注释
            "multiline_comment": {"foreground": "#6A9955", "font": "italic"},  # 绿色斜体用于多行注释
            "javadoc_comment": {"foreground": "#6A9955", "font": "italic"},  # 绿色斜体用于JavaDoc注释
            "string": {"foreground": "#CE9178"},  # 橙色用于字符串
            "char": {"foreground": "#CE9178"},  # 橙色用于字符
            "number": {"foreground": "#B5CEA8"},  # 浅绿色用于数字
            "hex_number": {"foreground": "#B5CEA8"},  # 浅绿色用于十六进制数字
            "binary_number": {"foreground": "#B5CEA8"},  # 浅绿色用于二进制数字
            "octal_number": {"foreground": "#B5CEA8"},  # 浅绿色用于八进制数字
            "boolean": {"foreground": "#569CD6"},  # 蓝色用于布尔值
            "null": {"foreground": "#569CD6"},  # 蓝色用于null值
            "class_def": {"foreground": "#569CD6", "font": "bold"},  # 蓝色粗体用于类定义
            "method_def": {"foreground": "#DCDCAA", "font": "bold"},  # 浅黄色粗体用于方法定义
            "method_call": {"foreground": "#DCDCAA"},  # 浅黄色用于方法调用
            "property_access": {"foreground": "#9CDCFE"},  # 浅蓝色用于属性访问
            "variable_decl": {"foreground": "#C586C0"},  # 紫色用于变量声明
            "annotation": {"foreground": "#C586C0"},  # 紫色用于注解
            "package_decl": {"foreground": "#C586C0"},  # 紫色用于包声明
            "import_decl": {"foreground": "#C586C0"},  # 紫色用于导入声明
            "operator": {"foreground": "#D4D4D4"},  # 浅灰色用于操作符
            "generic": {"foreground": "#4EC9B0"},  # 青色用于泛型
            "lambda": {"foreground": "#FF7700"},  # 橙色用于Lambda表达式
            "method_ref": {"foreground": "#FF7700"},  # 橙色用于方法引用
        }