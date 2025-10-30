"""
增强版语法高亮模块 - 高性能、后台线程分析、增量更新

功能特点：
1. 使用Pygments进行语法分析，支持多种编程语言
2. 在后台线程中执行语法分析，避免阻塞GUI
3. 增量更新机制，只处理修改的部分
4. 性能优化，支持大文件处理
5. 可配置的更新延迟和性能选项
6. 错误处理和自动恢复

使用方式：
- 创建文本组件
- 创建EnhancedSyntaxHighlighter实例，传入文本组件和配置参数
- 高亮器会自动监听文本变化并更新高亮
"""

import tkinter as tk
import pygments
from pygments.lexers import get_lexer_by_name, guess_lexer, get_all_lexers
from pygments.styles import get_style_by_name
from pygments.token import Token
import threading
import time
import queue
import re
from typing import Optional, Dict, Set, Tuple, Any


class EnhancedSyntaxHighlighter:
    """
    独立的语法高亮器类
    可以为任何兼容的tkinter文本组件提供语法高亮功能
    """

    def __init__(
        self, text_widget, lexer_name="python", style_name="default", **kwargs
    ):
        """
        初始化语法高亮器

        参数:
            text_widget: 要进行高亮的文本组件对象
            lexer_name: 语法解析器名称，如'python', 'javascript'等，'auto'表示自动检测
            style_name: 高亮样式名称
            **kwargs: 其他配置参数
        """
        # 存储文本组件引用
        self.text_widget = text_widget

        # Pygments相关设置
        self.lexer_name = lexer_name
        self.style_name = style_name
        self.lexer = get_lexer_by_name(lexer_name) if lexer_name != "auto" else None
        self.style = get_style_by_name(style_name)

        # 性能优化设置
        self.enable_optimizations = kwargs.get("enable_optimizations", True)  # 是否启用性能优化
        self.delay_update = kwargs.get("delay_update", 100)  # 延迟更新时间（毫秒）
        self.incremental_update = kwargs.get("incremental_update", True)  # 是否启用增量更新
        self.max_lines_for_full_update = kwargs.get("max_lines_for_full_update", 5000) # 最大行数触发全量更新

        # 状态变量
        self._updating = False
        self._update_timer = None
        self._modified_lines = set()
        self._highlight_queue = queue.Queue()
        self._worker_thread = None
        self._stop_event = threading.Event()
        self._lock = threading.RLock()

        # 初始化
        self._init_tags()
        self._bind_events()
        self._start_worker_thread()

        # 预编译常用正则表达式
        self._compile_regex()

    def _init_tags(self):
        """
        初始化所有可能的token样式标签
        """
        # 清除所有现有tag（保留'sel'选中样式）
        for tag in self.text_widget.tag_names():
            if tag != "sel":
                self.text_widget.tag_delete(tag)

        # 为每种token类型创建tag
        token_styles = {}

        # 遍历样式类的所有属性
        for attr_name in dir(self.style):
            if not attr_name.startswith("_"):
                attr_value = getattr(self.style, attr_name)
                if isinstance(attr_value, tuple) and len(attr_value) >= 2:
                    try:
                        if isinstance(attr_value[0], Token):
                            token_type = attr_value[0]
                            style_def = attr_value[1]
                            token_styles[token_type] = style_def
                    except:
                        continue

        # 如果没有找到样式，使用默认样式
        if not token_styles:
            self._setup_default_styles()
            return

        # 应用样式
        for token_type, style_def in token_styles.items():
            tag_name = str(token_type)
            tag_config = {}

            # 解析样式定义
            if isinstance(style_def, str):
                style_parts = style_def.split()
                for part in style_parts:
                    if part.startswith("#") and len(part) == 7:
                        tag_config["foreground"] = part
                    elif part == "underline":
                        tag_config["underline"] = True
            elif isinstance(style_def, dict):
                if "color" in style_def and style_def["color"]:
                    tag_config["foreground"] = f"#{style_def['color']}"
                if "bgcolor" in style_def and style_def["bgcolor"]:
                    tag_config["background"] = f"#{style_def['bgcolor']}"
                if style_def.get("underline"):
                    tag_config["underline"] = True

            if tag_config:
                self.text_widget.tag_configure(tag_name, **tag_config)

    def _setup_default_styles(self):
        """
        设置默认语法高亮样式
        只设置颜色，不设置字体样式，让编辑器自己管理字体
        """
        default_styles = {
            Token.Keyword: {"foreground": "#0000FF"},  # 关键字 - 蓝色
            Token.Name.Function: {"foreground": "#008000"},  # 函数名 - 绿色
            Token.Name.Class: {"foreground": "#008000"},  # 类名 - 绿色
            Token.String: {"foreground": "#800080"},  # 字符串 - 紫色
            Token.Comment: {"foreground": "#808080"},  # 注释 - 灰色
            Token.Number: {"foreground": "#FF0000"},  # 数字 - 红色
            Token.Operator: {"foreground": "#000000"},  # 运算符 - 黑色
            Token.Punctuation: {"foreground": "#000000"},  # 符号 - 黑色
            Token.Name.Builtin: {"foreground": "#000080"},  # 内置函数 - 蓝色
            Token.Keyword.Declaration: {"foreground": "#0000FF"},  # 声明关键字 - 蓝色
            Token.Keyword.Type: {"foreground": "#0000FF"},  # 类型关键字 - 蓝色
        }

        for token_type, style_config in default_styles.items():
            tag_name = str(token_type)
            self.text_widget.tag_configure(tag_name, **style_config)

    def _bind_events(self):
        """
        绑定文本修改和其他事件
        """
        # 使用<<Modified>>事件而不是KeyRelease，减少事件触发次数
        self.text_widget.bind("<<Modified>>", self._on_text_modified)  # 文本修改事件

        # 鼠标事件
        self.text_widget.bind("<ButtonRelease>", self._on_mouse_release)  # 鼠标释放事件

        # 滚动事件
        self.text_widget.bind("<MouseWheel>", self._on_scroll)  # 鼠标滚轮事件

        # 尝试获取主窗口并设置关闭事件处理
        master = self.text_widget.master
        if hasattr(master, "protocol"):
            # 保存原始的协议处理函数
            original_protocol = master.protocol("WM_DELETE_WINDOW")
            if original_protocol:

                def on_closing():
                    self.destroy()
                    original_protocol()

            else:

                def on_closing():
                    self.destroy()
                    master.destroy()

            master.protocol("WM_DELETE_WINDOW", on_closing)
        elif hasattr(master, "winfo_toplevel"):
            # 如果master是Frame等组件，获取根窗口
            # 不再接管窗口关闭协议，而是提供destroy方法供编辑器调用
            # 这样编辑器的关闭逻辑可以正常执行，同时适当清理语法高亮器的资源
            pass

    def _compile_regex(self):
        """
        预编译常用正则表达式
        """
        self._line_regex = re.compile(r"^.*$", re.MULTILINE)

    def _start_worker_thread(self):
        """
        启动后台工作线程
        """
        self._stop_event.clear()
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()

    def _worker_loop(self):
        """
        工作线程主循环，处理语法高亮任务
        """
        while not self._stop_event.is_set():
            try:
                # 从队列获取任务，最多等待0.1秒
                task = self._highlight_queue.get(timeout=0.1)
                if task["type"] == "full":
                    tokens = self._process_full_highlight(task["text"])
                    # 将结果发布到主线程
                    self.text_widget.after(
                        0, self._apply_highlighting, tokens, task["text"]
                    )
                elif task["type"] == "incremental":
                    tokens = self._process_incremental_highlight(
                        task["text_block"], task["min_line"], task["max_line"]
                    )
                    # 将结果发布到主线程
                    self.text_widget.after(
                        0,
                        self._apply_incremental_highlighting,
                        tokens,
                        task["min_line"],
                    )
                self._highlight_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"工作线程错误: {e}")
                # 出错时不崩溃，继续处理下一个任务
                continue

    def _on_text_modified(self, event=None):
        """
        文本修改时触发
        """
        # 检查是否是我们自己触发的修改事件
        if self._updating or not self.text_widget.edit_modified():
            return

        # 记录修改的行
        if self.incremental_update:
            insert_pos = self.text_widget.index(tk.INSERT)
            line_num = int(insert_pos.split(".")[0])
            self._modified_lines.add(line_num)
            # 也标记前后几行，确保上下文正确
            for i in range(-2, 3):
                self._modified_lines.add(line_num + i)

        # 使用延迟更新，避免频繁更新
        if self.enable_optimizations and self.delay_update > 0:
            if self._update_timer:
                self.text_widget.after_cancel(self._update_timer)

            # 计算延迟时间（可以根据文件大小动态调整）
            line_count = int(self.text_widget.index("end-1c").split(".")[0])
            dynamic_delay = min(self.delay_update, max(50, line_count // 100))

            self._update_timer = self.text_widget.after(
                dynamic_delay, self._queue_highlight_update
            )
        else:
            self._queue_highlight_update()

        # 不再重置修改状态，让编辑器自己处理修改状态的检测和重置
        # 这样可以确保状态栏正确显示"已修改"状态，并且自动保存功能能够正常工作

    def _on_mouse_release(self, event=None):
        """
        鼠标释放时检查是否需要更新
        """
        # 当鼠标选择文本时，可能需要更新高亮
        if self._modified_lines:
            self._on_text_modified()

    def _on_scroll(self, event=None):
        """
        滚动时的处理
        可以在这里添加可见区域优化
        """
        pass

    def _queue_highlight_update(self):
        """
        将高亮更新任务加入队列
        """
        # 获取所有文本
        text = self.text_widget.get("1.0", tk.END)
        line_count = text.count("\n") + 1

        if not text.strip():
            return

        # 清空队列中之前的任务，只保留最新的
        while not self._highlight_queue.empty():
            try:
                self._highlight_queue.get_nowait()
                self._highlight_queue.task_done()
            except queue.Empty:
                break

        # 根据文件大小选择更新策略
        if self.enable_optimizations and line_count <= self.max_lines_for_full_update:
            # 小文件使用全量更新
            self._highlight_queue.put({"type": "full", "text": text})
        else:
            # 大文件或增量更新使用增量方式
            if self._modified_lines:
                # 获取修改的行范围
                min_line = max(1, min(self._modified_lines))
                max_line = min(line_count, max(self._modified_lines))

                # 扩展范围以确保上下文正确
                context_lines = 2
                min_line = max(1, min_line - context_lines)
                max_line = min(line_count, max_line + context_lines)

                # 获取需要更新的文本块
                start_pos = f"{min_line}.0"
                end_pos = f"{max_line}.end"
                text_block = self.text_widget.get(start_pos, end_pos)

                self._highlight_queue.put(
                    {
                        "type": "incremental",
                        "text_block": text_block,
                        "min_line": min_line,
                        "max_line": max_line,
                    }
                )

                # 清空修改记录
                self._modified_lines.clear()
            else:
                # 如果没有修改记录，使用全量更新
                self._highlight_queue.put({"type": "full", "text": text})

    def _process_full_highlight(self, text):
        """
        在后台线程中处理全量高亮分析
        """
        try:
            # 尝试重新猜测lexer
            if self.lexer_name == "auto":
                self.lexer = guess_lexer(text)

            # 使用Pygments进行语法分析
            tokens = list(pygments.lex(text, self.lexer))
            return tokens
        except Exception as e:
            print(f"全量高亮分析错误: {e}")
            # 返回空列表，让主线程处理错误
            return []

    def _process_incremental_highlight(self, text_block, min_line, max_line):
        """
        在后台线程中处理增量高亮分析
        """
        try:
            # 对于自动检测，可能需要使用当前lexer
            if self.lexer_name == "auto" and not self.lexer:
                # 如果lexer尚未初始化，尝试猜测
                try:
                    self.lexer = guess_lexer(text_block)
                except:
                    # 如果猜测失败，使用Python lexer作为默认
                    self.lexer = get_lexer_by_name("python")

            # 使用Pygments进行语法分析
            tokens = list(pygments.lex(text_block, self.lexer))
            return tokens
        except Exception as e:
            print(f"增量高亮分析错误: {e}")
            # 返回空列表，让主线程处理错误
            return []

    def _apply_highlighting(self, tokens, text):
        """
        在主线程中应用高亮结果
        """
        if not tokens:
            # 如果分析失败，重新初始化标签
            self._init_tags()
            return

        self._updating = True
        try:
            # 清除所有现有高亮（保留选中样式）
            for tag in self.text_widget.tag_names():
                if tag != "sel":
                    self.text_widget.tag_remove(tag, "1.0", tk.END)

            # 应用新的高亮
            current_pos = "1.0"
            for token_type, value in tokens:
                # 计算结束位置
                end_pos = self.text_widget.index(f"{current_pos}+{len(value)}c")

                # 找到最具体的token类型
                current_token = token_type
                tag_applied = False

                while current_token is not None:
                    tag_name = str(current_token)
                    if tag_name in self.text_widget.tag_names():
                        self.text_widget.tag_add(tag_name, current_pos, end_pos)
                        tag_applied = True
                        break
                    current_token = current_token.parent

                current_pos = end_pos
        except Exception as e:
            print(f"应用高亮错误: {e}")
            # 出错时重新初始化标签
            self._init_tags()
        finally:
            self._updating = False

    def _apply_incremental_highlighting(self, tokens, min_line):
        """
        在主线程中应用增量高亮结果
        """
        if not tokens:
            return

        self._updating = True
        try:
            # 清除该区域的现有高亮
            start_pos = f"{min_line}.0"
            # 计算结束位置（基于tokens的总长度）
            total_length = sum(len(value) for _, value in tokens)
            end_pos = self.text_widget.index(f"{start_pos}+{total_length}c")

            for tag in self.text_widget.tag_names():
                if tag != "sel":
                    self.text_widget.tag_remove(tag, start_pos, end_pos)

            # 应用新的高亮到该区域
            current_pos = start_pos
            for token_type, value in tokens:
                end_pos = self.text_widget.index(f"{current_pos}+{len(value)}c")

                # 找到最具体的token类型
                current_token = token_type
                tag_applied = False

                while current_token is not None:
                    tag_name = str(current_token)
                    if tag_name in self.text_widget.tag_names():
                        self.text_widget.tag_add(tag_name, current_pos, end_pos)
                        tag_applied = True
                        break
                    current_token = current_token.parent

                current_pos = end_pos
        except Exception as e:
            print(f"应用增量高亮错误: {e}")
            # 增量更新失败时回退到全量更新
            self.text_widget.after(0, self._queue_highlight_update)
        finally:
            self._updating = False

    def set_lexer(self, lexer_name):
        """
        设置语法解析器

        参数:
            lexer_name: 语法解析器名称，如'python', 'javascript'等，'auto'表示自动检测
        """
        with self._lock:
            self.lexer_name = lexer_name
            if lexer_name == "auto":
                self.lexer = None
            else:
                try:
                    self.lexer = get_lexer_by_name(lexer_name)
                except Exception as e:
                    print(f"设置lexer错误: {e}")
                    self.lexer = get_lexer_by_name("python")  # 使用Python作为默认

        # 立即更新高亮
        self._queue_highlight_update()

    def set_style(self, style_name):
        """
        设置高亮样式

        参数:
            style_name: 高亮样式名称
        """
        with self._lock:
            self.style_name = style_name
            try:
                self.style = get_style_by_name(style_name)
                self._init_tags()
            except Exception as e:
                print(f"设置style错误: {e}")
                self.style = get_style_by_name("default")  # 使用默认样式
                self._init_tags()

        # 立即更新高亮
        self._queue_highlight_update()

    def set_performance_options(self, **options):
        """
        设置性能选项

        参数:
            enable_optimizations: 是否启用性能优化
            delay_update: 更新延迟（毫秒）
            incremental_update: 是否启用增量更新
            max_lines_for_full_update: 全量更新的最大行数
        """
        with self._lock:
            for key, value in options.items():
                if hasattr(self, key):
                    setattr(self, key, value)

    def update_highlighting(self):
        """
        手动触发高亮更新
        当外部代码修改了文本内容时可以调用此方法
        """
        self._queue_highlight_update()

    def destroy(self):
        """
        销毁高亮器，清理资源
        """
        # 设置停止事件
        self._stop_event.set()
        
        # 取消更新计时器
        if self._update_timer:
            try:
                self.text_widget.after_cancel(self._update_timer)
            except:
                pass
                
        # 等待工作线程结束
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=0.5)  # 等待工作线程结束
            
        # 清理所有高亮标签（保留'sel'选中样式）
        try:
            for tag in self.text_widget.tag_names():
                if tag != "sel":
                    self.text_widget.tag_remove(tag, "1.0", tk.END)
                    self.text_widget.tag_delete(tag)
        except Exception as e:
            print(f"清理标签时出错: {e}")


# 缓存语言列表，避免重复加载
_language_cache = None

# 编程语言与文件扩展名的映射字典
# key: 语言名称, value: 扩展名列表
LANGUAGE_EXTENSIONS = {
    'Python': ['.py', '.pyw', '.pyx', '.pxd', '.pxi'],
    'Java': ['.java', '.class'],
    'JavaScript': ['.js', '.jsx', '.mjs', '.cjs'],
    'TypeScript': ['.ts', '.tsx'],
    'HTML': ['.html', '.htm', '.xhtml'],
    'CSS': ['.css'],
    'SCSS': ['.scss'],
    'Sass': ['.sass'],
    'Less': ['.less'],
    'PHP': ['.php', '.php3', '.php4', '.php5', '.phtml'],
    'C': ['.c', '.h'],
    'C++': ['.cpp', '.cxx', '.cc', '.hpp', '.hxx', '.hh'],
    'C#': ['.cs'],
    'Go': ['.go'],
    'Rust': ['.rs'],
    'Swift': ['.swift'],
    'Kotlin': ['.kt', '.kts'],
    'Ruby': ['.rb', '.ruby'],
    'Perl': ['.pl', '.pm', '.perl'],
    'Lua': ['.lua'],
    'Shell': ['.sh', '.bash', '.zsh'],
    'PowerShell': ['.ps1', '.psm1', '.psd1'],
    'SQL': ['.sql'],
    'YAML': ['.yaml', '.yml'],
    'JSON': ['.json'],
    'XML': ['.xml'],
    'Markdown': ['.md', '.markdown'],
    'R': ['.r'],
    'Scala': ['.scala', '.sc'],
    'Dart': ['.dart'],
    'Objective-C': ['.m', '.mm'],
    'MATLAB': ['.m'],
    'Groovy': ['.groovy'],
    'CoffeeScript': ['.coffee'],
    'Erlang': ['.erl', '.hrl'],
    'Elixir': ['.ex', '.exs'],
    'Haskell': ['.hs', '.lhs'],
    'OCaml': ['.ml', '.mli'],
    'F#': ['.fs', '.fsi', '.fsx'],
    'Visual Basic': ['.vb'],
    'Pascal': ['.pas', '.pp'],
    'Fortran': ['.f', '.for', '.f90', '.f95'],
    'Julia': ['.jl'],
    'Clojure': ['.clj', '.cljs', '.cljc'],
    'Scheme': ['.scm', '.ss'],
    'Lisp': ['.lisp', '.lsp'],
    'Prolog': ['.pl', '.pro'],
    'Tcl': ['.tcl'],
    'Assembly': ['.asm', '.s'],
    'D': ['.d'],
    'Nim': ['.nim'],
    'Zig': ['.zig'],
    'V': ['.v'],
    'Crystal': ['.cr'],
    'Reason': ['.re', '.rei'],
    'GraphQL': ['.graphql', '.gql'],
    'Dockerfile': ['Dockerfile'],
    'Makefile': ['Makefile'],
    'CMake': ['.cmake', 'CMakeLists.txt'],
    'Ini': ['.ini'],
    'TOML': ['.toml'],
    'Diff': ['.diff', '.patch'],
    'ApacheConf': ['.htaccess'],
}

def get_lexer_name_by_filename(file_name):
    """
    根据文件名获取对应的语法分析器名称
    
    参数:
        file_name: 文件名，例如 'example.py', 'index.html' 等
    
    返回:
        str: 语法分析器名称，如果找不到匹配项则返回 'auto'
    """
    # 从文件名中提取扩展名
    if '.' in file_name:
        file_extension = '.' + file_name.split('.')[-1]
    else:
        # 如果没有扩展名，返回默认值
        return 'auto'
    
    # 遍历映射字典查找匹配的扩展名
    for language, extensions in LANGUAGE_EXTENSIONS.items():
        if file_extension in extensions:
            # 返回语言名称的小写形式作为lexer名称
            return language.lower()
    
    # 如果没有找到匹配项，返回默认值'auto'
    return 'auto'

def get_all_languages():
    """
    获取Pygments支持的所有语言及其别名
    使用缓存机制，避免重复加载

    返回:
        list: 包含(语言名称, 别名)元组的列表
    """
    global _language_cache
    
    # 如果缓存已存在，直接返回
    if _language_cache is not None:
        return _language_cache
    
    # 延迟加载语言列表
    languages = []
    seen_aliases = set()
    for name, aliases, _, _ in pygments.lexers.get_all_lexers():
        # 添加语言名称和主要别名
        alias = aliases[0] if aliases else name.lower()
        # 避免重复的别名
        if alias not in seen_aliases:
            languages.append((name, alias))
            seen_aliases.add(alias)
    # 按名称排序
    languages.sort(key=lambda x: x[0])
    
    # 缓存结果
    _language_cache = languages
    return languages


# 测试用的简单应用示例
if __name__ == "__main__":

    def create_demo_app():
        """
        创建演示应用
        展示如何使用EnhancedSyntaxHighlighter
        添加语言选择和控制按钮
        """
        root = tk.Tk()
        root.title("增强版语法高亮模块演示")
        root.geometry("1000x700")

        # 创建控制框架
        control_frame = tk.Frame(root)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        # 获取所有语言
        languages = get_all_languages()
        language_names = [lang[0] for lang in languages]
        language_aliases = dict(languages)

        # 创建语言选择标签
        lang_label = tk.Label(control_frame, text="选择语言:")
        lang_label.pack(side=tk.LEFT, padx=5)

        # 创建语言选择下拉菜单
        lang_var = tk.StringVar(root)
        lang_var.set("Python")  # 默认选择Python
        lang_menu = tk.OptionMenu(control_frame, lang_var, *language_names)
        lang_menu.pack(side=tk.LEFT, padx=5)

        # 创建样式选择标签
        style_label = tk.Label(control_frame, text="选择样式:")
        style_label.pack(side=tk.LEFT, padx=5)

        # 获取所有支持的样式
        style_names = sorted(pygments.styles.get_all_styles())
        style_var = tk.StringVar(root)
        style_var.set("monokai")  # 默认样式
        style_menu = tk.OptionMenu(control_frame, style_var, *style_names)
        style_menu.pack(side=tk.LEFT, padx=5)

        # 创建一个普通的文本框
        text_editor = tk.Text(root, wrap=tk.NONE, undo=True, font=("Consolas", 10))
        text_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 创建滚动条
        scrollbar = tk.Scrollbar(root, command=text_editor.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_editor.config(yscrollcommand=scrollbar.set)

        # 创建状态栏
        status_var = tk.StringVar()
        status_var.set("就绪 - 当前语言: Python")
        status_bar = tk.Label(
            root, textvariable=status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 创建语法高亮器，传入文本框对象
        highlighter = EnhancedSyntaxHighlighter(
            text_editor, lexer_name="python", style_name="monokai", delay_update=100
        )

        # 定义切换语言的函数
        def change_language():
            try:
                selected_lang = lang_var.get()
                if selected_lang in language_aliases:
                    lexer_name = language_aliases[selected_lang]
                    highlighter.set_lexer(lexer_name)
                    status_var.set(f"当前语言: {selected_lang}")
                else:
                    status_var.set(f"错误: 未知语言 {selected_lang}")
            except Exception as e:
                status_var.set(f"切换语言时出错: {str(e)}")

        # 定义切换样式的函数
        def change_style():
            try:
                selected_style = style_var.get()
                highlighter.set_style(selected_style)
                status_var.set(f"当前样式: {selected_style}")
            except Exception as e:
                status_var.set(f"切换样式时出错: {str(e)}")

        # 定义切换高亮的函数
        highlighting_enabled = tk.BooleanVar(value=True)

        def toggle_highlighting():
            if highlighting_enabled.get():
                # 清除所有高亮
                for tag in text_editor.tag_names():
                    if tag != "sel":
                        text_editor.tag_remove(tag, "1.0", tk.END)
                toggle_btn.config(text="开启高亮")
                status_var.set("语法高亮: 已禁用")
            else:
                highlighter.update_highlighting()
                toggle_btn.config(text="关闭高亮")
                status_var.set("语法高亮: 已启用")
            highlighting_enabled.set(not highlighting_enabled.get())

        # 定义重置按钮函数
        def reset_highlighter():
            try:
                nonlocal highlighter
                highlighter.destroy()
                highlighter = EnhancedSyntaxHighlighter(
                    text_editor,
                    lexer_name=language_aliases.get(lang_var.get(), "python"),
                    style_name=style_var.get(),
                    delay_update=100,
                )
                status_var.set("高亮器已重置")
            except Exception as e:
                status_var.set(f"重置高亮器时出错: {str(e)}")

        # 创建应用按钮
        apply_btn = tk.Button(control_frame, text="应用语言", command=change_language)
        apply_btn.pack(side=tk.LEFT, padx=5)

        # 创建样式应用按钮
        style_btn = tk.Button(control_frame, text="应用样式", command=change_style)
        style_btn.pack(side=tk.LEFT, padx=5)

        # 创建高亮切换按钮
        toggle_btn = tk.Button(
            control_frame, text="关闭高亮", command=toggle_highlighting
        )
        toggle_btn.pack(side=tk.LEFT, padx=5)

        # 创建重置按钮
        reset_btn = tk.Button(
            control_frame, text="重置高亮器", command=reset_highlighter
        )
        reset_btn.pack(side=tk.LEFT, padx=5)

        # 添加一些示例代码 - 包含多种语言的注释，方便测试不同语言的高亮
        sample_code = """\
        这是一个示例代码，包含多种语言的注释
        
        Python:
        # 这是Python注释
        def hello():
            print("Hello, World!")
        
        JavaScript:
        // 这是JavaScript注释
        function hello() {
            console.log("Hello, World!");
        }
        
        HTML:
        <!-- 这是HTML注释 -->
        <div class="example">Hello</div>
        
        CSS:
        /* 这是CSS注释 */
        .example {
            color: red;
        }
        
        Java:
        /* 这是Java多行注释 */
        public class Hello {
            public static void main(String[] args) {
                System.out.println("Hello, World!");
            }
        }
        
        C++:
        // 这是C++注释
        #include <iostream>
        using namespace std;
        
        int main() {
            cout << "Hello, World!" << endl;
            return 0;
        }
        
        SQL:
        -- 这是SQL注释
        SELECT * FROM users WHERE age > 18;
        
        切换不同的语言查看语法高亮效果！
        """

        # Python代码示例
        python_code = """
        
        class ExampleApp:
            def __init__(self, root):
                self.root = root
                self.root.title("示例应用")
                
                # 创建按钮
                self.button = tk.Button(
                    root, 
                    text="点击我", 
                    command=self.on_button_click
                )
                self.button.pack(pady=20)
                
            def on_button_click(self):
                print("按钮被点击了!")
                
        if __name__ == "__main__":
            root = tk.Tk()
            app = ExampleApp(root)
            root.mainloop()
        """

        text_editor.insert(tk.END, sample_code)
        text_editor.insert(tk.END, "\n\n# Python代码示例\n")
        text_editor.insert(tk.END, python_code)

        # 手动触发一次高亮更新
        highlighter.update_highlighting()

        # 设置窗口关闭处理
        def on_window_closing():
            # 清理高亮器资源
            highlighter.destroy()
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_window_closing)

        return root, highlighter

    # 运行演示应用
    root, _ = create_demo_app()
    root.mainloop()
