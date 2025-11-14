import tkinter as tk
from tkinter import font
import customtkinter as ctk
from config.config_manager import config_manager


class LineNumberCanvas(ctk.CTkCanvas):
    """
    行号侧边栏组件，用于在文本编辑器左侧显示行号

    Args:
        parent: 父窗口组件
        text_widget: 关联的文本编辑组件
        width: 侧边栏宽度，默认30像素
        **kwargs: 传递给CTkCanvas的其他参数
    """

    def __init__(self, parent, text_widget=None, width=60, **kwargs):
        super().__init__(parent, width=width, **kwargs)
        self.parent = parent
        self.text_widget = text_widget
        self.width = width

        # 获取文本框字体配置
        text_editor_config = config_manager.get("text_editor", {})
        self.font_family = text_editor_config.get("font", "Microsoft YaHei UI")
        self.font_size = max(
            8, text_editor_config.get("font_size", 15) - 2
        )  # 字号减2，确保最小值为8

        # 设置字体
        self.line_number_font = font.Font(family=self.font_family, size=self.font_size)

        # 设置文本颜色
        self.text_color = "#2b91af"

        # 设置背景颜色
        self.bg_color = "#e0e0e0"

        # 设置数字的容纳额外空间
        self.number_padding = 45

        # 配置Canvas样式
        self.configure(
            bg=self.bg_color, highlightthickness=1, highlightbackground="#cccccc"
        )

        # 初始化缓存属性
        self._cached_total_lines = None
        self._cached_line_number_width = width  # 初始化为传入的宽度
        self._cached_font = None

        # 调用set_text_widget来设置文本组件并绑定事件
        self.set_text_widget(text_widget)

        # 初始绘制示例行号
        self.parent.after(200, self.draw_line_numbers)

    def set_text_widget(self, text_widget):
        """设置关联的文本编辑组件并绑定必要的事件"""
        # 绑定行号栏的鼠标点击事件
        self.bind("<Button-1>", self._on_line_number_click, add="+")

        self.text_widget = text_widget
        if self.text_widget:
            # 绑定所有需要的事件，使用add="+"确保不覆盖其他绑定
            self.text_widget.bind(
                "<KeyPress>", self._on_text_change, add="+"
            )  # 绑定所有按键事件
            self.text_widget.bind(
                "<KeyRelease>", self._on_text_change, add="+"
            )  # 绑定所有按键抬起事件
            self.text_widget.bind(
                "<Button-1>", self._on_text_change, add="+"
            )  # 绑定鼠标点击事件
            self.text_widget.bind(
                "<MouseWheel>", self._on_scroll, add="+"
            )  # 绑定鼠标滚轮事件

            # 添加更多文本修改相关的事件绑定
            # 注意：CTkTextbox不支持<Modified>事件，所以我们使用其他事件来捕获文本变化
            self.text_widget.bind(
                "<Insert>", self._on_text_change, add="+"
            )  # 插入键事件
            self.text_widget.bind(
                "<Delete>", self._on_text_change, add="+"
            )  # 删除键事件
            self.text_widget.bind(
                "<BackSpace>", self._on_text_change, add="+"
            )  # 退格键事件
            self.text_widget.bind(
                "<Return>", self._on_text_change, add="+"
            )  # 回车键事件
            self.text_widget.bind("<Tab>", self._on_text_change, add="+")  # Tab键事件

            # 绑定粘贴和剪切事件
            self.text_widget.bind(
                "<<Paste>>", self._on_text_change, add="+"
            )  # 粘贴事件
            self.text_widget.bind("<<Cut>>", self._on_text_change, add="+")  # 剪切事件

            # 绑定滚动条相关事件
            self.text_widget.bind("<Button-4>", self._on_scroll, add="+")  # Linux上滚
            self.text_widget.bind("<Button-5>", self._on_scroll, add="+")  # Linux下滚
            self.text_widget.bind(
                "<B1-Motion>", self._on_scroll, add="+"
            )  # 鼠标拖动滚动
            self.text_widget.bind(
                "<ButtonRelease-1>", self._on_scroll, add="+"
            )  # 鼠标释放后更新

            # 对于CTkTextbox，我们需要监听其内部的textbox组件的Modified事件
            try:
                self.text_widget._textbox.bind(
                    "<<Modified>>", self._on_text_change, add="+"
                )
            except:
                # 如果绑定失败，忽略错误，继续使用其他事件监听
                pass

    def _on_line_number_click(self, event):
        """处理行号点击事件，选中对应的整行内容"""
        # 获取点击位置对应的行号
        clicked_item = self.find_closest(event.x, event.y)[0]
        tags = self.gettags(clicked_item)

        # 查找行号标签
        line_number = None
        for tag in tags:
            if tag.startswith("line_"):
                try:
                    line_number = int(tag.split("_")[1])
                    break
                except (ValueError, IndexError):
                    continue

        # 如果找到了行号，选中对应的整行内容
        if line_number and self.text_widget:
            try:
                # 选中整行内容
                line_start = f"{line_number}.0"
                line_end = f"{line_number}.end"
                self.text_widget.tag_add("sel", line_start, line_end)
                self.text_widget.mark_set("insert", line_end)  # 设置光标位置到行尾
                self.text_widget.focus_set()  # 确保文本框获得焦点
            except Exception as e:
                print(f"Error selecting line: {e}")
                pass

    def _on_text_change(self, event=None):
        """文本内容变化时更新行号"""
        self.draw_line_numbers()

    def _on_scroll(self, event=None):
        """滚动时更新行号位置"""
        self.draw_line_numbers()

    def draw_line_numbers(self):
        """
        绘制行号
        """
        # 清除之前的行号和高亮矩形
        self.delete("all")

        # 获取文本区域的行数
        try:
            # 获取总行数 (使用end-1c来正确获取最后一行)
            last_line = self.text_widget.index("end-1c").split(".")[0]
            total_lines = int(last_line)

            # 获取可见区域的第一行和最后一行
            first_visible = int(self.text_widget.index("@0,0").split(".")[0])

            # 计算可见区域的最后一行，考虑文本框高度
            try:
                # 获取文本框的高度
                text_height = self.text_widget.winfo_height()
                # 获取最后一行的索引
                last_visible_index = self.text_widget.index(f"@0,{text_height}")
                last_visible = int(last_visible_index.split(".")[0])
            except:
                # 如果计算失败，使用默认值
                last_visible = first_visible + 50  # 默认显示50行

            # 确保范围有效
            first_visible = max(1, first_visible)
            last_visible = min(total_lines, last_visible)

            # 计算行号区域宽度 (根据行号位数动态调整宽度)
            # 只有当行数发生变化时才重新计算宽度
            if self._cached_total_lines != total_lines:
                max_line_number = total_lines
                # 根据行号位数计算宽度：增加每数字宽度和额外空间确保行号能完整显示
                digits = len(str(max_line_number))
                # 进一步增加每数字宽度系数，为更多位数的行号提供足够空间
                line_number_width = max(
                    60, digits * 25 + self.number_padding
                )  # 大幅增加系数和边距
                # 调用update_width方法设置宽度
                self.update_width(line_number_width)
                # 更新行总数缓存
                self._cached_total_lines = total_lines
            else:
                # 获取缓存的宽度
                line_number_width = self._cached_line_number_width

            # 设置字体 (如果字体发生变化则更新)
            current_font = (self.font_family, self.font_size - 3)
            if self._cached_font != current_font:
                self._cached_font = current_font

            # 绘制可见区域的行号
            for i in range(first_visible, last_visible + 1):
                # 使用dlineinfo方法获取更准确的行位置信息
                dlineinfo = self.text_widget.dlineinfo(f"{i}.0")

                # 如果dlineinfo不可用, 跳过当前行
                if not dlineinfo:
                    continue

                # 开始绘制
                y_pos = dlineinfo[1]  # y坐标
                line_height = dlineinfo[3]  # 行高

                # 创建行号背景矩形（默认透明，鼠标悬浮时会使用悬浮颜色）
                self.create_rectangle(
                    0,
                    y_pos,
                    line_number_width,
                    y_pos + line_height,
                    fill="",
                    outline="",
                    tags=("line_bg", f"line_{i}"),
                )

                # 计算行号中心位置（垂直居中）
                # 使用文本的基线位置来对齐行号，确保与文本行完全对齐
                text_baseline = (
                    y_pos + line_height // 2 + 10
                )  # 微调位置，使行号与文本对齐

                # 在行号区域绘制行号
                self.create_text(
                    line_number_width - 5,
                    text_baseline,  # x, y坐标，使用基线位置
                    text=str(i),
                    font=current_font,
                    fill=self.text_color,
                    anchor="e",  # 右对齐
                    tags=("line_number", f"line_{i}"),
                )

                # 为行号添加可点击的透明矩形区域，扩大点击范围
                self.create_rectangle(
                    0,
                    y_pos,
                    line_number_width,
                    y_pos + line_height,
                    fill="",
                    outline="",
                    tags=("clickable", f"line_{i}"),
                )
        except Exception as e:
            # 忽略错误, 保持程序稳定
            print(f"Error in update_line_numbers: {e}")
            pass

    def toggle_visibility(self, show=True):
        """切换行号栏的可见性"""
        if show:
            # 使用grid布局显示行号栏
            self.grid(row=0, column=0, sticky="nsw")
            # 显示时重新计算宽度以确保正确性
            self.draw_line_numbers()
        else:
            self.grid_forget()

    def update_width(self, new_width):
        """更新侧边栏宽度

        手动设置行号栏宽度，更新缓存
        注意：不触发重绘，由调用者决定是否需要重绘

        Args:
            new_width: 新的行号栏宽度（像素）
        """
        self.width = new_width
        self.configure(width=new_width)
        # 更新宽度缓存
        self._cached_line_number_width = new_width
