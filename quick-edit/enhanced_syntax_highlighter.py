"""
增强版语法高亮模块 - 高性能、后台线程分析、增量更新

功能特点：
1. 使用Pygments进行语法分析，支持多种编程语言
2. 在后台线程中执行语法分析，避免阻塞GUI
3. 增量更新机制，只处理修改的部分
4. 性能优化，支持大文件处理
5. 可配置的更新延迟和性能选项
6. 错误处理和自动恢复
"""

import tkinter as tk
from tkinter import scrolledtext
import pygments
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.styles import get_style_by_name
from pygments.token import Token
import threading
import time
import queue
import re

class EnhancedSyntaxHighlightText(scrolledtext.ScrolledText):
    def __init__(self, master=None, lexer_name='python', style_name='default', **kwargs):
        """
        初始化增强版语法高亮文本框
        
        参数:
            master: 父窗口组件
            lexer_name: 语法解析器名称，如'python', 'javascript'等，'auto'表示自动检测
            style_name: 高亮样式名称
            **kwargs: 传递给scrolledtext.ScrolledText的其他参数
        """
        super().__init__(master, **kwargs)
        
        # Pygments相关设置
        self.lexer_name = lexer_name
        self.style_name = style_name
        self.lexer = get_lexer_by_name(lexer_name) if lexer_name != 'auto' else None
        self.style = get_style_by_name(style_name)
        
        # 性能优化设置
        self.enable_optimizations = True  # 启用优化
        self.delay_update = 100  # 延迟更新时间（毫秒）
        self.incremental_update = True  # 增量更新
        self.max_lines_for_full_update = 5000  # 全量更新的最大行数
        
        # 状态变量
        self._updating = False  # 是否正在更新高亮
        self._update_timer = None  # 更新定时器
        self._modified_lines = set()  # 修改过的行集合
        self._last_processed_line = 0  # 上次处理的行号
        self._highlight_queue = queue.Queue()  # 高亮任务队列
        self._worker_thread = None  # 工作线程
        self._stop_event = threading.Event()  # 停止事件
        self._lock = threading.RLock()  # 线程锁
        
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
        # 清除所有现有tag
        for tag in self.tag_names():
            self.tag_delete(tag)
        
        # 设置默认字体
        self.config(font=('Consolas', 10))
        
        # 为每种token类型创建tag
        token_styles = {}
        
        # 遍历样式类的所有属性
        for attr_name in dir(self.style):
            if not attr_name.startswith('_'):
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
                    if part.startswith('#') and len(part) == 7:
                        tag_config['foreground'] = part
                    elif part == 'bold':
                        tag_config['font'] = ('Consolas', 10, 'bold')
                    elif part == 'italic':
                        tag_config['font'] = ('Consolas', 10, 'italic')
                    elif part == 'underline':
                        tag_config['underline'] = True
            elif isinstance(style_def, dict):
                if 'color' in style_def and style_def['color']:
                    tag_config['foreground'] = f"#{style_def['color']}"
                if 'bgcolor' in style_def and style_def['bgcolor']:
                    tag_config['background'] = f"#{style_def['bgcolor']}"
                if style_def.get('bold'):
                    tag_config['font'] = ('Consolas', 10, 'bold')
                if style_def.get('italic'):
                    tag_config['font'] = ('Consolas', 10, 'italic')
                if style_def.get('underline'):
                    tag_config['underline'] = True
            
            if tag_config:
                self.tag_configure(tag_name, **tag_config)
    
    def _setup_default_styles(self):
        """
        设置默认语法高亮样式
        """
        default_styles = {
            Token.Keyword: {'foreground': '#0000FF'}, # 关键字 - 蓝色
            Token.Name.Function: {'foreground': '#008000'},  # 函数名 - 绿色
            Token.Name.Class: {'foreground': '#008000', 'font': ('Consolas', 10, 'bold')},  # 类名 - 绿色加粗
            Token.String: {'foreground': '#800080'},  # 字符串 - 紫色
            Token.Comment: {'foreground': '#808080', 'font': ('Consolas', 10, 'italic')},  # 注释 - 灰色斜体
            Token.Number: {'foreground': '#FF0000'}, # 数字 - 红色
            Token.Operator: {'foreground': '#000000', 'font': ('Consolas', 10, 'bold')},  # 运算符 - 黑色加粗
            Token.Punctuation: {'foreground': '#000000'}, # 符号 - 黑色
            Token.Name.Builtin: {'foreground': '#000080'}, # 内置函数 - 蓝色
            Token.Keyword.Declaration: {'foreground': '#0000FF', 'font': ('Consolas', 10, 'bold')}, # 声明关键字 - 蓝色加粗
            Token.Keyword.Type: {'foreground': '#0000FF'} # 类型关键字 - 蓝色
        }
        
        for token_type, style_config in default_styles.items():
            tag_name = str(token_type)
            self.tag_configure(tag_name, **style_config)
    
    def _bind_events(self):
        """
        绑定文本修改和其他事件
        """
        # 使用<<Modified>>事件而不是KeyRelease，减少事件触发次数
        self.bind('<<Modified>>', self._on_text_modified) # 文本修改事件
        
        # 鼠标事件
        self.bind('<ButtonRelease>', self._on_mouse_release) # 鼠标释放事件
        
        # 滚动事件
        self.bind('<MouseWheel>', self._on_scroll) # 鼠标滚轮事件
        
        # 窗口关闭时清理 - 只在master是Tk窗口对象时设置protocol
        if hasattr(self.master, 'protocol'):
            self.master.protocol("WM_DELETE_WINDOW", self._on_closing) # 窗口关闭事件
        elif hasattr(self.master, 'winfo_toplevel'):
            # 如果master是Frame等组件，获取根窗口
            root = self.master.winfo_toplevel()
            if hasattr(root, 'protocol'):
                root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _compile_regex(self):
        """
        预编译常用正则表达式
        """
        self._line_regex = re.compile(r'^.*$', re.MULTILINE)
    
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
                if task['type'] == 'full':
                    tokens = self._process_full_highlight(task['text'])
                    # 将结果发布到主线程
                    self.after(0, self._apply_highlighting, tokens, task['text'])
                elif task['type'] == 'incremental':
                    tokens = self._process_incremental_highlight(
                        task['text_block'], 
                        task['min_line'], 
                        task['max_line']
                    )
                    # 将结果发布到主线程
                    self.after(0, self._apply_incremental_highlighting, 
                              tokens, task['min_line'])
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
        if self._updating or not self.edit_modified():
            return
            
        # 记录修改的行
        if self.incremental_update:
            insert_pos = self.index(tk.INSERT)
            line_num = int(insert_pos.split('.')[0])
            self._modified_lines.add(line_num)
            # 也标记前后几行，确保上下文正确
            for i in range(-2, 3):
                self._modified_lines.add(line_num + i)
        
        # 使用延迟更新，避免频繁更新
        if self.enable_optimizations and self.delay_update > 0:
            if self._update_timer:
                self.after_cancel(self._update_timer)
            
            # 计算延迟时间（可以根据文件大小动态调整）
            line_count = int(self.index('end-1c').split('.')[0])
            dynamic_delay = min(self.delay_update, max(50, line_count // 100))
            
            self._update_timer = self.after(dynamic_delay, self._queue_highlight_update)
        else:
            self._queue_highlight_update()
        
        self.edit_modified(False)
    
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
        text = self.get('1.0', tk.END)
        line_count = text.count('\n') + 1
        
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
            self._highlight_queue.put({
                'type': 'full',
                'text': text
            })
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
                text_block = self.get(start_pos, end_pos)
                
                self._highlight_queue.put({
                    'type': 'incremental',
                    'text_block': text_block,
                    'min_line': min_line,
                    'max_line': max_line
                })
                
                # 清空修改记录
                self._modified_lines.clear()
            else:
                # 如果没有修改记录，使用全量更新
                self._highlight_queue.put({
                    'type': 'full',
                    'text': text
                })
    
    def _process_full_highlight(self, text):
        """
        在后台线程中处理全量高亮分析
        """
        try:
            # 尝试重新猜测lexer
            if self.lexer_name == 'auto':
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
            if self.lexer_name == 'auto' and not self.lexer:
                # 如果lexer尚未初始化，尝试猜测
                try:
                    self.lexer = guess_lexer(text_block)
                except:
                    # 如果猜测失败，使用Python lexer作为默认
                    self.lexer = get_lexer_by_name('python')
            
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
            for tag in self.tag_names():
                if tag != 'sel':
                    self.tag_remove(tag, '1.0', tk.END)
            
            # 应用新的高亮
            current_pos = '1.0'
            for token_type, value in tokens:
                # 计算结束位置
                end_pos = self.index(f"{current_pos}+{len(value)}c")
                
                # 找到最具体的token类型
                current_token = token_type
                tag_applied = False
                
                while current_token is not None:
                    tag_name = str(current_token)
                    if tag_name in self.tag_names():
                        self.tag_add(tag_name, current_pos, end_pos)
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
            end_pos = self.index(f"{start_pos}+{total_length}c")
            
            for tag in self.tag_names():
                if tag != 'sel':
                    self.tag_remove(tag, start_pos, end_pos)
            
            # 应用新的高亮到该区域
            current_pos = start_pos
            for token_type, value in tokens:
                end_pos = self.index(f"{current_pos}+{len(value)}c")
                
                # 找到最具体的token类型
                current_token = token_type
                tag_applied = False
                
                while current_token is not None:
                    tag_name = str(current_token)
                    if tag_name in self.tag_names():
                        self.tag_add(tag_name, current_pos, end_pos)
                        tag_applied = True
                        break
                    current_token = current_token.parent
                
                current_pos = end_pos
        except Exception as e:
            print(f"应用增量高亮错误: {e}")
            # 增量更新失败时回退到全量更新
            self.after(0, self._queue_highlight_update)
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
            if lexer_name == 'auto':
                self.lexer = None
            else:
                try:
                    self.lexer = get_lexer_by_name(lexer_name)
                except Exception as e:
                    print(f"设置lexer错误: {e}")
                    self.lexer = get_lexer_by_name('python')  # 使用Python作为默认
        
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
                self.style = get_style_by_name('default')  # 使用默认样式
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
    
    def _on_closing(self):
        """
        窗口关闭时的清理工作
        """
        self._stop_event.set()
        if self._worker_thread:
            self._worker_thread.join(timeout=0.5)  # 等待工作线程结束
        self.master.destroy()
    
    def destroy(self):
        """
        销毁组件时清理资源
        """
        self._stop_event.set()
        if self._worker_thread:
            self._worker_thread.join(timeout=0.5)  # 等待工作线程结束
        super().destroy()

# 测试用的简单应用示例
if __name__ == "__main__":
    def create_demo_app():
        """
        创建演示应用
        """
        root = tk.Tk()
        root.title("增强版语法高亮演示")
        root.geometry("1000x600")
        
        # 创建语法高亮文本框
        text_editor = EnhancedSyntaxHighlightText(
            root, 
            lexer_name='python',
            style_name='monokai',
            wrap=tk.NONE
        )
        
        # 显式设置窗口关闭处理程序，确保正确清理资源
        def on_window_closing():
            # 停止语法高亮工作线程
            text_editor._stop_event.set()
            if text_editor._worker_thread:
                text_editor._worker_thread.join(timeout=0.5)
            # 销毁窗口
            root.destroy()
        
        # 设置窗口关闭事件处理
        root.protocol("WM_DELETE_WINDOW", on_window_closing)
        
        # 设置性能选项
        text_editor.set_performance_options(
            enable_optimizations=True,
            delay_update=80,
            incremental_update=True,
            max_lines_for_full_update=3000
        )
        
        text_editor.pack(expand=True, fill=tk.BOTH)
        
        # 添加示例代码
        sample_code = '''import tkinter as tk
from tkinter import ttk
import time

class EnhancedApp:
    """高性能应用示例"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("高性能应用")
        
        # 性能监控
        self.performance_data = {
            'start_time': time.time(),
            'frame_count': 0,
            'last_update': time.time()
        }
        
        # 创建UI
        self._create_ui()
        
        # 启动性能监控
        self._start_performance_monitor()
    
    def _create_ui(self):
        """创建UI界面"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 文本编辑区域
        self.text_area = ttk.Frame(main_frame)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # 性能显示
        self.perf_label = ttk.Label(main_frame, text="性能: 0 FPS")
        self.perf_label.pack(anchor=tk.E)
    
    def _start_performance_monitor(self):
        """启动性能监控"""
        current_time = time.time()
        elapsed = current_time - self.performance_data['last_update']
        
        if elapsed >= 1.0:  # 每秒更新一次
            fps = self.performance_data['frame_count'] / elapsed
            self.perf_label.config(text=f"性能: {fps:.1f} FPS")
            self.performance_data['frame_count'] = 0
            self.performance_data['last_update'] = current_time
        
        self.performance_data['frame_count'] += 1
        self.root.after(16, self._start_performance_monitor)  # ~60 FPS

if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedApp(root)
    root.mainloop()'''
        
        text_editor.insert('1.0', sample_code)
        text_editor._queue_highlight_update()
        
        # 创建简单的菜单
        menu_bar = tk.Menu(root)
        
        # 语言菜单
        lang_menu = tk.Menu(menu_bar, tearoff=0)
        languages = [
            ('Python', 'python'),
            ('JavaScript', 'javascript'),
            ('HTML', 'html'),
            ('CSS', 'css'),
            ('Java', 'java'),
            ('C++', 'cpp'),
            ('自动检测', 'auto')
        ]
        for lang_name, lang_code in languages:
            lang_menu.add_command(
                label=lang_name, 
                command=lambda code=lang_code: text_editor.set_lexer(code)
            )
        menu_bar.add_cascade(label="语言", menu=lang_menu)
        
        # 样式菜单
        style_menu = tk.Menu(menu_bar, tearoff=0)
        styles = [
            ('默认', 'default'),
            ('单色', 'monokai'),
            ('友好', 'friendly'),
            ('色彩丰富', 'colorful'),
            ('murphy', 'murphy'),
            ('tango', 'tango')
        ]
        for style_name, style_code in styles:
            style_menu.add_command(
                label=style_name, 
                command=lambda code=style_code: text_editor.set_style(code)
            )
        menu_bar.add_cascade(label="样式", menu=style_menu)
        
        root.config(menu=menu_bar)
        
        return root
    
    root = create_demo_app()
    root.mainloop()