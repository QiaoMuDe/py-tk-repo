#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
代码片段管理器模块
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
from config.config_manager import config_manager


class CodeSnippetManager:
    """代码片段管理器类"""
    
    def __init__(self, parent=None):
        """
        初始化代码片段管理器
        
        Args:
            parent: 父窗口对象
        """
        self.parent = parent
        self.selected_snippet = None
        
        # 获取组件字体配置
        self.font_name = config_manager.get("components.font", "Microsoft YaHei UI")
        self.font_size = config_manager.get("components.font_size", 13)
        self.font_bold = config_manager.get("components.font_bold", False)
        self.font_bold = self.font_bold if self.font_bold else "normal"
        
        # 创建主窗口
        self.create_window()
        
        # 创建UI组件
        self.create_widgets()
        
        # 加载示例数据
        self.load_sample_data()
    
    def create_window(self):
        """创建主窗口"""
        # 创建子窗口
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("代码片段管理器")
        self.window.transient(self.parent)
        self.window.grab_set()
            
        
        # 设置窗口居中
        self.window.update_idletasks()
        width = 1200
        height = 700
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        
        # 绑定关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """创建UI组件"""
        # 创建主框架
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 创建左右分栏
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side="left", fill="both", expand=False, padx=(0, 5))
        left_frame.pack_propagate(False)
        left_frame.configure(width=300)
        
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # 左侧面板 - 分类和片段列表
        self.create_left_panel(left_frame)
        
        # 右侧面板 - 片段详情
        self.create_right_panel(right_frame)
        
        # 底部按钮栏
        self.create_bottom_buttons(main_frame)
    
    def create_left_panel(self, parent):
        """创建左侧面板"""
        # 分类框架
        category_frame = ctk.CTkFrame(parent)
        category_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        category_label = ctk.CTkLabel(
            category_frame,
            text="分类",
            font=ctk.CTkFont(size=self.font_size, weight="bold", family=self.font_name)
        )
        category_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # 分类下拉框
        self.category_var = tk.StringVar(value="Python")
        self.category_combobox = ctk.CTkComboBox(
            category_frame,
            variable=self.category_var,
            values=["Python", "JavaScript", "HTML/CSS", "SQL", "Shell", "其他"],
            command=self.on_category_change,
            font=ctk.CTkFont(size=self.font_size-1, family=self.font_name)
        )
        self.category_combobox.pack(fill="x", padx=10, pady=(0, 10))
        
        # 搜索框
        search_frame = ctk.CTkFrame(parent)
        search_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search_change)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="搜索代码片段...",
            textvariable=self.search_var,
            font=ctk.CTkFont(size=self.font_size-1, family=self.font_name)
        )
        self.search_entry.pack(fill="x", padx=10, pady=10)
        
        # 片段列表
        list_frame = ctk.CTkFrame(parent)
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        list_label = ctk.CTkLabel(
            list_frame,
            text="代码片段",
            font=ctk.CTkFont(size=self.font_size, weight="bold", family=self.font_name)
        )
        list_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # 创建滚动框架
        self.list_scroll_frame = ctk.CTkScrollableFrame(
            list_frame,
            height=300
        )
        self.list_scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # 片段列表将动态添加到这里
    
    def create_right_panel(self, parent):
        """创建右侧面板"""
        # 片段详情框架
        detail_frame = ctk.CTkFrame(parent)
        detail_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 标题输入
        title_label = ctk.CTkLabel(
            detail_frame,
            text="标题",
            font=ctk.CTkFont(size=self.font_size, weight="bold", family=self.font_name)
        )
        title_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.title_entry = ctk.CTkEntry(
            detail_frame,
            placeholder_text="输入代码片段标题...",
            font=ctk.CTkFont(size=self.font_size-1, family=self.font_name)
        )
        self.title_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # 描述输入
        desc_label = ctk.CTkLabel(
            detail_frame,
            text="描述",
            font=ctk.CTkFont(size=self.font_size, weight="bold", family=self.font_name)
        )
        desc_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        self.desc_textbox = ctk.CTkTextbox(
            detail_frame,
            height=60,
            font=ctk.CTkFont(size=self.font_size-1, family=self.font_name)
        )
        self.desc_textbox.pack(fill="x", padx=10, pady=(0, 10))
        
        # 代码输入
        code_label = ctk.CTkLabel(
            detail_frame,
            text="代码",
            font=ctk.CTkFont(size=self.font_size, weight="bold", family=self.font_name)
        )
        code_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        # 代码文本框框架
        code_text_frame = ctk.CTkFrame(detail_frame)
        code_text_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.code_textbox = ctk.CTkTextbox(
            code_text_frame,
            font=ctk.CTkFont(family="Consolas", size=self.font_size-1)
        )
        self.code_textbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 标签输入
        tags_label = ctk.CTkLabel(
            detail_frame,
            text="标签",
            font=ctk.CTkFont(size=self.font_size, weight="bold", family=self.font_name)
        )
        tags_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        self.tags_entry = ctk.CTkEntry(
            detail_frame,
            placeholder_text="输入标签，用逗号分隔...",
            font=ctk.CTkFont(size=self.font_size-1, family=self.font_name)
        )
        self.tags_entry.pack(fill="x", padx=10, pady=(0, 10))
    
    def create_bottom_buttons(self, parent):
        """创建底部按钮"""
        button_frame = ctk.CTkFrame(parent)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # 左侧按钮
        left_button_frame = ctk.CTkFrame(button_frame)
        left_button_frame.pack(side="left", fill="x", expand=True)
        
        self.new_button = ctk.CTkButton(
            left_button_frame,
            text="新建",
            command=self.on_new_snippet,
            width=80,
            font=ctk.CTkFont(size=self.font_size-1, family=self.font_name)
        )
        self.new_button.pack(side="left", padx=(10, 5), pady=10)
        
        self.save_button = ctk.CTkButton(
            left_button_frame,
            text="保存",
            command=self.on_save_snippet,
            width=80,
            font=ctk.CTkFont(size=self.font_size-1, family=self.font_name)
        )
        self.save_button.pack(side="left", padx=5, pady=10)
        
        self.delete_button = ctk.CTkButton(
            left_button_frame,
            text="删除",
            command=self.on_delete_snippet,
            width=80,
            font=ctk.CTkFont(size=self.font_size-1, family=self.font_name)
        )
        self.delete_button.pack(side="left", padx=5, pady=10)
        
        # 右侧按钮
        right_button_frame = ctk.CTkFrame(button_frame)
        right_button_frame.pack(side="right")
        
        self.import_button = ctk.CTkButton(
            right_button_frame,
            text="导入",
            command=self.on_import_snippets,
            width=80,
            font=ctk.CTkFont(size=self.font_size-1, family=self.font_name)
        )
        self.import_button.pack(side="left", padx=5, pady=10)
        
        self.export_button = ctk.CTkButton(
            right_button_frame,
            text="导出",
            command=self.on_export_snippets,
            width=80,
            font=ctk.CTkFont(size=self.font_size-1, family=self.font_name)
        )
        self.export_button.pack(side="left", padx=5, pady=10)
        
        self.copy_button = ctk.CTkButton(
            right_button_frame,
            text="复制代码",
            command=self.on_copy_code,
            width=80,
            font=ctk.CTkFont(size=self.font_size-1, family=self.font_name)
        )
        self.copy_button.pack(side="left", padx=(5, 10), pady=10)
    
    def load_sample_data(self):
        """加载示例数据"""
        # 示例数据
        self.snippets = {
            "Python": [
                {
                    "id": 1,
                    "title": "快速排序",
                    "description": "Python实现的快速排序算法",
                    "code": "def quick_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quick_sort(left) + middle + quick_sort(right)",
                    "tags": ["算法", "排序", "递归"]
                },
                {
                    "id": 2,
                    "title": "文件读取",
                    "description": "安全地读取文件内容",
                    "code": "def read_file(file_path):\n    try:\n        with open(file_path, 'r', encoding='utf-8') as f:\n            return f.read()\n    except FileNotFoundError:\n        print(f\"文件 {file_path} 不存在\")\n        return None\n    except Exception as e:\n        print(f\"读取文件时出错: {e}\")\n        return None",
                    "tags": ["文件操作", "异常处理"]
                }
            ],
            "JavaScript": [
                {
                    "id": 3,
                    "title": "防抖函数",
                    "description": "JavaScript实现的防抖函数",
                    "code": "function debounce(func, wait) {\n    let timeout;\n    return function() {\n        const context = this;\n        const args = arguments;\n        clearTimeout(timeout);\n        timeout = setTimeout(() => {\n            func.apply(context, args);\n        }, wait);\n    };\n}",
                    "tags": ["函数", "性能优化", "事件处理"]
                }
            ]
        }
        
        # 更新列表显示
        self.update_snippet_list()
    
    def update_snippet_list(self):
        """更新片段列表显示"""
        # 清空当前列表
        for widget in self.list_scroll_frame.winfo_children():
            widget.destroy()
        
        # 获取当前分类
        category = self.category_var.get()
        search_term = self.search_var.get().lower()
        
        # 获取该分类下的片段
        snippets = self.snippets.get(category, [])
        
        # 如果有搜索词，过滤片段
        if search_term:
            snippets = [
                s for s in snippets
                if search_term in s["title"].lower() or 
                   search_term in s["description"].lower() or
                   any(search_term in tag.lower() for tag in s["tags"])
            ]
        
        # 添加片段到列表
        for snippet in snippets:
            item_frame = ctk.CTkFrame(self.list_scroll_frame)
            item_frame.pack(fill="x", padx=5, pady=3)
            
            # 片段标题
            title_label = ctk.CTkLabel(
                item_frame,
                text=snippet["title"],
                font=ctk.CTkFont(size=self.font_size-1, weight="bold", family=self.font_name)
            )
            title_label.pack(anchor="w", padx=10, pady=(5, 2))
            
            # 片段描述
            desc_label = ctk.CTkLabel(
                item_frame,
                text=snippet["description"],
                font=ctk.CTkFont(size=self.font_size-2, family=self.font_name),
                text_color="gray"
            )
            desc_label.pack(anchor="w", padx=10, pady=(0, 2))
            
            # 片段标签
            tags_text = ", ".join(snippet["tags"])
            tags_label = ctk.CTkLabel(
                item_frame,
                text=tags_text,
                font=ctk.CTkFont(size=self.font_size-2, family=self.font_name),
                text_color="gray"
            )
            tags_label.pack(anchor="w", padx=10, pady=(0, 5))
            
            # 绑定点击事件
            def on_click(event, s=snippet):
                self.on_snippet_select(s)
            
            item_frame.bind("<Button-1>", on_click)
            title_label.bind("<Button-1>", on_click)
            desc_label.bind("<Button-1>", on_click)
            tags_label.bind("<Button-1>", on_click)
            
            # 设置鼠标悬停样式
            for widget in [item_frame, title_label, desc_label, tags_label]:
                widget.bind("<Enter>", lambda e, f=item_frame: f.configure(fg_color=("gray70", "gray30")))
                widget.bind("<Leave>", lambda e, f=item_frame: f.configure(fg_color=("gray90", "gray20")))
    
    def on_category_change(self, choice):
        """分类改变时的回调函数"""
        self.update_snippet_list()
    
    def on_search_change(self, *args):
        """搜索内容改变时的回调函数"""
        self.update_snippet_list()
    
    def on_snippet_select(self, snippet):
        """选择片段时的回调函数"""
        self.selected_snippet = snippet
        
        # 更新右侧面板
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, snippet["title"])
        
        self.desc_textbox.delete("1.0", "end")
        self.desc_textbox.insert("1.0", snippet["description"])
        
        self.code_textbox.delete("1.0", "end")
        self.code_textbox.insert("1.0", snippet["code"])
        
        self.tags_entry.delete(0, "end")
        self.tags_entry.insert(0, ", ".join(snippet["tags"]))
    
    def on_new_snippet(self):
        """新建片段按钮的回调函数"""
        self.selected_snippet = None
        
        # 清空右侧面板
        self.title_entry.delete(0, "end")
        self.desc_textbox.delete("1.0", "end")
        self.code_textbox.delete("1.0", "end")
        self.tags_entry.delete(0, "end")
        
        # 聚焦到标题输入框
        self.title_entry.focus_set()
    
    def on_save_snippet(self):
        """保存片段按钮的回调函数"""
        title = self.title_entry.get().strip()
        description = self.desc_textbox.get("1.0", "end").strip()
        code = self.code_textbox.get("1.0", "end").strip()
        tags_text = self.tags_entry.get().strip()
        
        if not title:
            messagebox.showwarning("警告", "请输入代码片段标题")
            return
        
        if not code:
            messagebox.showwarning("警告", "请输入代码内容")
            return
        
        # 处理标签
        tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]
        
        category = self.category_var.get()
        
        # 如果是编辑现有片段
        if self.selected_snippet:
            # 找到并更新片段
            for i, snippet in enumerate(self.snippets[category]):
                if snippet["id"] == self.selected_snippet["id"]:
                    self.snippets[category][i] = {
                        "id": self.selected_snippet["id"],
                        "title": title,
                        "description": description,
                        "code": code,
                        "tags": tags
                    }
                    break
            messagebox.showinfo("成功", "代码片段已更新")
        else:
            # 创建新片段
            new_id = max([s["id"] for s in self.snippets.get(category, [])], default=0) + 1
            new_snippet = {
                "id": new_id,
                "title": title,
                "description": description,
                "code": code,
                "tags": tags
            }
            
            # 确保分类存在
            if category not in self.snippets:
                self.snippets[category] = []
            
            # 添加新片段
            self.snippets[category].append(new_snippet)
            messagebox.showinfo("成功", "代码片段已保存")
        
        # 更新列表显示
        self.update_snippet_list()
    
    def on_delete_snippet(self):
        """删除片段按钮的回调函数"""
        if not self.selected_snippet:
            messagebox.showwarning("警告", "请先选择要删除的代码片段")
            return
        
        if messagebox.askyesno("确认", "确定要删除这个代码片段吗？"):
            category = self.category_var.get()
            
            # 找到并删除片段
            self.snippets[category] = [
                s for s in self.snippets[category]
                if s["id"] != self.selected_snippet["id"]
            ]
            
            # 清空右侧面板
            self.on_new_snippet()
            
            # 更新列表显示
            self.update_snippet_list()
            
            messagebox.showinfo("成功", "代码片段已删除")
    
    def on_import_snippets(self):
        """导入片段按钮的回调函数"""
        file_path = filedialog.askopenfilename(
            title="选择要导入的文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                # 这里应该实现实际的导入逻辑
                messagebox.showinfo("提示", f"将从 {file_path} 导入代码片段")
            except Exception as e:
                messagebox.showerror("错误", f"导入失败: {str(e)}")
    
    def on_export_snippets(self):
        """导出片段按钮的回调函数"""
        file_path = filedialog.asksaveasfilename(
            title="选择保存位置",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                # 这里应该实现实际的导出逻辑
                messagebox.showinfo("提示", f"将导出代码片段到 {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")
    
    def on_copy_code(self):
        """复制代码按钮的回调函数"""
        code = self.code_textbox.get("1.0", "end").strip()
        
        if not code:
            messagebox.showwarning("警告", "没有可复制的代码")
            return
        
        try:
            self.window.clipboard_clear()
            self.window.clipboard_append(code)
            messagebox.showinfo("成功", "代码已复制到剪贴板")
        except Exception as e:
            messagebox.showerror("错误", f"复制失败: {str(e)}")
    
    def on_closing(self):
        """窗口关闭事件"""
        if self.parent is None:
            self.window.quit()
        else:
            self.window.destroy()


def show_code_snippet_manager(parent):
    """
    显示代码片段管理器窗口
    
    参数:
        parent: 父窗口实例
    """
    # 创建代码片段管理器窗口
    manager = CodeSnippetManager(parent)
    
    # 显示窗口
    manager.window.grab_set()  # 使窗口模态化
    manager.window.wait_window()  # 等待窗口关闭


def main():
    """测试函数"""
    # 设置外观模式
    ctk.set_appearance_mode(config_manager.get("app.theme_mode", "light"))
    
    # 创建应用
    app = CodeSnippetManager()
    
    # 运行主循环
    app.window.mainloop()


if __name__ == "__main__":
    main()