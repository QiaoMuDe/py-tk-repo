import tkinter as tk
from tkinter import ttk

class ThemeManager:
    """主题管理器类"""

    # 预定义的主题
    THEMES = {
        "light": {
            "name": "浅色主题", # 主题名称
            "text_bg": "white",  # 文本区域背景色
            "text_fg": "black",  # 文本区域前景色
            "text_insert_bg": "black",  # 插入点背景色
            "text_select_bg": "lightblue",  # 选择区域背景色
            "text_select_fg": "black",  # 选择区域前景色
            "line_numbers_bg": "#f0f0f0",  # 行号区域背景色
            "line_numbers_fg": "gray",  # 行号区域前景色
            "found_bg": "yellow",  # 搜索结果背景色
            "found_fg": "black",  # 搜索结果前景色 
            "current_match_bg": "#ff9900",  # 当前匹配项背景色
            "current_match_fg": "black",  # 当前匹配项前景色
            "cursor_line_bg": "yellow",  # 光标所在行背景色
            "hover_line_bg": "#e0e0e0",  # 悬停行背景色
            "menu_bg": "#f0f0f0",  # 菜单背景色
            "menu_fg": "black",  # 菜单前景色
            "menu_active_bg": "lightblue",  # 激活菜单背景色
            "menu_active_fg": "black",  # 激活菜单前景色
            "toolbar_bg": "#f0f0f0",  # 工具栏背景色
            "toolbar_active_bg": "#d0d0d0",  # 激活工具栏背景色
            "toolbar_pressed_bg": "#b0b0b0",  # 按下工具栏背景色
            "toolbar_button_fg": "black",  # 工具栏按钮前景色
            "statusbar_bg": "#f0f0f0",  # 状态栏背景色
            "statusbar_fg": "black",  # 状态栏前景色
        },
        "dark": {
            "name": "深色主题",
            "text_bg": "#2d2d2d",
            "text_fg": "#ffffff",
            "text_insert_bg": "#ffffff",
            "text_select_bg": "#3a6ea5",
            "text_select_fg": "#ffffff",
            "line_numbers_bg": "#3a3a3a",
            "line_numbers_fg": "#aaaaaa",
            "found_bg": "#ffff00",
            "found_fg": "#000000",
            "current_match_bg": "#ffa500",
            "current_match_fg": "#000000",
            "cursor_line_bg": "#3a3a3a",  # 光标所在行背景色
            "hover_line_bg": "#3a3a3a",  # 悬停行背景色
            "menu_bg": "#3a3a3a",
            "menu_fg": "#ffffff",
            "menu_active_bg": "#094771",
            "menu_active_fg": "#ffffff",
            "toolbar_bg": "#3a3a3a",
            "toolbar_active_bg": "#4a4a4a",
            "toolbar_pressed_bg": "#5a5a5a",
            "toolbar_button_fg": "black",
            "statusbar_bg": "#3a3a3a",
            "statusbar_fg": "#ffffff",
        },
        "blue": {
            "name": "蓝色主题",
            "text_bg": "#f0f8ff",
            "text_fg": "#000080",
            "text_insert_bg": "#000080",
            "text_select_bg": "#87ceeb",
            "text_select_fg": "#000000",
            "line_numbers_bg": "#e1ebf5",
            "line_numbers_fg": "#191970",
            "found_bg": "#ffff99",
            "found_fg": "#000080",
            "current_match_bg": "#ffcc66",
            "current_match_fg": "#000000",
            "cursor_line_bg": "#cce6ff",  # 光标所在行背景色
            "hover_line_bg": "#cce6ff",  # 悬停行背景色
            "menu_bg": "#e1ebf5",
            "menu_fg": "#000080",
            "menu_active_bg": "#4682b4",
            "menu_active_fg": "#ffffff",
            "toolbar_bg": "#e1ebf5",
            "toolbar_active_bg": "#b0c4de",
            "toolbar_pressed_bg": "#708090",
            "toolbar_button_fg": "#000080",
            "statusbar_bg": "#4682b4",
            "statusbar_fg": "#ffffff",
        },
        "parchment": {
            "name": "羊皮卷主题",
            "text_bg": "#f5e9d0",
            "text_fg": "#5a4a3f",
            "text_insert_bg": "#5a4a3f",
            "text_select_bg": "#e0c8a0",
            "text_select_fg": "#5a4a3f",
            "line_numbers_bg": "#e6d5b8",
            "line_numbers_fg": "#8c7a63",
            "found_bg": "#ffd700",
            "found_fg": "#5a4a3f",
            "current_match_bg": "#ff8c00",
            "current_match_fg": "#ffffff",
            "cursor_line_bg": "#e6d5b8",  # 光标所在行背景色
            "hover_line_bg": "#e6d5b8",  # 悬停行背景色
            "menu_bg": "#e6d5b8",
            "menu_fg": "#5a4a3f",
            "menu_active_bg": "#d0b895",
            "menu_active_fg": "#ffffff",
            "toolbar_bg": "#e6d5b8",
            "toolbar_active_bg": "#d0b895",
            "toolbar_pressed_bg": "#c0a885",
            "toolbar_button_fg": "#5a4a3f",
            "statusbar_bg": "#e6d5b8",
            "statusbar_fg": "#5a4a3f",
        },
        "green": {
            "name": "经典绿色",
            "text_bg": "#f0fff0",
            "text_fg": "#006400",
            "text_insert_bg": "#006400",
            "text_select_bg": "#90ee90",
            "text_select_fg": "#000000",
            "line_numbers_bg": "#ccffcc",
            "line_numbers_fg": "#006600",
            "found_bg": "#ffff99",
            "found_fg": "#000000",
            "current_match_bg": "#ffcc66",
            "current_match_fg": "#000000",
            "cursor_line_bg": "#ccffcc",  # 光标所在行背景色
            "hover_line_bg": "#ccffcc",  # 悬停行背景色
            "menu_bg": "#ccffcc",
            "menu_fg": "#006600",
            "menu_active_bg": "#006600",
            "menu_active_fg": "#ffffff",
            "toolbar_bg": "#ccffcc",
            "toolbar_active_bg": "#99cc99",
            "toolbar_pressed_bg": "#669966",
            "toolbar_button_fg": "#006600",
            "statusbar_bg": "#ccffcc",
            "statusbar_fg": "#006600",
        },
        "midnight_purple": {
            "name": "午夜紫主题",
            "text_bg": "#f0e6ff",  # 更浅的紫色背景
            "text_fg": "#330066",  # 深紫色文字
            "text_insert_bg": "#330066",
            "text_select_bg": "#cc99ff",
            "text_select_fg": "#000000",
            "line_numbers_bg": "#e0d6f0",
            "line_numbers_fg": "#6600cc",
            "found_bg": "#ffcc99",
            "found_fg": "#000000",
            "current_match_bg": "#ff9966",
            "current_match_fg": "#000000",
            "cursor_line_bg": "#e0d6f0",  # 光标所在行背景色
            "hover_line_bg": "#e0d6f0",  # 悬停行背景色
            "menu_bg": "#e0d6f0",
            "menu_fg": "#330066",
            "menu_active_bg": "#6600cc",
            "menu_active_fg": "#ffffff",
            "toolbar_bg": "#e0d6f0",
            "toolbar_active_bg": "#cc99ff",
            "toolbar_pressed_bg": "#9966cc",
            "toolbar_button_fg": "#330066",
            "statusbar_bg": "#e0d6f0",
            "statusbar_fg": "#330066",
        },
        "sunset": {
            "name": "日落橙主题",
            "text_bg": "#fff0e1",
            "text_fg": "#d35400",
            "text_insert_bg": "#d35400",
            "text_select_bg": "#f39c12",
            "text_select_fg": "#ffffff",
            "line_numbers_bg": "#f5d1b0",
            "line_numbers_fg": "#e67e22",
            "found_bg": "#f1c40f",
            "found_fg": "#d35400",
            "current_match_bg": "#e67e22",
            "current_match_fg": "#ffffff",
            "cursor_line_bg": "#f5d1b0",  # 光标所在行背景色
            "hover_line_bg": "#f5d1b0",  # 悬停行背景色
            "menu_bg": "#f5d1b0",
            "menu_fg": "#d35400",
            "menu_active_bg": "#e67e22",
            "menu_active_fg": "#ffffff",
            "toolbar_bg": "#f5d1b0",
            "toolbar_active_bg": "#ebbc91",
            "toolbar_pressed_bg": "#e0a87d",
            "toolbar_button_fg": "#d35400",
            "statusbar_bg": "#f5d1b0",
            "statusbar_fg": "#d35400",
        },
    }

    def __init__(self, editor):
        self.editor = editor
        self.current_theme = "light"

    def get_current_theme(self):
        """获取当前主题配置"""
        return self.THEMES.get(self.current_theme, self.THEMES["light"])

    def set_theme(self, theme_name):
        """设置主题"""
        if theme_name in self.THEMES:
            self.current_theme = theme_name
            self.apply_theme()
            return True
        return False

    def apply_theme(self):
        """应用当前主题到所有UI元素"""
        theme = self.get_current_theme()

        # 应用文本区域样式
        self.editor.text_area.config(
            bg=theme["text_bg"],
            fg=theme["text_fg"],
            insertbackground=theme["text_insert_bg"],
            selectbackground=theme["text_select_bg"],
            selectforeground=theme["text_select_fg"],
        )

        # 应用行号区域样式
        if hasattr(self.editor, "line_numbers"):
            self.editor.line_numbers.config(bg=theme["line_numbers_bg"])
            # 更新行号颜色
            self.editor.update_line_numbers()

        # 应用查找高亮样式
        self.editor.text_area.tag_configure(
            "found", background=theme["found_bg"], foreground=theme["found_fg"]
        )
        self.editor.text_area.tag_configure(
            "current_match",
            background=theme["current_match_bg"],
            foreground=theme["current_match_fg"],
        )
        
        # 应用光标所在行背景色样式
        self.editor.text_area.tag_configure(
            "cursor_line", background=theme["cursor_line_bg"]
        )
        
        # 应用悬停行背景色样式
        self.editor.text_area.tag_configure(
            "hover_line", background=theme["hover_line_bg"]
        )

        # 应用菜单样式
        try:
            # 配置菜单样式
            menu_bg = theme.get("menu_bg", theme["toolbar_bg"])
            menu_fg = theme.get("menu_fg", "black")
            menu_active_bg = theme.get("menu_active_bg", theme["toolbar_bg"])
            menu_active_fg = theme.get("menu_active_fg", "white")

            # 使用tk.Menu配置菜单样式
            if hasattr(self.editor, "root") and self.editor.root:
                self.editor.root.option_add("*Menu.Background", menu_bg)
                self.editor.root.option_add("*Menu.Foreground", menu_fg)
                self.editor.root.option_add("*Menu.ActiveBackground", menu_active_bg)
                self.editor.root.option_add("*Menu.ActiveForeground", menu_active_fg)

                # 重新创建菜单以应用新样式
                self.editor.create_menu()
        except Exception as e:
            print(f"应用菜单样式时出错: {e}")

        # 应用工具栏样式
        if hasattr(self.editor, "toolbar"):
            # 使用ttk.Style配置工具栏样式
            style = ttk.Style()
            # 创建一个唯一的样式名称
            toolbar_style = f"Toolbar_{self.current_theme.replace(' ', '_')}.TFrame"
            style.configure(toolbar_style, background=theme["toolbar_bg"])
            self.editor.toolbar.configure(style=toolbar_style)

            # 配置工具栏按钮样式
            button_style = (
                f"ToolbarButton_{self.current_theme.replace(' ', '_')}.TButton"
            )
            # 使用主题配置中的按钮文字颜色
            button_fg = theme.get("toolbar_button_fg", "black")

            style.configure(
                button_style, background=theme["toolbar_bg"], foreground=button_fg
            )
            # 配置按钮在不同状态下的样式
            style.map(
                button_style,
                background=[
                    (
                        "active",
                        (
                            theme["toolbar_active_bg"]
                            if "toolbar_active_bg" in theme
                            else theme["toolbar_bg"]
                        ),
                    ),
                    (
                        "pressed",
                        (
                            theme["toolbar_pressed_bg"]
                            if "toolbar_pressed_bg" in theme
                            else theme["toolbar_bg"]
                        ),
                    ),
                ],
                foreground=[("active", button_fg), ("pressed", button_fg)],
            )

            # 更新所有工具栏按钮的样式
            if hasattr(self.editor, "toolbar_buttons"):
                for btn in self.editor.toolbar_buttons:
                    btn.configure(style=button_style)

        # 应用状态栏样式
        if hasattr(self.editor, "statusbar_frame"):
            self.editor.statusbar_frame.config(bg=theme["statusbar_bg"])
        if hasattr(self.editor, "left_status"):
            self.editor.left_status.config(
                bg=theme["statusbar_bg"], fg=theme["statusbar_fg"]
            )
        if hasattr(self.editor, "right_status"):
            self.editor.right_status.config(
                bg=theme["statusbar_bg"], fg=theme["statusbar_fg"]
            )
        # 应用居中状态栏样式（自动保存状态）
        if hasattr(self.editor, "center_status"):
            self.editor.center_status.config(
                bg=theme["statusbar_bg"], fg=theme["statusbar_fg"]
            )
            # 如果编辑器有重置居中状态栏的方法，调用它以确保状态一致
            if hasattr(self.editor, "reset_center_status"):
                self.editor.reset_center_status()