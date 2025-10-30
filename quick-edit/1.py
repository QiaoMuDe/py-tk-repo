"""
方案A：推荐方案 - 直接集成Pygments和tkinter Text组件
修复了样式处理的bug
"""

import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import pygments
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.styles import get_style_by_name
from pygments.token import Token
from pygments.style import StyleMeta
import re

class SyntaxHighlightText(scrolledtext.ScrolledText):
    def __init__(self, master=None, lexer_name='python', style_name='default', **kwargs):
        super().__init__(master, **kwargs)
        
        # Pygments相关设置
        self.lexer_name = lexer_name
        self.style_name = style_name
        self.lexer = get_lexer_by_name(lexer_name)
        self.style = get_style_by_name(style_name)
        
        # 初始化tag样式
        self._init_tags()
        
        # 绑定事件
        self.bind('<KeyRelease>', self._on_text_change)
        self.bind('<FocusIn>', self._on_text_change)
        self.bind('<<Modified>>', self._on_text_change)
        
        # 标记是否正在更新，避免递归调用
        self._updating = False
        
    def _init_tags(self):
        """初始化所有可能的token样式"""
        # 清除所有现有tag
        for tag in self.tag_names():
            self.tag_delete(tag)
        
        # 设置默认字体
        self.config(font=('Consolas', 10))
        
        # 为每种token类型创建tag
        # 首先获取所有token类型和对应的样式
        token_styles = {}
        
        # 遍历样式类的所有属性
        for attr_name in dir(self.style):
            if not attr_name.startswith('_'):
                attr_value = getattr(self.style, attr_name)
                if isinstance(attr_value, tuple) and len(attr_value) >= 2:
                    # 检查是否是token样式定义
                    token_type = None
                    style_def = None
                    
                    # 处理不同的样式定义格式
                    if isinstance(attr_value[0], Token):
                        token_type = attr_value[0]
                        style_def = attr_value[1]
                    elif isinstance(attr_value, (list, tuple)) and len(attr_value) >= 2:
                        # 有些样式可能使用不同的格式
                        try:
                            if isinstance(attr_value[0], Token):
                                token_type = attr_value[0]
                                style_def = attr_value[1]
                        except:
                            pass
                    
                    if token_type and style_def:
                        token_styles[token_type] = style_def
        
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
                # 处理字符串格式的样式定义
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
                # 处理字典格式的样式定义
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
    
    def _on_text_change(self, event=None):
        """文本改变时重新高亮"""
        if self._updating or not self.edit_modified():
            return
            
        self._updating = True
        try:
            self._highlight_syntax()
            self.edit_modified(False)
        finally:
            self._updating = False
    
    def _highlight_syntax(self):
        """执行语法高亮"""
        # 获取所有文本
        text = self.get('1.0', tk.END)
        
        if not text.strip():
            return
            
        try:
            # 尝试重新猜测lexer（对于不同类型的文件）
            if self.lexer_name == 'auto':
                self.lexer = guess_lexer(text)
            
            # 使用Pygments进行语法分析
            tokens = pygments.lex(text, self.lexer)
            
            # 清除所有现有高亮
            for tag in self.tag_names():
                if tag != 'sel':  # 保留选中样式
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
            print(f"高亮错误: {e}")
            # 出错时使用默认样式重新初始化
            self._init_tags()
    
    def set_lexer(self, lexer_name):
        """设置语法解析器"""
        self.lexer_name = lexer_name
        if lexer_name == 'auto':
            self.lexer = None
        else:
            self.lexer = get_lexer_by_name(lexer_name)
        self._highlight_syntax()
    
    def set_style(self, style_name):
        """设置高亮样式"""
        self.style_name = style_name
        self.style = get_style_by_name(style_name)
        self._init_tags()
        self._highlight_syntax()

class CodeEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("高级代码编辑器 - 方案A（修复版）")
        self.root.geometry("1000x600")
        
        # 创建菜单栏
        self._create_menu()
        
        # 创建主编辑区域
        self.text_editor = SyntaxHighlightText(
            root, 
            lexer_name='python',
            style_name='monokai',
            wrap=tk.NONE
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
        
        # 帮助菜单
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="关于", command=self._show_about)
        menu_bar.add_cascade(label="帮助", menu=help_menu)
        
        self.root.config(menu=menu_bar)
    
    def _add_sample_code(self):
        """添加示例Python代码"""
        sample_code = '''import tkinter as tk
from tkinter import ttk

class HelloApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hello World App")
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建标签
        self.label = ttk.Label(self.main_frame, text="Hello, Tkinter!")
        self.label.grid(row=0, column=0, padx=5, pady=5)
        
        # 创建按钮
        self.button = ttk.Button(
            self.main_frame, 
            text="点击我", 
            command=self.on_button_click
        )
        self.button.grid(row=1, column=0, padx=5, pady=5)
        
        # 响应式布局
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
    
    def on_button_click(self):
        """按钮点击事件"""
        self.label.config(text="按钮被点击了！")

if __name__ == "__main__":
    root = tk.Tk()
    app = HelloApp(root)
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
        about_info = """高级代码编辑器 - 方案A（修复版）
基于tkinter和Pygments的语法高亮编辑器

功能特点：
- 支持多种编程语言语法高亮
- 多种主题样式选择
- 完整的编辑功能
- 文件操作（新建、打开、保存）
- 自动语言检测

使用说明：
- 从菜单栏选择编程语言和样式
- 支持常规的编辑操作
- 可以打开和保存各种代码文件
"""
        messagebox.showinfo("关于", about_info)

def main():
    root = tk.Tk()
    app = CodeEditorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()