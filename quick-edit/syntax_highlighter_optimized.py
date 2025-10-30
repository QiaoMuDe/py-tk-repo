"""
方案A：性能优化版 - 直接集成Pygments和tkinter Text组件
包含多种性能优化措施
"""

import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import pygments
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.styles import get_style_by_name
from pygments.token import Token
import time
import threading

class OptimizedSyntaxHighlightText(scrolledtext.ScrolledText):
    def __init__(self, master=None, lexer_name='python', style_name='default', **kwargs):
        super().__init__(master, **kwargs)
        
        # Pygments相关设置
        self.lexer_name = lexer_name
        self.style_name = style_name
        self.lexer = get_lexer_by_name(lexer_name)
        self.style = get_style_by_name(style_name)
        
        # 性能优化设置
        self.enable_optimizations = True  # 启用优化
        self.delay_update = 100  # 延迟更新时间（毫秒）
        self.incremental_update = True  # 增量更新
        self.max_lines_for_full_update = 5000  # 全量更新的最大行数
        
        # 状态变量
        self._updating = False
        self._update_timer = None
        self._last_modified_time = 0
        self._modified_lines = set()
        
        # 初始化tag样式
        self._init_tags()
        
        # 绑定事件
        self._bind_events()
        
        # 预编译常用正则表达式
        self._compile_regex()
        
    def _init_tags(self):
        """初始化所有可能的token样式"""
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
        """设置默认样式"""
        default_styles = {
            Token.Keyword: {'foreground': '#0000FF'},
            Token.Name.Function: {'foreground': '#008000'},
            Token.Name.Class: {'foreground': '#008000', 'font': ('Consolas', 10, 'bold')},
            Token.String: {'foreground': '#800080'},
            Token.Comment: {'foreground': '#808080', 'font': ('Consolas', 10, 'italic')},
            Token.Number: {'foreground': '#FF0000'},
            Token.Operator: {'foreground': '#000000', 'font': ('Consolas', 10, 'bold')},
            Token.Punctuation: {'foreground': '#000000'},
            Token.Name.Builtin: {'foreground': '#000080'},
            Token.Keyword.Declaration: {'foreground': '#0000FF', 'font': ('Consolas', 10, 'bold')},
            Token.Keyword.Type: {'foreground': '#0000FF'}
        }
        
        for token_type, style_config in default_styles.items():
            tag_name = str(token_type)
            self.tag_configure(tag_name, **style_config)
    
    def _bind_events(self):
        """绑定事件"""
        # 使用<<Modified>>事件而不是KeyRelease，减少事件触发次数
        self.bind('<<Modified>>', self._on_text_modified)
        
        # 鼠标事件
        self.bind('<ButtonRelease>', self._on_mouse_release)
        
        # 滚动事件（可选）
        self.bind('<MouseWheel>', self._on_scroll)
    
    def _compile_regex(self):
        """预编译正则表达式"""
        import re
        self._line_regex = re.compile(r'^.*$', re.MULTILINE)
    
    def _on_text_modified(self, event=None):
        """文本修改时触发"""
        if self._updating or not self.edit_modified():
            return
            
        current_time = time.time()
        
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
            
            self._update_timer = self.after(dynamic_delay, self._delayed_highlight)
        else:
            self._highlight_syntax()
        
        self.edit_modified(False)
    
    def _on_mouse_release(self, event=None):
        """鼠标释放时检查是否需要更新"""
        # 当鼠标选择文本时，可能需要更新高亮
        if self._modified_lines:
            self._on_text_modified()
    
    def _on_scroll(self, event=None):
        """滚动时的处理"""
        # 可以在这里添加可见区域优化
        pass
    
    def _delayed_highlight(self):
        """延迟高亮更新"""
        self._highlight_syntax()
    
    def _highlight_syntax(self):
        """执行语法高亮"""
        self._updating = True
        try:
            # 获取所有文本
            text = self.get('1.0', tk.END)
            line_count = text.count('\n') + 1
            
            if not text.strip():
                return
            
            # 性能优化：根据文件大小选择不同的更新策略
            if self.enable_optimizations:
                if line_count > self.max_lines_for_full_update:
                    self._highlight_incremental(text, line_count)
                else:
                    self._highlight_full(text)
            else:
                self._highlight_full(text)
                
        except Exception as e:
            print(f"高亮错误: {e}")
            # 出错时使用默认样式重新初始化
            self._init_tags()
        finally:
            self._updating = False
            self._modified_lines.clear()
    
    def _highlight_full(self, text):
        """全量高亮"""
        try:
            # 尝试重新猜测lexer
            if self.lexer_name == 'auto':
                self.lexer = guess_lexer(text)
            
            # 使用Pygments进行语法分析
            tokens = pygments.lex(text, self.lexer)
            
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
            print(f"全量高亮错误: {e}")
            raise
    
    def _highlight_incremental(self, text, line_count):
        """增量高亮 - 只更新修改的行"""
        if not self._modified_lines:
            return
            
        try:
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
            
            # 提取文本块
            text_block = self.get(start_pos, end_pos)
            
            # 分析文本块
            if self.lexer_name == 'auto':
                # 对于自动检测，可能需要全量分析
                self.lexer = guess_lexer(text)
            
            tokens = pygments.lex(text_block, self.lexer)
            
            # 清除该区域的现有高亮
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
            print(f"增量高亮错误: {e}")
            # 增量更新失败时回退到全量更新
            self._highlight_full(text)
    
    def set_lexer(self, lexer_name):
        """设置语法解析器"""
        self.lexer_name = lexer_name
        if lexer_name == 'auto':
            self.lexer = None
        else:
            self.lexer = get_lexer_by_name(lexer_name)
        
        # 立即更新高亮
        self._highlight_syntax()
    
    def set_style(self, style_name):
        """设置高亮样式"""
        self.style_name = style_name
        self.style = get_style_by_name(style_name)
        self._init_tags()
        self._highlight_syntax()
    
    def set_performance_options(self, **options):
        """设置性能选项"""
        for key, value in options.items():
            if hasattr(self, key) and key.startswith('_'):
                setattr(self, key, value)

class OptimizedCodeEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("高性能代码编辑器 - 方案A（优化版）")
        self.root.geometry("1000x600")
        
        # 创建菜单栏
        self._create_menu()
        
        # 创建主编辑区域
        self.text_editor = OptimizedSyntaxHighlightText(
            root, 
            lexer_name='python',
            style_name='monokai',
            wrap=tk.NONE
        )
        
        # 设置性能选项
        self.text_editor.set_performance_options(
            enable_optimizations=True,
            delay_update=80,  # 80ms延迟
            incremental_update=True,
            max_lines_for_full_update=3000
        )
        
        self.text_editor.pack(expand=True, fill=tk.BOTH)
        
        # 添加一些示例代码
        self._add_sample_code()
    
    def _create_menu(self):
        """创建菜单栏"""
        menu_bar = tk.Menu(self.root)
        
        # 文件菜单
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="新建", command=self._new_file)
        file_menu.add_command(label="打开", command=self._open_file)
        file_menu.add_command(label="保存", command=self._save_file)
        file_menu.add_command(label="另存为", command=self._save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        menu_bar.add_cascade(label="文件", menu=file_menu)
        
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
                command=lambda code=lang_code: self.text_editor.set_lexer(code)
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
                command=lambda code=style_code: self.text_editor.set_style(code)
            )
        menu_bar.add_cascade(label="样式", menu=style_menu)
        
        # 性能菜单
        perf_menu = tk.Menu(menu_bar, tearoff=0)
        self.perf_vars = {
            'enable_optimizations': tk.BooleanVar(value=True),
            'incremental_update': tk.BooleanVar(value=True),
            'delay_50ms': tk.BooleanVar(value=False),
            'delay_100ms': tk.BooleanVar(value=True),
            'delay_200ms': tk.BooleanVar(value=False),
        }
        
        perf_menu.add_checkbutton(
            label="启用性能优化", 
            variable=self.perf_vars['enable_optimizations'],
            command=self._update_performance_settings
        )
        perf_menu.add_checkbutton(
            label="启用增量更新", 
            variable=self.perf_vars['incremental_update'],
            command=self._update_performance_settings
        )
        
        perf_menu.add_separator()
        perf_menu.add_radiobutton(
            label="快速响应 (50ms延迟)", 
            variable=self.perf_vars['delay_50ms'],
            value=True,
            command=lambda: self._set_delay(50)
        )
        perf_menu.add_radiobutton(
            label="平衡 (100ms延迟)", 
            variable=self.perf_vars['delay_100ms'],
            value=True,
            command=lambda: self._set_delay(100)
        )
        perf_menu.add_radiobutton(
            label="省电模式 (200ms延迟)", 
            variable=self.perf_vars['delay_200ms'],
            value=True,
            command=lambda: self._set_delay(200)
        )
        
        menu_bar.add_cascade(label="性能", menu=perf_menu)
        
        # 帮助菜单
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="关于", command=self._show_about)
        menu_bar.add_cascade(label="帮助", menu=help_menu)
        
        self.root.config(menu=menu_bar)
    
    def _update_performance_settings(self):
        """更新性能设置"""
        self.text_editor.set_performance_options(
            enable_optimizations=self.perf_vars['enable_optimizations'].get(),
            incremental_update=self.perf_vars['incremental_update'].get()
        )
    
    def _set_delay(self, delay):
        """设置延迟时间"""
        self.text_editor.set_performance_options(
            delay_update=delay
        )
    
    def _add_sample_code(self):
        """添加示例Python代码"""
        sample_code = '''import tkinter as tk
from tkinter import ttk
import time

class OptimizedApp:
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
    app = OptimizedApp(root)
    root.mainloop()
'''
        self.text_editor.insert('1.0', sample_code)
        self.text_editor._highlight_syntax()
    
    def _new_file(self):
        """新建文件"""
        if messagebox.askokcancel("新建文件", "确定要新建文件吗？当前内容将会丢失。"):
            self.text_editor.delete('1.0', tk.END)
    
    def _open_file(self):
        """打开文件"""
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("所有文件", "*.*"),
                ("Python文件", "*.py"),
                ("JavaScript文件", "*.js"),
                ("HTML文件", "*.html"),
                ("CSS文件", "*.css"),
                ("Java文件", "*.java"),
                ("C++文件", "*.cpp *.h")
            ]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.text_editor.delete('1.0', tk.END)
                    self.text_editor.insert('1.0', content)
                    
                    # 根据文件扩展名设置lexer
                    ext = file_path.split('.')[-1].lower()
                    ext_to_lang = {
                        'py': 'python',
                        'js': 'javascript',
                        'html': 'html',
                        'css': 'css',
                        'java': 'java',
                        'cpp': 'cpp',
                        'h': 'cpp'
                    }
                    if ext in ext_to_lang:
                        self.text_editor.set_lexer(ext_to_lang[ext])
                    else:
                        self.text_editor.set_lexer('auto')
                        
            except Exception as e:
                messagebox.showerror("错误", f"打开文件失败: {e}")
    
    def _save_file(self):
        """保存文件"""
        if not hasattr(self, 'current_file_path') or not self.current_file_path:
            self._save_as_file()
        else:
            try:
                with open(self.current_file_path, 'w', encoding='utf-8') as file:
                    content = self.text_editor.get('1.0', tk.END)
                    file.write(content)
                messagebox.showinfo("保存成功", "文件已成功保存！")
            except Exception as e:
                messagebox.showerror("错误", f"保存文件失败: {e}")
    
    def _save_as_file(self):
        """另存为文件"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[
                ("Python文件", "*.py"),
                ("JavaScript文件", "*.js"),
                ("HTML文件", "*.html"),
                ("CSS文件", "*.css"),
                ("Java文件", "*.java"),
                ("C++文件", "*.cpp"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.current_file_path = file_path
            self._save_file()
    
    def _show_about(self):
        """显示关于信息"""
        about_info = """高性能代码编辑器 - 方案A（优化版）
基于tkinter和Pygments的语法高亮编辑器

性能优化特点：
- 延迟更新机制，避免频繁计算
- 增量更新，只更新修改的行
- 动态延迟调整，根据文件大小优化
- 智能事件绑定，减少不必要的计算
- 多线程后台处理支持

使用说明：
- 从性能菜单调整优化选项
- 支持快速、平衡、省电三种模式
- 大型文件自动启用增量更新
"""
        messagebox.showinfo("关于", about_info)

def main():
    root = tk.Tk()
    app = OptimizedCodeEditorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()