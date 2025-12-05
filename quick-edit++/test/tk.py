import tkinter as tk

# 主窗口
root = tk.Tk()
root.title("VS 风格左右分栏（tk 原生最终版）")
root.geometry("800x600")

# 原生 tk PanedWindow（不支持 weight，仅保留支持的参数）
paned_window = tk.PanedWindow(
    root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=4
)
paned_window.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

# 左侧面板（仅设置 minsize，无 weight）
left_frame = tk.Frame(paned_window, width=200, height=600, bg="#f0f0f0")
tk.Label(left_frame, text="左侧面板", bg="#f0f0f0").pack(pady=20)
paned_window.add(left_frame, minsize=100)  # 仅设置最小宽度，无 weight

# 右侧面板
right_frame = tk.Frame(paned_window, width=600, height=600, bg="#ffffff")
tk.Label(right_frame, text="右侧面板", bg="#ffffff").pack(pady=20)
paned_window.add(right_frame, minsize=300)  # 仅设置最小宽度，无 weight

root.mainloop()
