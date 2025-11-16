#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
行号更新性能测试脚本
用于测试优化后的行号更新功能性能改进
"""

import tkinter as tk
from tkinter import ttk
import time
import random
import string


class LineNumberPerformanceTest:
    def __init__(self, root):
        self.root = root
        self.root.title("行号更新性能测试")
        self.root.geometry("800x600")

        # 创建文本区域和行号区域
        self.text_frame = ttk.Frame(root)
        self.text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 行号区域
        self.line_numbers = tk.Canvas(
            self.text_frame, width=50, bg="#f0f0f0", highlightthickness=0
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # 文本区域
        self.text_area = tk.Text(self.text_frame, wrap=tk.NONE, undo=True, maxundo=20)
        self.text_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 滚动条
        self.scrollbar = ttk.Scrollbar(
            self.text_area, orient=tk.VERTICAL, command=self.text_area.yview
        )
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=self.scrollbar.set)

        # 控制面板
        self.control_frame = ttk.Frame(root)
        self.control_frame.pack(fill=tk.X, padx=10, pady=5)

        # 测试按钮
        self.test_btn = ttk.Button(
            self.control_frame, text="测试性能", command=self.run_performance_test
        )
        self.test_btn.pack(side=tk.LEFT, padx=5)

        # 结果显示
        self.result_text = tk.Text(root, height=10)
        self.result_text.pack(fill=tk.BOTH, expand=False, padx=10, pady=5)

        # 初始化变量
        self.show_line_numbers = True
        self.font_family = "Consolas"
        self.font_size = 12
        self._cached_total_lines = 0
        self._cached_line_number_width = 50
        self._cached_font = (self.font_family, self.font_size)

        # 绑定事件
        self.text_area.bind(
            "<KeyRelease>", lambda e: self.schedule_line_number_update(50)
        )
        self.text_area.bind(
            "<<Modified>>", lambda e: self.schedule_line_number_update(50)
        )
        self.text_area.bind(
            "<ButtonRelease>", lambda e: self.schedule_line_number_update(50)
        )
        self.root.bind("<Configure>", self.on_window_configure)

        # 生成测试数据
        self.generate_test_data()

    def generate_test_data(self):
        """生成测试数据"""
        self.text_area.delete(1.0, tk.END)
        # 生成1000行测试数据
        for i in range(1000):
            line_length = random.randint(20, 100)
            line_content = "".join(
                random.choices(
                    string.ascii_letters + string.digits + " ", k=line_length
                )
            )
            self.text_area.insert(tk.END, f"{i+1}: {line_content}\n")

    def on_window_configure(self, event):
        """处理窗口配置事件"""
        if event.widget == self.root:
            self.schedule_line_number_update()

    def schedule_line_number_update(self, delay=50):
        """调度行号更新，实现防抖动机制"""
        if hasattr(self, "_line_number_update_job"):
            self.root.after_cancel(self._line_number_update_job)
        self._line_number_update_job = self.root.after(delay, self.update_line_numbers)

    def update_line_numbers(self, event=None):
        """更新行号显示（优化版本）"""
        start_time = time.time()

        # 如果没有启用行号显示，直接返回
        if not getattr(self, "show_line_numbers", True):
            return

        # 清除之前的行号
        self.line_numbers.delete("all")

        # 获取文本区域的行数
        try:
            # 获取总行数
            last_line = self.text_area.index("end-1c").split(".")[0]
            total_lines = int(last_line)

            # 获取可见区域的第一行和最后一行
            first_visible = int(self.text_area.index("@0,0").split(".")[0])
            last_visible = int(
                self.text_area.index(f"@0,{self.text_area.winfo_height()}").split(".")[
                    0
                ]
            )

            # 确保范围有效
            first_visible = max(1, first_visible)
            last_visible = min(total_lines, last_visible + 1)

            # 计算行号区域宽度 (根据行号位数动态调整宽度)
            # 只有当行数发生变化时才重新计算宽度
            if (
                not hasattr(self, "_cached_total_lines")
                or self._cached_total_lines != total_lines
            ):
                max_line_number = total_lines
                # 根据行号位数计算宽度
                digits = len(str(max_line_number))
                line_number_width = max(40, digits * 13 + 10)
                self.line_numbers.config(width=line_number_width)
                # 缓存计算结果
                self._cached_line_number_width = line_number_width
                self._cached_total_lines = total_lines
            else:
                line_number_width = self._cached_line_number_width

            # 设置字体 (如果字体发生变化则更新)
            current_font = (self.font_family, self.font_size)
            if not hasattr(self, "_cached_font") or self._cached_font != current_font:
                self._cached_font = current_font

            # 绘制可见区域的行号
            for i in range(first_visible, last_visible + 1):
                # 计算行号的y坐标
                dlineinfo = self.text_area.dlineinfo(f"{i}.0")
                if dlineinfo:
                    y_pos = dlineinfo[1]  # y坐标
                    line_height = dlineinfo[3]  # 行高
                    # 在行号区域绘制行号
                    self.line_numbers.create_text(
                        line_number_width - 5,
                        y_pos + line_height // 2,  # x, y坐标
                        text=str(i),
                        font=current_font,
                        fill="gray",
                        anchor="e",  # 右对齐
                    )
        except Exception as e:
            print(f"Error in update_line_numbers: {e}")

        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # 转换为毫秒
        self.result_text.insert(tk.END, f"行号更新耗时: {execution_time:.4f} 毫秒\n")
        self.result_text.see(tk.END)

    def run_performance_test(self):
        """运行性能测试"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "开始性能测试...\n")

        # 测试多次行号更新的平均耗时
        total_time = 0
        test_count = 100

        for i in range(test_count):
            start_time = time.time()
            self.update_line_numbers()
            end_time = time.time()
            total_time += (end_time - start_time) * 1000  # 转换为毫秒

            # 强制更新界面
            self.root.update_idletasks()

        average_time = total_time / test_count
        self.result_text.insert(
            tk.END, f"平均行号更新耗时: {average_time:.4f} 毫秒 ({test_count} 次测试)\n"
        )
        self.result_text.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = LineNumberPerformanceTest(root)
    root.mainloop()
