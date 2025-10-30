import tkinter as tk
from tkinter import font

# 创建主窗口
root = tk.Tk()
root.title("字体功能测试")
root.geometry("400x300")

# 获取系统字体列表
available_fonts = list(font.families())
available_fonts.sort()

# 显示前20个字体
print("前20个可用字体:")
for i, f in enumerate(available_fonts[:20]):
    print(f"{i+1}. {f}")

print(f"\n总共找到 {len(available_fonts)} 种字体")

# 创建标签显示不同字体
label1 = tk.Label(root, text="Microsoft YaHei UI 字体", font=("Microsoft YaHei UI", 12))
label1.pack(pady=10)

label2 = tk.Label(root, text="Times New Roman 字体", font=("Times New Roman", 12))
label2.pack(pady=10)

label3 = tk.Label(root, text="Courier New 字体", font=("Courier New", 12))
label3.pack(pady=10)

# 如果有微软雅黑字体，也显示
if "微软雅黑" in available_fonts:
    label4 = tk.Label(root, text="微软雅黑 字体", font=("微软雅黑", 12))
    label4.pack(pady=10)
elif "Microsoft YaHei" in available_fonts:
    label4 = tk.Label(root, text="Microsoft YaHei 字体", font=("Microsoft YaHei", 12))
    label4.pack(pady=10)

# 显示字体数量
count_label = tk.Label(root, text=f"系统中共有 {len(available_fonts)} 种字体", font=("Microsoft YaHei UI", 10))
count_label.pack(pady=20)

root.mainloop()