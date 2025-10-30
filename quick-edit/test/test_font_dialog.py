import tkinter as tk
from tkinter import ttk, font

class FontDialogTest:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("字体对话框测试")
        self.root.geometry("600x400")
        
        self.font_family = "Microsoft YaHei UI"
        self.font_size = 12
        
        # 创建UI
        self.create_ui()
        
    def create_ui(self):
        # 显示当前字体
        self.current_font_label = tk.Label(
            self.root, 
            text=f"当前字体: {self.font_family}", 
            font=(self.font_family, 12)
        )
        self.current_font_label.pack(pady=20)
        
        # 打开字体选择对话框按钮
        select_font_btn = tk.Button(
            self.root,
            text="选择字体",
            command=self.choose_font,
            font=("Microsoft YaHei UI", 12),
            width=15,
            height=2
        )
        select_font_btn.pack(pady=20)
        
        # 示例文本
        sample_label = tk.Label(
            self.root,
            text="示例文本：The quick brown fox jumps over the lazy dog\n快速的棕色狐狸跳过了懒惰的狗",
            font=(self.font_family, self.font_size),
            wraplength=500,
            justify=tk.LEFT
        )
        sample_label.pack(pady=20)
        
        self.sample_label = sample_label
        
    def choose_font(self):
        """选择字体"""
        # 获取系统可用字体列表
        available_fonts = list(font.families())
        available_fonts.sort()  # 排序字体列表
        
        # 创建字体选择对话框
        font_dialog = tk.Toplevel(self.root)
        font_dialog.title("选择字体")
        font_dialog.geometry("400x500")
        font_dialog.resizable(True, True)
        font_dialog.transient(self.root)
        font_dialog.grab_set()  # 模态对话框
        
        # 当前字体标签
        current_label = tk.Label(
            font_dialog, 
            text=f"当前字体: {self.font_family}", 
            font=("Microsoft YaHei UI", 10)
        )
        current_label.pack(pady=10)
        
        # 创建滚动条和列表框
        frame = tk.Frame(font_dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 字体列表框
        font_listbox = tk.Listbox(
            frame, 
            yscrollcommand=scrollbar.set,
            font=("Microsoft YaHei UI", 10)
        )
        font_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=font_listbox.yview)
        
        # 添加字体到列表框
        for font_name in available_fonts:
            font_listbox.insert(tk.END, font_name)
            
        # 选中当前字体
        try:
            current_index = available_fonts.index(self.font_family)
            font_listbox.selection_set(current_index)
            font_listbox.see(current_index)
        except ValueError:
            # 如果当前字体不在列表中，默认选中第一个
            if available_fonts:
                font_listbox.selection_set(0)
                font_listbox.see(0)
        
        # 双击选择字体
        def on_font_select(event=None):
            selection = font_listbox.curselection()
            if selection:
                selected_font = font_listbox.get(selection[0])
                self.font_family = selected_font
                self.update_display()
                font_dialog.destroy()
        
        # 绑定双击事件
        font_listbox.bind("<Double-Button-1>", on_font_select)
        
        # 按钮框架
        button_frame = tk.Frame(font_dialog)
        button_frame.pack(pady=10)
        
        # 确定按钮
        ok_button = tk.Button(
            button_frame, 
            text="确定", 
            command=on_font_select,
            width=10
        )
        ok_button.pack(side=tk.LEFT, padx=5)
        
        # 取消按钮
        cancel_button = tk.Button(
            button_frame, 
            text="取消", 
            command=font_dialog.destroy,
            width=10
        )
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # 居中显示对话框
        font_dialog.update_idletasks()
        x = (font_dialog.winfo_screenwidth() // 2) - (font_dialog.winfo_width() // 2)
        y = (font_dialog.winfo_screenheight() // 2) - (font_dialog.winfo_height() // 2)
        font_dialog.geometry(f"+{x}+{y}")
        
    def update_display(self):
        """更新显示"""
        self.current_font_label.config(text=f"当前字体: {self.font_family}", font=(self.font_family, 12))
        self.sample_label.config(font=(self.font_family, self.font_size))
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = FontDialogTest()
    app.run()