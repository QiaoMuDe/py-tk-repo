#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
C/C++语言处理器

提供.c, .cpp, .cc, .cxx, .c++, .h, .hpp, .hh, .hxx, .inl, .tpp等文件的语法高亮支持
"""

import re
from typing import Dict, List, Any

from .base import LanguageHandler


class CppHandler(LanguageHandler):
    """
    C/C++语言处理器

    提供C/C++文件的语法高亮支持
    """

    # C/C++文件扩展名
    file_extensions = [
        ".c",
        ".cpp",
        ".cc",
        ".cxx",
        ".c++",
        ".h",
        ".hpp",
        ".hh",
        ".hxx",
        ".inl",
        ".tpp",
    ]

    def _setup_language(self):
        """
        设置C/C++语言的语法高亮规则
        """
        # C/C++关键字
        self._keywords = [
            # C关键字
            "auto",
            "break",
            "case",
            "char",
            "const",
            "continue",
            "default",
            "do",
            "double",
            "else",
            "enum",
            "extern",
            "float",
            "for",
            "goto",
            "if",
            "int",
            "long",
            "register",
            "return",
            "short",
            "signed",
            "sizeof",
            "static",
            "struct",
            "switch",
            "typedef",
            "union",
            "unsigned",
            "void",
            "volatile",
            "while",
            # C++关键字
            "alignas",
            "alignof",
            "and",
            "and_eq",
            "asm",
            "atomic_cancel",
            "atomic_commit",
            "atomic_noexcept",
            "bitand",
            "bitor",
            "bool",
            "catch",
            "char16_t",
            "char32_t",
            "char8_t",
            "class",
            "compl",
            "concept",
            "const_cast",
            "constexpr",
            "consteval",
            "constinit",
            "decltype",
            "delete",
            "dynamic_cast",
            "explicit",
            "export",
            "false",
            "friend",
            "inline",
            "mutable",
            "namespace",
            "new",
            "noexcept",
            "not",
            "not_eq",
            "nullptr",
            "operator",
            "or",
            "or_eq",
            "private",
            "protected",
            "public",
            "reinterpret_cast",
            "requires",
            "static_assert",
            "static_cast",
            "synchronized",
            "template",
            "this",
            "thread_local",
            "throw",
            "true",
            "try",
            "typeid",
            "typename",
            "using",
            "virtual",
            "wchar_t",
            "xor",
            "xor_eq",
            # C++20关键字
            "co_await",
            "co_return",
            "co_yield",
            "module",
            "import",
            # C++23关键字
            "consteval",
            "constinit",
            # 存储类说明符
            "auto",
            "extern",
            "register",
            "static",
            "thread_local",
            "mutable",
            # 类型限定符
            "const",
            "volatile",
            "constexpr",
            "consteval",
            "constinit",
            # 函数说明符
            "inline",
            "virtual",
            "explicit",
            # 访问说明符
            "public",
            "private",
            "protected",
            # 其他说明符
            "friend",
            "typedef",
            # 特殊值
            "true",
            "false",
            "nullptr",
            # C标准库类型
            "size_t",
            "ptrdiff_t",
            "wchar_t",
            "time_t",
            "clock_t",
            "FILE",
            "fpos_t",
            "div_t",
            "ldiv_t",
            "lldiv_t",
            "imaxdiv_t",
            "sig_atomic_t",
            # C++标准库类型
            "string",
            "wstring",
            "u16string",
            "u32string",
            "string_view",
            "wstring_view",
            "u16string_view",
            "u32string_view",
            "array",
            "vector",
            "deque",
            "list",
            "forward_list",
            "set",
            "multiset",
            "map",
            "multimap",
            "unordered_set",
            "unordered_multiset",
            "unordered_map",
            "unordered_multimap",
            "stack",
            "queue",
            "priority_queue",
            "pair",
            "tuple",
            "optional",
            "variant",
            "any",
            "bitset",
            "complex",
            "valarray",
            "slice",
            "gslice",
            "mask_array",
            "indirect_array",
            # 智能指针
            "unique_ptr",
            "shared_ptr",
            "weak_ptr",
            "auto_ptr",
            "inplace_ptr",
            # 迭代器类型
            "iterator",
            "const_iterator",
            "reverse_iterator",
            "const_reverse_iterator",
            "input_iterator_tag",
            "output_iterator_tag",
            "forward_iterator_tag",
            "bidirectional_iterator_tag",
            "random_access_iterator_tag",
            "contiguous_iterator_tag",
            # 函数对象
            "function",
            "mem_fn",
            "bind",
            "reference_wrapper",
            " cref",
            "ref",
            # 类型特征
            "is_void",
            "is_null_pointer",
            "is_integral",
            "is_floating_point",
            "is_array",
            "is_pointer",
            "is_lvalue_reference",
            "is_rvalue_reference",
            "is_member_object_pointer",
            "is_member_function_pointer",
            "is_enum",
            "is_union",
            "is_class",
            "is_function",
            "is_fundamental",
            "is_arithmetic",
            "is_scalar",
            "is_object",
            "is_compound",
            "is_reference",
            "is_member_pointer",
            "is_const",
            "is_volatile",
            "is_trivial",
            "is_trivially_copyable",
            "is_standard_layout",
            "is_pod",
            "is_literal_type",
            "is_empty",
            "is_polymorphic",
            "is_abstract",
            "is_final",
            "is_aggregate",
            "is_signed",
            "is_unsigned",
            "is_constructible",
            "is_default_constructible",
            "is_copy_constructible",
            "is_move_constructible",
            "is_copy_assignable",
            "is_move_assignable",
            "is_destructible",
            "is_trivially_constructible",
            "is_trivially_default_constructible",
            "is_trivially_copy_constructible",
            "is_trivially_move_constructible",
            "is_trivially_copy_assignable",
            "is_trivially_move_assignable",
            "is_trivially_destructible",
            "is_nothrow_constructible",
            "is_nothrow_default_constructible",
            "is_nothrow_copy_constructible",
            "is_nothrow_move_constructible",
            "is_nothrow_copy_assignable",
            "is_nothrow_move_assignable",
            "is_nothrow_destructible",
            "has_virtual_destructor",
            "is_swappable",
            "is_nothrow_swappable",
            # 其他C++类型
            "istream",
            "ostream",
            "iostream",
            "ifstream",
            "ofstream",
            "fstream",
            "istringstream",
            "ostringstream",
            "stringstream",
            "wistream",
            "wostream",
            "wiostream",
            "wifstream",
            "wofstream",
            "wfstream",
            "wistringstream",
            "wostringstream",
            "wstringstream",
            "cin",
            "cout",
            "cerr",
            "clog",
            "wcin",
            "wcout",
            "wcerr",
            "wclog",
            "ios_base",
            "ios",
            "wios",
            "streambuf",
            "wstreambuf",
            "filebuf",
            "wfilebuf",
            "stringbuf",
            "wstringbuf",
            # 异常类型
            "exception",
            "bad_exception",
            "logic_error",
            "runtime_error",
            "bad_alloc",
            "bad_array_new_length",
            "bad_cast",
            "bad_typeid",
            "bad_function_call",
            "bad_weak_ptr",
            "bad_variant_access",
            "ios_base::failure",
            # 数值限制
            "numeric_limits",
            # C++20概念
            "same_as",
            "derived_from",
            "convertible_to",
            "common_reference_with",
            "common_with",
            "integral",
            "signed_integral",
            "unsigned_integral",
            "floating_point",
            "assignable_from",
            "swappable",
            "movable",
            "copyable",
            "semiregular",
            "regular",
            "invocable",
            "predicate",
            "relation",
            "equivalence_relation",
            "strict_weak_order",
            "totally_ordered",
            # C++20范围
            "ranges::range",
            "ranges::borrowed_range",
            "ranges::sized_range",
            "ranges::view",
            "ranges::input_range",
            "ranges::output_range",
            "ranges::forward_range",
            "ranges::bidirectional_range",
            "ranges::random_access_range",
            "ranges::contiguous_range",
            "ranges::common_range",
            "ranges::viewable_range",
        ]

        # C/C++内置函数和库
        self._builtins = [
            # C标准库函数
            # 输入/输出
            "printf",
            "fprintf",
            "sprintf",
            "snprintf",
            "scanf",
            "fscanf",
            "sscanf",
            "fopen",
            "fclose",
            "freopen",
            "fflush",
            "setbuf",
            "setvbuf",
            "fread",
            "fwrite",
            "fseek",
            "ftell",
            "rewind",
            "fgetpos",
            "fsetpos",
            "clearerr",
            "feof",
            "ferror",
            "perror",
            "getc",
            "getchar",
            "gets",
            "putc",
            "putchar",
            "puts",
            "ungetc",
            "fgets",
            "fputs",
            "remove",
            "rename",
            "tmpfile",
            "tmpnam",
            # 内存操作
            "malloc",
            "calloc",
            "realloc",
            "free",
            "memcpy",
            "memmove",
            "memcmp",
            "memchr",
            "memset",
            # 字符串操作
            "strcpy",
            "strncpy",
            "strcat",
            "strncat",
            "strcmp",
            "strncmp",
            "strcoll",
            "strchr",
            "strrchr",
            "strspn",
            "strcspn",
            "strpbrk",
            "strstr",
            "strlen",
            "strerror",
            "strtok",
            "strxfrm",
            # 数学函数
            "abs",
            "labs",
            "llabs",
            "div",
            "ldiv",
            "lldiv",
            "fabs",
            "ceil",
            "floor",
            "fmod",
            "remainder",
            "remquo",
            "fma",
            "fmax",
            "fmin",
            "fdim",
            "exp",
            "exp2",
            "expm1",
            "log",
            "log2",
            "log10",
            "log1p",
            "pow",
            "sqrt",
            "cbrt",
            "hypot",
            "sin",
            "cos",
            "tan",
            "asin",
            "acos",
            "atan",
            "atan2",
            "sinh",
            "cosh",
            "tanh",
            "asinh",
            "acosh",
            "atanh",
            "erf",
            "erfc",
            "tgamma",
            "lgamma",
            "round",
            "lround",
            "llround",
            "trunc",
            "lrint",
            "llrint",
            "nearbyint",
            "rint",
            "frexp",
            "ldexp",
            "modf",
            "scalbn",
            "scalbln",
            "ilogb",
            "logb",
            "nextafter",
            "nexttoward",
            "copysign",
            "isnan",
            "isinf",
            "isnormal",
            "signbit",
            # 时间函数
            "clock",
            "time",
            "difftime",
            "mktime",
            "asctime",
            "ctime",
            "gmtime",
            "localtime",
            "strftime",
            # 控制流
            "abort",
            "exit",
            "atexit",
            "quick_exit",
            "_Exit",
            "at_quick_exit",
            "getenv",
            "system",
            "assert",
            # 类型转换
            "atoi",
            "atol",
            "atoll",
            "atof",
            "strtol",
            "strtoll",
            "strtoul",
            "strtoull",
            "strtof",
            "strtod",
            "strtold",
            "rand",
            "srand",
            # 多字节字符
            "mblen",
            "mbtowc",
            "wctomb",
            "mbstowcs",
            "wcstombs",
            # C++标准库函数
            # 算法
            "for_each",
            "find",
            "find_if",
            "find_if_not",
            "find_end",
            "find_first_of",
            "adjacent_find",
            "count",
            "count_if",
            "mismatch",
            "equal",
            "is_permutation",
            "search",
            "search_n",
            "copy",
            "copy_n",
            "copy_if",
            "copy_backward",
            "move",
            "move_backward",
            "fill",
            "fill_n",
            "transform",
            "generate",
            "generate_n",
            "remove",
            "remove_if",
            "remove_copy",
            "remove_copy_if",
            "unique",
            "unique_copy",
            "reverse",
            "reverse_copy",
            "rotate",
            "rotate_copy",
            "random_shuffle",
            "shuffle",
            "is_partitioned",
            "partition",
            "stable_partition",
            "partition_copy",
            "partition_point",
            "sort",
            "stable_sort",
            "partial_sort",
            "partial_sort_copy",
            "is_sorted",
            "is_sorted_until",
            "nth_element",
            "lower_bound",
            "upper_bound",
            "binary_search",
            "equal_range",
            "merge",
            "inplace_merge",
            "includes",
            "set_union",
            "set_intersection",
            "set_difference",
            "set_symmetric_difference",
            "push_heap",
            "pop_heap",
            "make_heap",
            "sort_heap",
            "is_heap",
            "is_heap_until",
            "min",
            "max",
            "minmax",
            "min_element",
            "max_element",
            "minmax_element",
            "lexicographical_compare",
            "is_permutation",
            "next_permutation",
            "prev_permutation",
            "accumulate",
            "inner_product",
            "adjacent_difference",
            "partial_sum",
            "iota",
            "reduce",
            "transform_reduce",
            "exclusive_scan",
            "inclusive_scan",
            "transform_exclusive_scan",
            "transform_inclusive_scan",
            # C++20范围算法
            "ranges::for_each",
            "ranges::find",
            "ranges::find_if",
            "ranges::find_if_not",
            "ranges::find_end",
            "ranges::find_first_of",
            "ranges::adjacent_find",
            "ranges::count",
            "ranges::count_if",
            "ranges::mismatch",
            "ranges::equal",
            "ranges::is_permutation",
            "ranges::search",
            "ranges::search_n",
            "ranges::copy",
            "ranges::copy_n",
            "ranges::copy_if",
            "ranges::copy_backward",
            "ranges::move",
            "ranges::move_backward",
            "ranges::fill",
            "ranges::fill_n",
            "ranges::transform",
            "ranges::generate",
            "ranges::generate_n",
            "ranges::remove",
            "ranges::remove_if",
            "ranges::remove_copy",
            "ranges::remove_copy_if",
            "ranges::unique",
            "ranges::unique_copy",
            "ranges::reverse",
            "ranges::reverse_copy",
            "ranges::rotate",
            "ranges::rotate_copy",
            "ranges::shuffle",
            "ranges::is_partitioned",
            "ranges::partition",
            "ranges::stable_partition",
            "ranges::partition_copy",
            "ranges::partition_point",
            "ranges::sort",
            "ranges::stable_sort",
            "ranges::partial_sort",
            "ranges::partial_sort_copy",
            "ranges::is_sorted",
            "ranges::is_sorted_until",
            "ranges::nth_element",
            "ranges::lower_bound",
            "ranges::upper_bound",
            "ranges::binary_search",
            "ranges::equal_range",
            "ranges::merge",
            "ranges::inplace_merge",
            "ranges::includes",
            "ranges::set_union",
            "ranges::set_intersection",
            "ranges::set_difference",
            "ranges::set_symmetric_difference",
            "ranges::push_heap",
            "ranges::pop_heap",
            "ranges::make_heap",
            "ranges::sort_heap",
            "ranges::is_heap",
            "ranges::is_heap_until",
            "ranges::min",
            "ranges::max",
            "ranges::minmax",
            "ranges::min_element",
            "ranges::max_element",
            "ranges::minmax_element",
            "ranges::lexicographical_compare",
            "ranges::next_permutation",
            "ranges::prev_permutation",
            "ranges::accumulate",
            "ranges::inner_product",
            "ranges::adjacent_difference",
            "ranges::partial_sum",
            "ranges::iota",
            "ranges::reduce",
            "ranges::transform_reduce",
            "ranges::exclusive_scan",
            "ranges::inclusive_scan",
            "ranges::transform_exclusive_scan",
            "ranges::transform_inclusive_scan",
            # 内存管理
            "new",
            "delete",
            "new[]",
            "delete[]",
            "operator new",
            "operator delete",
            "operator new[]",
            "operator delete[]",
            "get_new_handler",
            "set_new_handler",
            "make_unique",
            "make_shared",
            "allocate_shared",
            "make_shared_for_overwrite",
            "make_unique_for_overwrite",
            # 类型转换
            "static_cast",
            "dynamic_cast",
            "const_cast",
            "reinterpret_cast",
            # 异常处理
            "try",
            "catch",
            "throw",
            "noexcept",
            "terminate",
            "unexpected",
            "get_terminate",
            "set_terminate",
            "get_unexpected",
            "set_unexpected",
            "current_exception",
            "rethrow_exception",
            "make_exception_ptr",
            "rethrow_exception",
            "throw_with_nested",
            "rethrow_if_nested",
            # RTTI
            "typeid",
            "dynamic_cast",
            # 并发
            "thread",
            "join",
            "detach",
            "joinable",
            "get_id",
            "hardware_concurrency",
            "native_handle",
            "swap",
            "this_thread::get_id",
            "this_thread::yield",
            "this_thread::sleep_for",
            "this_thread::sleep_until",
            "mutex",
            "lock_guard",
            "unique_lock",
            "scoped_lock",
            "shared_lock",
            "defer_lock_t",
            "try_to_lock_t",
            "adopt_lock_t",
            "defer_lock",
            "try_to_lock",
            "adopt_lock",
            "try_lock",
            "unlock",
            "lock",
            "try_lock",
            "call_once",
            "once_flag",
            "condition_variable",
            "condition_variable_any",
            "notify_one",
            "notify_all",
            "wait",
            "wait_for",
            "wait_until",
            "future",
            "promise",
            "shared_future",
            "packaged_task",
            "async",
            "launch",
            "future_status",
            "future_errc",
            "future_error",
            "get",
            "wait",
            "wait_for",
            "wait_until",
            "set_value",
            "set_exception",
            "set_value_at_thread_exit",
            "set_exception_at_thread_exit",
            "make_ready_at_thread_exit",
            "shared_future",
            "atomic",
            "atomic_is_lock_free",
            "atomic_load",
            "atomic_load_explicit",
            "atomic_store",
            "atomic_store_explicit",
            "atomic_exchange",
            "atomic_exchange_explicit",
            "atomic_compare_exchange_weak",
            "atomic_compare_exchange_weak_explicit",
            "atomic_compare_exchange_strong",
            "atomic_compare_exchange_strong_explicit",
            "atomic_fetch_add",
            "atomic_fetch_add_explicit",
            "atomic_fetch_sub",
            "atomic_fetch_sub_explicit",
            "atomic_fetch_and",
            "atomic_fetch_and_explicit",
            "atomic_fetch_or",
            "atomic_fetch_or_explicit",
            "atomic_fetch_xor",
            "atomic_fetch_xor_explicit",
            "atomic_flag",
            "atomic_flag_test_and_set",
            "atomic_flag_test_and_set_explicit",
            "atomic_flag_clear",
            "atomic_flag_clear_explicit",
            "atomic_thread_fence",
            "atomic_signal_fence",
            "kill_dependency",
            # 文件系统
            "path",
            "filesystem::absolute",
            "filesystem::canonical",
            "filesystem::copy",
            "filesystem::copy_file",
            "filesystem::copy_symlink",
            "filesystem::create_directory",
            "filesystem::create_directories",
            "filesystem::create_hard_link",
            "filesystem::create_symlink",
            "filesystem::current_path",
            "filesystem::exists",
            "filesystem::equivalent",
            "filesystem::file_size",
            "filesystem::hard_link_count",
            "filesystem::is_block_file",
            "filesystem::is_character_file",
            "filesystem::is_directory",
            "filesystem::is_empty",
            "filesystem::is_fifo",
            "filesystem::is_other",
            "filesystem::is_regular_file",
            "filesystem::is_socket",
            "filesystem::is_symlink",
            "filesystem::last_write_time",
            "filesystem::permissions",
            "filesystem::read_symlink",
            "filesystem::relative",
            "filesystem::remove",
            "filesystem::remove_all",
            "filesystem::rename",
            "filesystem::resize_file",
            "filesystem::space",
            "filesystem::status",
            "filesystem::status_known",
            "filesystem::symlink_status",
            "filesystem::temp_directory_path",
            "filesystem::weakly_canonical",
            "file_status",
            "directory_entry",
            "directory_iterator",
            "recursive_directory_iterator",
            "file_type",
            "perms",
            "perm_options",
            "copy_options",
            "directory_options",
            # 正则表达式
            "basic_regex",
            "match_results",
            "sub_match",
            "regex_match",
            "regex_search",
            "regex_replace",
            "regex_iterator",
            "regex_token_iterator",
            "syntax_option_type",
            "match_flag_type",
            "error_type",
            "regex_error",
            "regex_constants",
            # 随机数
            "rand",
            "srand",
            "random_device",
            "mt19937",
            "mt19937_64",
            "minstd_rand0",
            "minstd_rand",
            "ranlux24_base",
            "ranlux48_base",
            "ranlux24",
            "ranlux48",
            "knuth_b",
            "default_random_engine",
            "seed_seq",
            "generate_canonical",
            "uniform_int_distribution",
            "uniform_real_distribution",
            "bernoulli_distribution",
            "binomial_distribution",
            "geometric_distribution",
            "negative_binomial_distribution",
            "poisson_distribution",
            "exponential_distribution",
            "gamma_distribution",
            "weibull_distribution",
            "extreme_value_distribution",
            "normal_distribution",
            "lognormal_distribution",
            "chi_squared_distribution",
            "cauchy_distribution",
            "fisher_f_distribution",
            "student_t_distribution",
            "discrete_distribution",
            "piecewise_constant_distribution",
            "piecewise_linear_distribution",
            # C++20格式化
            "format",
            "format_to",
            "format_to_n",
            "formatted_size",
            "make_format_args",
            "make_wformat_args",
            "format_args",
            "wformat_args",
            "format_string",
            "wformat_string",
            "runtime_format_string",
            "runtime_wformat_string",
            "basic_format_string",
            "wformat_string",
            "format_parse_context",
            "wformat_parse_context",
            "format_context",
            "wformat_context",
            "format_args_t",
            "wformat_args_t",
            "format_to_n_result",
            "format_error",
            # C++20协程
            "coroutine_handle",
            "coroutine_traits",
            "suspend_always",
            "suspend_never",
            "noop_coroutine",
            "noop_coroutine_handle",
            "coroutine_handle<>",
            "coroutine_handle<promise_type>",
            # C++20模块
            "import",
            "export",
            "module",
            "global module",
            "module partition",
            # C++20概念
            "requires",
            "concept",
            # C++20空间
            "std::ranges",
            "std::views",
            "std::span",
            "std::jthread",
            # C++23特性
            "std::expected",
            "std::mdspan",
            "std::flat_map",
            "std::flat_set",
            "std::print",
            "std::println",
            "std::format_to",
            "std::format_to_n",
            "std::formatted_size",
            "std::format_error",
            "std::format_args",
            "std::make_format_args",
            "std::format_context",
            "std::basic_format_string",
            "std::format_string",
            "std::runtime_format_string",
            "std::format_parse_context",
            # C++23特性
            "std::expected",
            "std::mdspan",
            "std::flat_map",
            "std::flat_set",
            "std::print",
            "std::println",
            "std::format_to",
            "std::format_to_n",
            "std::formatted_size",
            "std::format_error",
            "std::format_args",
            "std::make_format_args",
            "std::format_context",
            "std::basic_format_string",
            "std::format_string",
            "std::runtime_format_string",
            "std::format_parse_context",
            # C++23特性
            "std::expected",
            "std::mdspan",
            "std::flat_map",
            "std::flat_set",
            "std::print",
            "std::println",
            "std::format_to",
            "std::format_to_n",
            "std::formatted_size",
            "std::format_error",
            "std::format_args",
            "std::make_format_args",
            "std::format_context",
            "std::basic_format_string",
            "std::format_string",
            "std::runtime_format_string",
            "std::format_parse_context",
        ]

        # 正则表达式模式
        self._regex_patterns = {
            # 预处理指令
            "preprocessor": r"^\s*#\s*[a-zA-Z_][a-zA-Z0-9_]*",
            # 单行注释
            "comment": r"//.*$",
            # 多行注释
            "multiline_comment": r"/\*.*?\*/",
            # 字符串
            "string": r"(?:u8|u|U|L)?\"(?:[^\"\\]|\\.)*\"",
            # 原始字符串
            "raw_string": r"(?:u8|u|U|L)?R\"(?:[^\(\)]*)\((?:[^)]*)\)\"",
            # 字符
            "char": r"(?:u8|u|U|L)?'(?:[^'\\]|\\.)*'",
            # 数字
            "number": r"\b(?:[0-9]+\.?[0-9]*|[0-9]*\.[0-9]+)(?:[eE][+-]?[0-9]+)?[fFlL]?\b",
            # 十六进制数字
            "hex_number": r"\b0[xX][0-9a-fA-F]+(?:[uUlL]{1,3})?\b",
            # 八进制数字
            "octal_number": r"\b0[0-7]+(?:[uUlL]{1,3})?\b",
            # 二进制数字
            "binary_number": r"\b0[bB][01]+(?:[uUlL]{1,3})?\b",
            # 布尔值
            "boolean": r"\b(?:true|false)\b",
            # nullptr
            "nullptr": r"\bnullptr\b",
            # 标识符
            "identifier": r"[a-zA-Z_][a-zA-Z0-9_]*",
            # 类定义
            "class_def": r"\b(?:class|struct|union)\s+[a-zA-Z_][a-zA-Z0-9_]*",
            # 枚举定义
            "enum_def": r"\benum\s+(?:class\s+)?[a-zA-Z_][a-zA-Z0-9_]*",
            # 命名空间定义
            "namespace_def": r"\bnamespace\s+[a-zA-Z_][a-zA-Z0-9_]*",
            # 函数定义
            "function_def": r"[a-zA-Z_][a-zA-Z0-9_:&*<>]*\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)\s*(?:const)?\s*(?:override|final)?\s*(?:noexcept)?\s*\{?",
            # 模板定义
            "template_def": r"\btemplate\s*<[^>]*>",
            # 成员函数定义
            "method_def": r"[a-zA-Z_][a-zA-Z0-9_:&*<>]*\s+[a-zA-Z_][a-zA-Z0-9_]*::[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)\s*(?:const)?\s*(?:override|final)?\s*(?:noexcept)?\s*\{?",
            # 构造函数
            "constructor_def": r"[a-zA-Z_][a-zA-Z0-9_]*::[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)\s*(?:noexcept)?\s*\{?",
            # 析构函数
            "destructor_def": r"[a-zA-Z_][a-zA-Z0-9_]*::~[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)\s*(?:noexcept)?\s*\{?",
            # 函数调用
            "function_call": r"[a-zA-Z_][a-zA-Z0-9_]*\s*\(",
            # 成员访问
            "member_access": r"[a-zA-Z_][a-zA-Z0-9_]*\.(?:[a-zA-Z_][a-zA-Z0-9_]*|~[a-zA-Z_][a-zA-Z0-9_]*)",
            # 指针成员访问
            "pointer_member_access": r"[a-zA-Z_][a-zA-Z0-9_]*->(?:[a-zA-Z_][a-zA-Z0-9_]*|~[a-zA-Z_][a-zA-Z0-9_]*)",
            # 命名空间访问
            "namespace_access": r"[a-zA-Z_][a-zA-Z0-9_]*::[a-zA-Z_][a-zA-Z0-9_]*",
            # 变量声明
            "variable_declaration": r"(?:const|volatile|constexpr|static|thread_local|auto|register|extern)?\s*(?:[a-zA-Z_][a-zA-Z0-9_:&*<>]*\s+)+[a-zA-Z_][a-zA-Z0-9_]*(?:\s*=.*?)?;",
            # 操作符
            "operator": r"[+\-*/%=<>!&|^~?:.,;]+",
            # 括号
            "brackets": r"[()\[\]{}]",
            # 标签
            "label": r"[a-zA-Z_][a-zA-Z0-9_]*:",
            # goto语句
            "goto": r"\bgoto\s+[a-zA-Z_][a-zA-Z0-9_]*",
            # 宏定义
            "macro_define": r"^\s*#\s*define\s+[a-zA-Z_][a-zA-Z0-9_]*",
            # 宏调用
            "macro_call": r"[A-Z_][A-Z0-9_]*\s*\(",
            # 类型别名
            "type_alias": r"\busing\s+[a-zA-Z_][a-zA-Z0-9_]*\s*=",
            # typedef
            "typedef": r"\btypedef\s+.*;",
            # 属性
            "attribute": r"\[\[.*?\]\]",
            # C++20概念
            "concept_def": r"\bconcept\s+[a-zA-Z_][a-zA-Z0-9_]*\s*=",
            # C++20 requires子句
            "requires_clause": r"\brequires\s+.*",
            # C++20模块导入
            "module_import": r"\bimport\s+.*;",
            # C++20模块导出
            "module_export": r"\bexport\s+.*;",
            # C++20模块声明
            "module_declaration": r"\bmodule\s+.*;",
            # C++20协程
            "co_await": r"\bco_await\b",
            "co_return": r"\bco_return\b",
            "co_yield": r"\bco_yield\b",
            # C++20空间
            "ranges": r"ranges::[a-zA-Z_][a-zA-Z0-9_]*",
            "views": r"views::[a-zA-Z_][a-zA-Z0-9_]*",
            # C++23特性
            "print": r"\bstd::print\b",
            "println": r"\bstd::println\b",
            # Lambda表达式
            "lambda": r"\[.*\]\s*\([^)]*\)\s*(?:mutable\s+)?(?:noexcept\s+)?(?:->\s*[a-zA-Z_][a-zA-Z0-9_:&*<>]*)?\s*\{",
            # 异常规范
            "exception_spec": r"(?:noexcept|throw)\s*\([^)]*\)",
            # 友元声明
            "friend": r"\bfriend\s+(?:class|struct)\s+[a-zA-Z_][a-zA-Z0-9_]*",
            # 虚函数声明
            "virtual": r"\bvirtual\s+.*",
            # 纯虚函数
            "pure_virtual": r"=\s*0\s*;",
            # 重载操作符
            "operator_overload": r"\boperator\s+[+\-*/%=<>!&|^~?:.,;[\](){}]+",
            # 类型转换操作符
            "conversion_operator": r"\boperator\s+[a-zA-Z_][a-zA-Z0-9_:&*<>]*",
            # 初始化列表
            "initializer_list": r"\{.*\}",
            # 统一初始化
            "uniform_initialization": r"[a-zA-Z_][a-zA-Z0-9_]*\s*\{.*\}",
            # 委托构造函数
            "delegating_constructor": r"[a-zA-Z_][a-zA-Z0-9_]*\s*::\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)\s*:\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)",
            # 继承列表
            "inheritance_list": r":\s*(?:public|private|protected)\s+[a-zA-Z_][a-zA-Z0-9_<>]*",
            # 成员初始化列表
            "member_initializer_list": r":\s*[a-zA-Z_][a-zA-Z0-9_]*\s*(?:\([^)]*\)|\{.*\})",
            # 静态断言
            "static_assert": r"\bstatic_assert\s*\([^)]*\)",
            # 类型特征
            "type_trait": r"std::is_[a-zA-Z_][a-zA-Z0-9_]*",
            # 常量表达式
            "consteval": r"\bconsteval\b",
            "constinit": r"\bconstinit\b",
            # C++20三路比较操作符
            "spaceship": r"<=>",
            # C++20位域
            "bitfield": r"[a-zA-Z_][a-zA-Z0-9_]*\s*:\s*[0-9]+",
            # C++20结构化绑定
            "structured_binding": r"\[.*\]\s*=.*;",
            # C++20 if/switch初始化器
            "if_switch_initializer": r"(?:if|switch)\s*\([^)]*\)\s*{",
            # C++20范围for循环
            "range_for": r"for\s*\([^)]*:\s*[^)]*\)",
            # C++20模板参数列表
            "template_parameter_list": r"template\s*<.*>",
            # C++20概念约束
            "concept_constraint": r"[a-zA-Z_][a-zA-Z0-9_]*\s*[a-zA-Z_][a-zA-Z0-9_]*\s*requires",
            # C++20 requires表达式
            "requires_expression": r"requires\s*\([^)]*\)\s*\{.*\}",
            # C++20模块分区
            "module_partition": r"\bexport\s+module\s+.*:[a-zA-Z_][a-zA-Z0-9_]*",
            # C++20全局模块片段
            "global_module_fragment": r"\bmodule\s*;",
            # C++20私有模块片段
            "private_module_fragment": r"\bmodule\s*:\s*private",
            # C++23特性
            "explicit_object_parameter": r"this\s+[a-zA-Z_][a-zA-Z0-9_]*",
            # C++23 if constexpr
            "if_constexpr": r"\bif\s+constexpr\s*\([^)]*\)",
            # C++23 std::expected
            "expected": r"std::expected<[^>]*>",
            # C++23 std::mdspan
            "mdspan": r"std::mdspan<[^>]*>",
            # C++23 std::flat_map
            "flat_map": r"std::flat_map<[^>]*>",
            # C++23 std::flat_set
            "flat_set": r"std::flat_set<[^>]*>",
        }

        # 标签样式 - 使用适合C/C++语言的配色方案
        self._tag_styles = {
            "preprocessor": {
                "foreground": "#C586C0",
                "font": "bold",
            },  # 紫色粗体用于预处理指令
            "comment": {
                "foreground": "#6A9955",
                "font": "italic",
            },  # 绿色斜体用于单行注释
            "multiline_comment": {
                "foreground": "#6A9955",
                "font": "italic",
            },  # 绿色斜体用于多行注释
            "string": {"foreground": "#CE9178"},  # 橙色用于字符串
            "raw_string": {"foreground": "#CE9178"},  # 橙色用于原始字符串
            "char": {"foreground": "#CE9178"},  # 橙色用于字符
            "number": {"foreground": "#B5CEA8"},  # 浅绿色用于数字
            "hex_number": {"foreground": "#B5CEA8"},  # 浅绿色用于十六进制数字
            "octal_number": {"foreground": "#B5CEA8"},  # 浅绿色用于八进制数字
            "binary_number": {"foreground": "#B5CEA8"},  # 浅绿色用于二进制数字
            "boolean": {"foreground": "#569CD6"},  # 蓝色用于布尔值
            "nullptr": {"foreground": "#569CD6"},  # 蓝色用于nullptr
            "identifier": {"foreground": "#D4D4D4"},  # 默认颜色用于标识符
            "class_def": {
                "foreground": "#569CD6",
                "font": "bold",
            },  # 蓝色粗体用于类定义
            "enum_def": {
                "foreground": "#569CD6",
                "font": "bold",
            },  # 蓝色粗体用于枚举定义
            "namespace_def": {
                "foreground": "#C586C0",
                "font": "bold",
            },  # 紫色粗体用于命名空间定义
            "function_def": {
                "foreground": "#DCDCAA",
                "font": "bold",
            },  # 浅黄色粗体用于函数定义
            "template_def": {
                "foreground": "#C586C0",
                "font": "bold",
            },  # 紫色粗体用于模板定义
            "method_def": {
                "foreground": "#DCDCAA",
                "font": "bold",
            },  # 浅黄色粗体用于成员函数定义
            "constructor_def": {
                "foreground": "#DCDCAA",
                "font": "bold",
            },  # 浅黄色粗体用于构造函数
            "destructor_def": {
                "foreground": "#DCDCAA",
                "font": "bold",
            },  # 浅黄色粗体用于析构函数
            "function_call": {"foreground": "#DCDCAA"},  # 浅黄色用于函数调用
            "member_access": {"foreground": "#9CDCFE"},  # 浅蓝色用于成员访问
            "pointer_member_access": {
                "foreground": "#9CDCFE"
            },  # 浅蓝色用于指针成员访问
            "namespace_access": {"foreground": "#C586C0"},  # 紫色用于命名空间访问
            "variable_declaration": {"foreground": "#4EC9B0"},  # 青色用于变量声明
            "operator": {"foreground": "#D4D4D4"},  # 默认颜色用于操作符
            "brackets": {"foreground": "#FFD700"},  # 金色用于括号
            "label": {"foreground": "#C586C0", "font": "bold"},  # 紫色粗体用于标签
            "goto": {"foreground": "#C586C0", "font": "bold"},  # 紫色粗体用于goto语句
            "macro_define": {
                "foreground": "#C586C0",
                "font": "bold",
            },  # 紫色粗体用于宏定义
            "macro_call": {"foreground": "#C586C0"},  # 紫色用于宏调用
            "type_alias": {
                "foreground": "#C586C0",
                "font": "bold",
            },  # 紫色粗体用于类型别名
            "typedef": {"foreground": "#C586C0", "font": "bold"},  # 紫色粗体用于typedef
            "attribute": {
                "foreground": "#C586C0",
                "font": "italic",
            },  # 紫色斜体用于属性
            "concept_def": {
                "foreground": "#C586C0",
                "font": "bold",
            },  # 紫色粗体用于概念定义
            "requires_clause": {"foreground": "#C586C0"},  # 紫色用于requires子句
            "module_import": {
                "foreground": "#C586C0",
                "font": "bold",
            },  # 紫色粗体用于模块导入
            "module_export": {
                "foreground": "#C586C0",
                "font": "bold",
            },  # 紫色粗体用于模块导出
            "module_declaration": {
                "foreground": "#C586C0",
                "font": "bold",
            },  # 紫色粗体用于模块声明
            "co_await": {
                "foreground": "#C586C0",
                "font": "bold",
            },  # 紫色粗体用于co_await
            "co_return": {
                "foreground": "#C586C0",
                "font": "bold",
            },  # 紫色粗体用于co_return
            "co_yield": {
                "foreground": "#C586C0",
                "font": "bold",
            },  # 紫色粗体用于co_yield
            "ranges": {"foreground": "#C586C0"},  # 紫色用于ranges
            "views": {"foreground": "#C586C0"},  # 紫色用于views
            "print": {"foreground": "#DCDCAA"},  # 浅黄色用于print
            "println": {"foreground": "#DCDCAA"},  # 浅黄色用于println
            "lambda": {
                "foreground": "#DCDCAA",
                "font": "bold",
            },  # 浅黄色粗体用于Lambda表达式
            "exception_spec": {"foreground": "#C586C0"},  # 紫色用于异常规范
            "friend": {"foreground": "#C586C0", "font": "bold"},  # 紫色粗体用于友元声明
            "virtual": {
                "foreground": "#C586C0",
                "font": "bold",
            },  # 紫色粗体用于虚函数声明
            "pure_virtual": {
                "foreground": "#C586C0",
                "font": "italic",
            },  # 紫色斜体用于纯虚函数
            "operator_overload": {
                "foreground": "#DCDCAA",
                "font": "bold",
            },  # 浅黄色粗体用于重载操作符
            "conversion_operator": {
                "foreground": "#DCDCAA",
                "font": "bold",
            },  # 浅黄色粗体用于类型转换操作符
            "initializer_list": {"foreground": "#4EC9B0"},  # 青色用于初始化列表
            "uniform_initialization": {"foreground": "#4EC9B0"},  # 青色用于统一初始化
            "delegating_constructor": {
                "foreground": "#DCDCAA",
                "font": "bold",
            },  # 浅黄色粗体用于委托构造函数
            "inheritance_list": {"foreground": "#C586C0"},  # 紫色用于继承列表
            "member_initializer_list": {
                "foreground": "#4EC9B0"
            },  # 青色用于成员初始化列表
            "static_assert": {
                "foreground": "#C586C0",
                "font": "bold",
            },  # 紫色粗体用于静态断言
            "type_trait": {"foreground": "#C586C0"},  # 紫色用于类型特征
            "consteval": {
                "foreground": "#C586C0",
                "font": "bold",
            },  # 紫色粗体用于consteval
            "constinit": {
                "foreground": "#C586C0",
                "font": "bold",
            },  # 紫色粗体用于constinit
            "spaceship": {
                "foreground": "#DCDCAA",
                "font": "bold",
            },  # 浅黄色粗体用于三路比较操作符
            "bitfield": {"foreground": "#4EC9B0"},  # 青色用于位域
            "structured_binding": {"foreground": "#4EC9B0"},  # 青色用于结构化绑定
            "if_switch_initializer": {
                "foreground": "#C586C0"
            },  # 紫色用于if/switch初始化器
            "range_for": {"foreground": "#C586C0"},  # 紫色用于范围for循环
            "template_parameter_list": {
                "foreground": "#C586C0",
                "font": "bold",
            },  # 紫色粗体用于模板参数列表
            "concept_constraint": {"foreground": "#C586C0"},  # 紫色用于概念约束
            "requires_expression": {"foreground": "#C586C0"},  # 紫色用于requires表达式
            "module_partition": {
                "foreground": "#C586C0",
                "font": "bold",
            },  # 紫色粗体用于模块分区
            "global_module_fragment": {
                "foreground": "#C586C0",
                "font": "bold",
            },  # 紫色粗体用于全局模块片段
            "private_module_fragment": {
                "foreground": "#C586C0",
                "font": "bold",
            },  # 紫色粗体用于私有模块片段
            "explicit_object_parameter": {
                "foreground": "#C586C0"
            },  # 紫色用于显式对象参数
            "if_constexpr": {
                "foreground": "#C586C0",
                "font": "bold",
            },  # 紫色粗体用于if constexpr
            "expected": {"foreground": "#C586C0"},  # 紫色用于std::expected
            "mdspan": {"foreground": "#C586C0"},  # 紫色用于std::mdspan
            "flat_map": {"foreground": "#C586C0"},  # 紫色用于std::flat_map
            "flat_set": {"foreground": "#C586C0"},  # 紫色用于std::flat_set
        }
