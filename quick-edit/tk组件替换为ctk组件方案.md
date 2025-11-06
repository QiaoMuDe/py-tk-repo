# CustomTkinter 组件替换方案

## 项目概述

本方案旨在将现有的文本编辑器项目中所有的 tkinter 和 ttk 组件替换为 CustomTkinter 库的组件，以提升界面美观度和用户体验。

## 组件替换对照表

### 核心窗口组件

| 原有组件         | CustomTkinter 替换组件            | 替换说明                               |
| ---------------- | --------------------------------- | -------------------------------------- |
| tk.Tk()          | customtkinter.CTk()               | 主窗口替换，需要设置外观模式和颜色主题 |
| tk.Toplevel()    | customtkinter.CTkToplevel()       | 顶级窗口替换                           |
| tkinterdnd2.Tk() | customtkinter.CTk() + tkinterdnd2 | 需要同时继承 CTk 和 DnD 功能           |

### 布局容器组件

| 原有组件         | CustomTkinter 替换组件   | 替换说明                           |
| ---------------- | ------------------------ | ---------------------------------- |
| tk.Frame()       | customtkinter.CTkFrame() | 基础框架替换                       |
| ttk.Frame()      | customtkinter.CTkFrame() | 基础框架替换                       |
| tk.LabelFrame()  | customtkinter.CTkFrame() | 使用 CTkFrame 模拟 LabelFrame 效果 |
| ttk.LabelFrame() | customtkinter.CTkFrame() | 使用 CTkFrame 模拟 LabelFrame 效果 |

### 交互控件组件

| 原有组件          | CustomTkinter 替换组件         | 替换说明                             |
| ----------------- | ------------------------------ | ------------------------------------ |
| tk.Button()       | customtkinter.CTkButton()      | 按钮替换，支持 hover 和 pressed 状态 |
| ttk.Button()      | customtkinter.CTkButton()      | 按钮替换                             |
| tk.Label()        | customtkinter.CTkLabel()       | 标签替换                             |
| ttk.Label()       | customtkinter.CTkLabel()       | 标签替换                             |
| tk.Entry()        | customtkinter.CTkEntry()       | 单行输入框替换                       |
| ttk.Entry()       | customtkinter.CTkEntry()       | 单行输入框替换                       |
| tk.Text()         | customtkinter.CTkTextbox()     | 多行文本框替换                       |
| tk.Checkbutton()  | customtkinter.CTkCheckBox()    | 复选框替换                           |
| ttk.Checkbutton() | customtkinter.CTkCheckBox()    | 复选框替换                           |
| tk.Radiobutton()  | customtkinter.CTkRadioButton() | 单选按钮替换                         |
| ttk.Radiobutton() | customtkinter.CTkRadioButton() | 单选按钮替换                         |
| tk.Listbox()      | customtkinter.CTkTextbox()     | 使用 CTkTextbox 模拟 Listbox 功能    |
| tk.Scrollbar()    | customtkinter.CTkScrollbar()   | 滚动条替换                           |
| ttk.Scrollbar()   | customtkinter.CTkScrollbar()   | 滚动条替换                           |

### 菜单组件

| 原有组件        | CustomTkinter 替换组件           | 替换说明               |
| --------------- | -------------------------------- | ---------------------- |
| tk.Menu()       | customtkinter.CTkMenu()          | 菜单替换               |
| tk.Menubutton() | customtkinter.CTkButton() + 菜单 | 使用按钮和菜单组合模拟 |

### 变量类

| 原有组件        | CustomTkinter 替换组件     | 替换说明       |
| --------------- | -------------------------- | -------------- |
| tk.StringVar()  | customtkinter.StringVar()  | 字符串变量替换 |
| tk.BooleanVar() | customtkinter.BooleanVar() | 布尔变量替换   |
| tk.IntVar()     | customtkinter.IntVar()     | 整数变量替换   |

### 对话框

| 原有组件        | CustomTkinter 替换组件 | 替换说明                          |
| --------------- | ---------------------- | --------------------------------- |
| tk.filedialog   | 自定义对话框           | 使用 CTk 组件创建自定义文件对话框 |
| tk.messagebox   | 自定义消息框           | 使用 CTk 组件创建自定义消息框     |
| tk.simpledialog | 自定义对话框           | 使用 CTk 组件创建自定义对话框     |

## 实施步骤

### 1. 环境准备

```
# 安装CustomTkinter库
pip install customtkinter
pip install CTkMessagebox  # 用于消息框
pip install CTkFileDialog   # 用于文件对话框
```

### 2. 导入替换

在所有 Python 文件中替换导入语句：

```
# 替换前
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

# 替换后
import customtkinter
from customtkinter import CTk, CTkToplevel, CTkFrame, CTkButton, CTkLabel, CTkEntry, CTkTextbox, CTkCheckBox, CTkRadioButton, CTkScrollbar, StringVar, BooleanVar, IntVar
import CTkMessagebox
import CTkFileDialog
```

### 3. 主窗口改造 ([QuickEdit.py](http://QuickEdit.py))

```
# 替换前
root = tkinterdnd2.Tk()

# 替换后
class DnDCTk(CTk, tkinterdnd2.TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
root = DnDCTk()
customtkinter.set_appearance_mode("light")  # 设置外观模式
customtkinter.set_default_color_theme("blue")  # 设置颜色主题
```

### 4. 主要组件替换示例

#### 框架组件替换

```
# 替换前
frame = tk.Frame(parent)
frame = ttk.Frame(parent)

# 替换后
frame = CTkFrame(parent, corner_radius=8, border_width=1)
```

#### 按钮组件替换

```
# 替换前
button = tk.Button(parent, text="确定", command=callback)
button = ttk.Button(parent, text="确定", command=callback)

# 替换后
button = CTkButton(parent, text="确定", command=callback, corner_radius=6)
```

#### 文本框组件替换

```
# 替换前
text_area = tk.Text(parent, font=("Microsoft YaHei UI", 12))

# 替换后
text_area = CTkTextbox(parent, font=("Microsoft YaHei UI", 12), corner_radius=4)
```

#### 滚动条组件替换

```
# 替换前
scrollbar = tk.Scrollbar(parent)
scrollbar = ttk.Scrollbar(parent)

# 替换后
scrollbar = CTkScrollbar(parent)
```

### 5. 对话框替换

#### 消息框替换

```
# 替换前
tk.messagebox.showinfo("标题", "内容")
tk.messagebox.showwarning("标题", "警告")
tk.messagebox.showerror("标题", "错误")

# 替换后
CTkMessagebox.CTkMessagebox(title="标题", message="内容", icon="info")
CTkMessagebox.CTkMessagebox(title="标题", message="警告", icon="warning")
CTkMessagebox.CTkMessagebox(title="标题", message="错误", icon="cancel")
```

#### 文件对话框替换

```
# 替换前
file_path = tk.filedialog.askopenfilename()
file_path = tk.filedialog.asksaveasfilename()

# 替换后
file_path = CTkFileDialog.CTkFileDialog().open_file()
file_path = CTkFileDialog.CTkFileDialog().save_file()
```

### 6. 样式配置

```
# 设置全局外观模式
customtkinter.set_appearance_mode("light")  # "light" 或 "dark"

# 设置全局颜色主题
customtkinter.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

# 自定义组件样式
button = CTkButton(
    parent,
    text="自定义按钮",
    fg_color="#4A90E2",
    hover_color="#357ABD",
    text_color="white",
    font=("Microsoft YaHei UI", 12, "bold"),
    corner_radius=8,
    width=120,
    height=40
)
```

### 7. 主题管理器适配

修改[theme_manager.py](http://theme_manager.py)文件，适配 CustomTkinter 的主题系统：

```
def apply_theme(self):
    """应用当前主题到所有UI元素"""
    theme = self.get_current_theme()
    
    # 设置全局外观模式
    if theme["name"] in ["深色主题", "霓虹粉主题"]:
        customtkinter.set_appearance_mode("dark")
    else:
        customtkinter.set_appearance_mode("light")
    
    # 应用文本区域样式
    self.editor.text_area.configure(
        bg_color=theme["text_bg"],
        text_color=theme["text_fg"],
        border_color=theme["line_numbers_bg"]
    )
    
    # 应用按钮样式
    for btn in self.editor.toolbar_buttons:
        btn.configure(
            fg_color=theme["toolbar_bg"],
            hover_color=theme["toolbar_active_bg"],
            text_color=theme["toolbar_button_fg"]
        )
```

## 重点注意事项

### 1. 事件绑定兼容性

- CustomTkinter 组件的事件绑定方式与 tkinter 基本一致

- 需要测试所有键盘快捷键和鼠标事件

### 2. 布局管理

- CTk 组件的 pack、grid、place 方法与 tkinter 兼容

- 可能需要调整一些间距和内边距

### 3. 字体设置

- CTk 组件的字体设置方式略有不同

- 需要确保所有文本元素使用统一的字体配置

### 4. 颜色配置

- CustomTkinter 使用 fg_color、text_color 等参数

- 需要重新映射主题管理器中的颜色配置

### 5. 兼容性测试

- 需要对所有功能进行全面测试

- 特别注意对话框、菜单和快捷键功能

## 预期效果

1. **界面美观度提升**：现代化的设计风格，支持深色 / 浅色主题

1. **交互体验改善**：按钮 hover 效果、圆角设计、阴影效果

1. **主题系统优化**：更好的主题切换体验

1. **性能优化**：CustomTkinter 在某些场景下性能更好

## 实施计划

### 第一阶段：基础组件替换

- 替换主窗口和基础框架

- 替换按钮、标签、输入框等简单组件

### 第二阶段：复杂组件替换

- 替换文本框、滚动条、列表框等复杂组件

- 适配语法高亮功能

### 第三阶段：对话框和菜单

- 替换所有对话框

- 替换菜单系统

### 第四阶段：主题系统适配

- 更新主题管理器

- 确保主题切换正常工作

### 第五阶段：测试和优化

- 全面功能测试

- 性能优化

- 界面微调

## 风险评估

1. **兼容性风险**：部分 tkinter 特性在 CustomTkinter 中可能不支持

1. **学习成本**：开发团队需要熟悉 CustomTkinter 的 API

1. **测试工作量**：需要全面测试所有功能

1. **性能影响**：在某些情况下可能影响性能

建议采用渐进式替换策略，先在非关键功能上进行替换，验证稳定性后再全面推广。