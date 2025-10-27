import tkinter as tk
from tkinter import ttk

class ThemeManager:
    """主题管理器类"""

    # 预定义的主题
    THEMES = {
        "light": {
            "name": "浅色主题",
            "text_bg": "white",
            "text_fg": "black",
            "text_insert_bg": "black",
            "text_select_bg": "lightblue",
            "text_select_fg": "black",
            "line_numbers_bg": "#f0f0f0",
            "line_numbers_fg": "gray",
            "found_bg": "yellow",
            "found_fg": "black",
            "current_match_bg": "orange",
            "current_match_fg": "black",
            "menu_bg": "#f0f0f0",
            "menu_fg": "black",
            "menu_active_bg": "#316AC5",
            "menu_active_fg": "white",
            "toolbar_bg": "#f0f0f0",
            "toolbar_active_bg": "#d0d0d0",
            "toolbar_pressed_bg": "#c0c0c0",
            "toolbar_button_fg": "black",
            "statusbar_bg": "#f0f0f0",
            "statusbar_fg": "black",
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
            "text_bg": "#e6f3ff",
            "text_fg": "#003366",
            "text_insert_bg": "#003366",
            "text_select_bg": "#99ccff",
            "text_select_fg": "#003366",
            "line_numbers_bg": "#cce6ff",
            "line_numbers_fg": "#0066cc",
            "found_bg": "#ffff99",
            "found_fg": "#003366",
            "current_match_bg": "#ffcc66",
            "current_match_fg": "#003366",
            "menu_bg": "#cce6ff",
            "menu_fg": "#003366",
            "menu_active_bg": "#003366",
            "menu_active_fg": "#ffffff",
            "toolbar_bg": "#cce6ff",
            "toolbar_active_bg": "#99ccff",
            "toolbar_pressed_bg": "#6699cc",
            "toolbar_button_fg": "#003366",
            "statusbar_bg": "#cce6ff",
            "statusbar_fg": "#003366",
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
            "name": "经典绿色主题",
            "text_bg": "#e6ffe6",  # 更浅的绿色背景
            "text_fg": "#006600",  # 深绿色文字
            "text_insert_bg": "#006600",
            "text_select_bg": "#99cc99",
            "text_select_fg": "#000000",
            "line_numbers_bg": "#ccffcc",
            "line_numbers_fg": "#006600",
            "found_bg": "#ffff99",
            "found_fg": "#000000",
            "current_match_bg": "#ffcc66",
            "current_match_fg": "#000000",
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