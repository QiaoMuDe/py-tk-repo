import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

# 设置CTK主题
ctk.set_appearance_mode("dark")  # 可选: "dark", "light", "system"
ctk.set_default_color_theme("blue")  # 可选: "blue", "green", "dark-blue"

# 主窗口
root = ctk.CTk()
root.title("CTK + TTK 混合组件测试")
root.geometry("800x600")

# 配置 ttk 分割线样式
style = ttk.Style(root)
style.configure(
    "TPanedwindow", sashwidth=8, background="#cccccc"
)  # 设置分割线宽度和背景色

# 创建 ttk PanedWindow
paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
paned_window.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

# 左侧面板 - 使用CTK组件
left_frame = ctk.CTkFrame(paned_window)
ctk.CTkLabel(left_frame, text="左侧面板 (CTK组件)").pack(pady=20, padx=10)
ctk.CTkButton(left_frame, text="CTK按钮").pack(pady=10)
paned_window.add(left_frame, weight=1)  # weight 生效

# 右侧面板 - 混合使用CTK和TTK组件
right_frame = ctk.CTkFrame(paned_window)
ctk.CTkLabel(right_frame, text="右侧面板 (混合组件)").pack(pady=10, padx=10)

# 添加一个TTK按钮
ttk_button = ttk.Button(right_frame, text="TTK按钮")
ttk_button.pack(pady=10)

# 添加一个CTK按钮
ctk.CTkButton(right_frame, text="CTK按钮").pack(pady=10)

# 添加一个TTK输入框
ttk.Entry(right_frame).pack(pady=10, padx=20, fill=tk.X)

paned_window.add(right_frame, weight=3)  # weight=3 表示拉伸时占比更高


# 设置初始分割位置
def set_initial_pane_position():
    # 设置左侧面板初始宽度为200像素
    paned_window.sashpos(0, 200)


# 限制面板的最小宽度
def limit_pane_size(event=None):
    # 获取当前分割线的位置
    sash_pos = paned_window.sashpos(0)

    # 限制左侧面板最小宽度为100像素
    if sash_pos < 100:
        paned_window.sashpos(0, 100)

    # 限制右侧面板最小宽度为300像素
    window_width = root.winfo_width()
    if sash_pos > window_width - 300:
        paned_window.sashpos(0, window_width - 300)


# 绑定事件，限制面板的最小宽度
# 绑定到 <Configure> 事件，当窗口大小改变时也会触发
paned_window.bind("<Configure>", limit_pane_size)
# 绑定到 <ButtonRelease-1> 事件，当用户释放鼠标时也会触发
paned_window.bind("<ButtonRelease-1>", limit_pane_size)

# 在窗口显示后设置初始分割位置
root.after(100, set_initial_pane_position)

root.mainloop()
