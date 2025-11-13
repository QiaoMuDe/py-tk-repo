#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Rust语言处理器

提供.rs文件的语法高亮支持
"""

import re
from typing import Dict, List, Any

from .base import LanguageHandler


class RustHandler(LanguageHandler):
    """
    Rust语言处理器

    提供.rs文件的语法高亮支持
    """

    # Rust文件扩展名
    file_extensions = [".rs"]

    def _setup_language(self):
        """
        设置Rust语言的语法高亮规则
        """
        # Rust关键字
        self._keywords = [
            # 主要关键字
            "as",
            "async",
            "await",
            "break",
            "const",
            "continue",
            "crate",
            "dyn",
            "else",
            "enum",
            "extern",
            "false",
            "fn",
            "for",
            "if",
            "impl",
            "in",
            "let",
            "loop",
            "match",
            "mod",
            "move",
            "mut",
            "pub",
            "ref",
            "return",
            "self",
            "Self",
            "static",
            "struct",
            "super",
            "trait",
            "true",
            "type",
            "union",
            "unsafe",
            "use",
            "where",
            "while",
            # 保留字
            "abstract",
            "become",
            "box",
            "do",
            "final",
            "macro",
            "override",
            "priv",
            "try",
            "typeof",
            "unsized",
            "virtual",
            "yield",
            # 特殊标识符
            "macro_rules",
            "union",
        ]

        # Rust内置类型和函数
        self._builtins = [
            # 基本类型
            "i8",
            "i16",
            "i32",
            "i64",
            "i128",
            "isize",
            "u8",
            "u16",
            "u32",
            "u64",
            "u128",
            "usize",
            "f32",
            "f64",
            "bool",
            "char",
            "str",
            # 常用集合类型
            "Vec",
            "HashMap",
            "HashSet",
            "BTreeMap",
            "BTreeSet",
            "LinkedList",
            "VecDeque",
            "BinaryHeap",
            "Option",
            "Result",
            "String",
            "Box",
            "Rc",
            "Arc",
            "Cell",
            "RefCell",
            # 常用trait
            "Copy",
            "Clone",
            "Debug",
            "Display",
            "Default",
            "Eq",
            "PartialEq",
            "Ord",
            "PartialOrd",
            "Hash",
            "Iterator",
            "IntoIterator",
            "From",
            "Into",
            "AsRef",
            "AsMut",
            "Borrow",
            "BorrowMut",
            "ToOwned",
            "Drop",
            "Deref",
            "DerefMut",
            "Index",
            "IndexMut",
            "Add",
            "Sub",
            "Mul",
            "Div",
            "Rem",
            "Neg",
            "Not",
            "BitAnd",
            "BitOr",
            "BitXor",
            "Shl",
            "Shr",
            "AddAssign",
            "SubAssign",
            "MulAssign",
            "DivAssign",
            "RemAssign",
            "BitAndAssign",
            "BitOrAssign",
            "BitXorAssign",
            "ShlAssign",
            "ShrAssign",
            "Fn",
            "FnMut",
            "FnOnce",
            # 常用模块
            "std",
            "core",
            "alloc",
            "proc_macro",
            "io",
            "fs",
            "path",
            "env",
            "process",
            "thread",
            "sync",
            "time",
            "net",
            "collections",
            "any",
            "cmp",
            "convert",
            "default",
            "error",
            "fmt",
            "hash",
            "iter",
            "marker",
            "mem",
            "ops",
            "option",
            "result",
            "ptr",
            "slice",
            "str",
            "string",
            "task",
            "vec",
            # 常用宏
            "println",
            "print",
            "eprintln",
            "eprint",
            "format",
            "panic",
            "assert",
            "assert_eq",
            "assert_ne",
            "debug_assert",
            "debug_assert_eq",
            "debug_assert_ne",
            "unreachable",
            "unimplemented",
            "todo",
            "vec",
            "format_args",
            "write",
            "writeln",
            "concat",
            "include",
            "include_str",
            "include_bytes",
            "env",
            "option_env",
            "cfg",
            "column",
            "file",
            "line",
            "module_path",
            "stringify",
            "compile_error",
            "global_asm",
            "trace_macros",
            "log",
            "info",
            "warn",
            "error",
            # 常用函数
            "Some",
            "None",
            "Ok",
            "Err",
            "main",
            "new",
            "len",
            "is_empty",
            "push",
            "pop",
            "insert",
            "remove",
            "clear",
            "contains",
            "get",
            "get_mut",
            "iter",
            "iter_mut",
            "into_iter",
            "collect",
            "map",
            "filter",
            "fold",
            "reduce",
            "for_each",
            "all",
            "any",
            "find",
            "position",
            "rposition",
            "max",
            "min",
            "max_by",
            "min_by",
            "max_by_key",
            "min_by_key",
            "sum",
            "product",
            "count",
            "last",
            "nth",
            "step_by",
            "chain",
            "zip",
            "enumerate",
            "rev",
            "cloned",
            "cycle",
            "take",
            "take_while",
            "skip",
            "skip_while",
            "fuse",
            "inspect",
            "by_ref",
            "peekable",
            "scan",
            "flat_map",
            "flatten",
            "filter_map",
            "unzip",
            "partition",
            "find_map",
            "try_fold",
            "try_for_each",
            "from_fn",
            "successors",
            "from_iter",
            "from",
            "into",
            "as_ref",
            "as_mut",
            "borrow",
            "borrow_mut",
            "to_owned",
            "clone",
            "clone_from",
            "drop",
            "deref",
            "deref_mut",
            "hash",
            "cmp",
            "partial_cmp",
            "eq",
            "ne",
            "lt",
            "le",
            "gt",
            "ge",
            "ord",
            "max",
            "min",
            "clamp",
            "type_name",
            "type_id",
            "size_of",
            "size_of_val",
            "align_of",
            "align_of_val",
            "min_align_of",
            "min_align_of_val",
            "layout_for",
            "layout",
            "transmute",
            "transmute_copy",
            "forget",
            "manually_drop",
            "maybe_uninit",
            "assume_init",
            "ptr::read",
            "ptr::write",
            "ptr::read_volatile",
            "ptr::write_volatile",
            "ptr::read_unaligned",
            "ptr::write_unaligned",
            "ptr::swap",
            "ptr::replace",
            "ptr::swap_nonoverlapping",
            "ptr::copy",
            "ptr::copy_nonoverlapping",
            "mem::replace",
            "mem::swap",
            "mem::discriminant",
            "mem::variant_count",
            "mem::needs_drop",
            "mem::drop_in_place",
            "mem::forget",
            "mem::ManuallyDrop",
            "mem::MaybeUninit",
            "mem::align_of",
            "mem::size_of",
            "mem::align_of_val",
            "mem::size_of_val",
            "mem::min_align_of",
            "mem::min_align_of_val",
            "mem::offset_of",
            "mem::variant_count",
            # 异步相关
            "Future",
            "Stream",
            "Sink",
            "Poll",
            "Ready",
            "Pending",
            "Pin",
            "Unpin",
            "Context",
            "Waker",
            "RawWaker",
            "RawWakerVTable",
            "task",
            "future",
            "pin",
            "unpin",
            "poll",
            "ready",
            "pending",
            "wake",
            "wake_by_ref",
            "clone_waker",
            # 并发相关
            "Mutex",
            "RwLock",
            "Condvar",
            "Barrier",
            "Once",
            "OnceCell",
            "LazyCell",
            "LazyLock",
            "AtomicBool",
            "AtomicI8",
            "AtomicI16",
            "AtomicI32",
            "AtomicI64",
            "AtomicIsize",
            "AtomicU8",
            "AtomicU16",
            "AtomicU32",
            "AtomicU64",
            "AtomicUsize",
            "AtomicPtr",
            "Ordering",
            "SeqCst",
            "Release",
            "Acquire",
            "AcqRel",
            "Relaxed",
            "thread",
            "spawn",
            "scope",
            "park",
            "unpark",
            "park_timeout",
            "current",
            "yield_now",
            "sleep",
            "sleep_ms",
            "join",
            "detach",
            "id",
            "name",
            "stack_size",
            # 错误处理
            "Error",
            "Result",
            "Option",
            "try",
            "catch_unwind",
            "resume_unwind",
            "panic",
            "panic_any",
            "set_hook",
            "take_hook",
            "Location",
            "PanicInfo",
            "PanicHook",
            # 序列化相关
            "Serialize",
            "Deserialize",
            "Serializer",
            "Deserializer",
            "Visitor",
            "de",
            "ser",
            "SerializeTuple",
            "SerializeTupleStruct",
            "SerializeTupleVariant",
            "SerializeMap",
            "SerializeStruct",
            "SerializeStructVariant",
            "DeserializeSeed",
            # 常用trait对象
            "Read",
            "Write",
            "BufRead",
            "Seek",
            "SeekFrom",
            "BufRead",
            "Iterator",
            "DoubleEndedIterator",
            "ExactSizeIterator",
            "FusedIterator",
            "TrustedLen",
            "Extend",
            "FromIterator",
            "IntoIterator",
            "Sum",
            "Product",
            # 常用结构体和枚举
            "Duration",
            "Instant",
            "SystemTime",
            "UNIX_EPOCH",
            "IpAddr",
            "Ipv4Addr",
            "Ipv6Addr",
            "SocketAddr",
            "SocketAddrV4",
            "SocketAddrV6",
            "TcpStream",
            "TcpListener",
            "UdpSocket",
            "AddrParseError",
            "Shutdown",
            "ErrorKind",
            "FileType",
            "Metadata",
            "Permissions",
            "OpenOptions",
            "DirBuilder",
            "DirEntry",
            "ReadDir",
            "Path",
            "PathBuf",
            "Components",
            "Iter",
            "Ancestors",
            "Prefix",
            "PrefixComponent",
            "Component",
            "StripPrefixError",
            "Args",
            "OsString",
            "OsStr",
            "Command",
            "ExitStatus",
            "Output",
            "Stdio",
            "Child",
            "ChildStdin",
            "ChildStdout",
            "ChildStderr",
            "JoinHandle",
            "ThreadId",
            "ThreadId",
            "LocalKey",
            "ThreadId",
            "ThreadId",
            "ThreadId",
            "ThreadId",
            "ThreadId",
            "ThreadId",
            "ThreadId",
            "ThreadId",
            "ThreadId",
            "ThreadId",
            "ThreadId",
            "ThreadId",
        ]

        # 正则表达式模式
        self._regex_patterns = {
            # 单行注释
            "comment": r"//.*$",
            # 多行注释
            "multiline_comment": r"/\*.*?\*/",
            # 文档注释
            "doc_comment": r"///.*$|/\*\*.*?\*/",
            # 字符串
            "string": r'"(?:[^"\\]|\\.)*"',
            # 原始字符串
            "raw_string": r'r#*"[^"]*"#*',
            # 字符
            "char": r"'(?:[^'\\]|\\.)'",
            # 字节字符串
            "byte_string": r'b"(?:[^"\\]|\\.)*"',
            # 原始字节字符串
            "raw_byte_string": r'br#*"[^"]*"#*',
            # 字节
            "byte": r"b'(?:[^'\\]|\\.)'",
            # 数字
            "number": r"\b\d+\.?\d*([eE][+-]?\d+)?[fF]?\b",
            # 二进制数字
            "binary_number": r"0b[01_]+",
            # 八进制数字
            "octal_number": r"0o[0-7_]+",
            # 十六进制数字
            "hex_number": r"0x[0-9a-fA-F_]+",
            # 布尔值
            "boolean": r"\b(true|false)\b",
            # 生命周期
            "lifetime": r"'[a-zA-Z_][a-zA-Z0-9_]*",
            # 属性
            "attribute": r"#\[.*?\]",
            # 宏调用
            "macro_call": r"[a-zA-Z_][a-zA-Z0-9_]*!\s*",
            # 模式匹配
            "pattern_match": r"\bmatch\b.*?\{",
            # 结构体定义
            "struct_def": r"\b(?:pub\s+)?struct\s+[a-zA-Z_][a-zA-Z0-9_]*",
            # 枚举定义
            "enum_def": r"\b(?:pub\s+)?enum\s+[a-zA-Z_][a-zA-Z0-9_]*",
            # 联合体定义
            "union_def": r"\b(?:pub\s+)?union\s+[a-zA-Z_][a-zA-Z0-9_]*",
            # 特质定义
            "trait_def": r"\b(?:pub\s+)?trait\s+[a-zA-Z_][a-zA-Z0-9_]*",
            # 函数定义
            "fn_def": r"\b(?:pub\s+)?(?:async\s+)?(?:unsafe\s+)?(?:extern\s+)?fn\s+[a-zA-Z_][a-zA-Z0-9_]*",
            # 方法调用
            "method_call": r"[a-zA-Z_][a-zA-Z0-9_]*\s*\(",
            # 字段访问
            "field_access": r"[a-zA-Z_][a-zA-Z0-9_]*\s*\.\s*[a-zA-Z_][a-zA-Z0-9_]*",
            # 模块导入
            "mod_use": r"\b(?:use|mod)\s+[a-zA-Z_][a-zA-Z0-9_]*(?:\s*::\s*[a-zA-Z_][a-zA-Z0-9_]*)*",
            # 变量绑定
            "let_binding": r"\blet\s+(?:mut\s+)?[a-zA-Z_][a-zA-Z0-9_]*",
            # 类型注解
            "type_annotation": r":\s*[a-zA-Z_][a-zA-Z0-9_]*(?:\s*<[^>]*>)?",
            # 泛型
            "generic": r"<[a-zA-Z_][a-zA-Z0-9_]*(?:\s*,\s*[a-zA-Z_][a-zA-Z0-9_]*)*(?:\s*:\s*[a-zA-Z_][a-zA-Z0-9_]*(?:\s*<[^>]*>)?)?>",
            # 闭包
            "closure": r"\|[^\|]*\|",
            # 异步块
            "async_block": r"async\s+move?\s*\{",
            # 不安全块
            "unsafe_block": r"unsafe\s*\{",
            # 循环
            "loop_block": r"(?:loop|for|while)\s*\{",
            # 条件语句
            "if_block": r"if\s+.*?\{",
            # 操作符
            "operator": r"[+\-*/%=<>!&|^~?:]+",
            # 模式匹配操作符
            "match_operator": r"=>",
            # 范围操作符
            "range_operator": r"\.\.",
            # 引用操作符
            "ref_operator": r"&[a-zA-Z_][a-zA-Z0-9_]*",
            # 解引用操作符
            "deref_operator": r"\*[a-zA-Z_][a-zA-Z0-9_]*",
        }

        # 标签样式 - 使用适合Rust语言的配色方案
        self._tag_styles = {
            "comment": {
                "foreground": "#6A9955",
                "font": "italic",
            },  # 绿色斜体用于单行注释
            "multiline_comment": {
                "foreground": "#6A9955",
                "font": "italic",
            },  # 绿色斜体用于多行注释
            "doc_comment": {
                "foreground": "#608B4E",
                "font": "italic",
            },  # 深绿色斜体用于文档注释
            "string": {"foreground": "#CE9178"},  # 橙色用于字符串
            "raw_string": {"foreground": "#CE9178"},  # 橙色用于原始字符串
            "char": {"foreground": "#CE9178"},  # 橙色用于字符
            "byte_string": {"foreground": "#CE9178"},  # 橙色用于字节字符串
            "raw_byte_string": {"foreground": "#CE9178"},  # 橙色用于原始字节字符串
            "byte": {"foreground": "#CE9178"},  # 橙色用于字节
            "number": {"foreground": "#B5CEA8"},  # 浅绿色用于数字
            "binary_number": {"foreground": "#B5CEA8"},  # 浅绿色用于二进制数字
            "octal_number": {"foreground": "#B5CEA8"},  # 浅绿色用于八进制数字
            "hex_number": {"foreground": "#B5CEA8"},  # 浅绿色用于十六进制数字
            "boolean": {"foreground": "#569CD6"},  # 蓝色用于布尔值
            "lifetime": {"foreground": "#C586C0"},  # 紫色用于生命周期
            "attribute": {"foreground": "#C586C0"},  # 紫色用于属性
            "macro_call": {"foreground": "#DCDCAA"},  # 浅黄色用于宏调用
            "pattern_match": {
                "foreground": "#DCDCAA",
                "font": "bold",
            },  # 浅黄色粗体用于模式匹配
            "struct_def": {
                "foreground": "#569CD6",
                "font": "bold",
            },  # 蓝色粗体用于结构体定义
            "enum_def": {
                "foreground": "#569CD6",
                "font": "bold",
            },  # 蓝色粗体用于枚举定义
            "union_def": {
                "foreground": "#569CD6",
                "font": "bold",
            },  # 蓝色粗体用于联合体定义
            "trait_def": {
                "foreground": "#569CD6",
                "font": "bold",
            },  # 蓝色粗体用于特质定义
            "fn_def": {
                "foreground": "#DCDCAA",
                "font": "bold",
            },  # 浅黄色粗体用于函数定义
            "method_call": {"foreground": "#DCDCAA"},  # 浅黄色用于方法调用
            "field_access": {"foreground": "#9CDCFE"},  # 浅蓝色用于字段访问
            "mod_use": {"foreground": "#C586C0"},  # 紫色用于模块导入
            "let_binding": {"foreground": "#C586C0"},  # 紫色用于变量绑定
            "type_annotation": {"foreground": "#4EC9B0"},  # 青色用于类型注解
            "generic": {"foreground": "#4EC9B0"},  # 青色用于泛型
            "closure": {"foreground": "#FF7700"},  # 橙色用于闭包
            "async_block": {
                "foreground": "#FF7700",
                "font": "bold",
            },  # 橙色粗体用于异步块
            "unsafe_block": {
                "foreground": "#FF7700",
                "font": "bold",
            },  # 橙色粗体用于不安全块
            "loop_block": {"foreground": "#FF7700", "font": "bold"},  # 橙色粗体用于循环
            "if_block": {
                "foreground": "#FF7700",
                "font": "bold",
            },  # 橙色粗体用于条件语句
            "operator": {"foreground": "#D4D4D4"},  # 浅灰色用于操作符
            "match_operator": {
                "foreground": "#D4D4D4",
                "font": "bold",
            },  # 浅灰色粗体用于模式匹配操作符
            "range_operator": {
                "foreground": "#D4D4D4",
                "font": "bold",
            },  # 浅灰色粗体用于范围操作符
            "ref_operator": {"foreground": "#D4D4D4"},  # 浅灰色用于引用操作符
            "deref_operator": {"foreground": "#D4D4D4"},  # 浅灰色用于解引用操作符
        }
