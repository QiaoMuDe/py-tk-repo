#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
编辑操作类
该模块实现文本编辑的基本操作，包括撤销、重做、剪切、复制、粘贴、全选和清除等功能
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from config.config_manager import config_manager
import os
import datetime
import uuid
import base64
from ui.color_picker import show_color_picker


class EditOperations:
    """文本编辑操作类，提供基本的文本编辑功能"""

    def __init__(self):
        """初始化编辑操作"""
        pass

    def undo(self):
        """撤销上一步操作"""
        try:
            # 检查是否可以撤销
            if self.text_area.edit_undo():
                # 更新状态栏
                self._update_status_bar()
                # 更新字符计数
                self.update_char_count()
                # 应用语法高亮
                self.syntax_highlighter.apply_highlighting(self.current_file_path)
            else:
                self.status_bar.show_notification("没有可撤销的操作", 500)
        except Exception as e:
            # 忽略撤销操作异常
            pass

    def redo(self):
        """重做上一步撤销的操作"""
        try:
            # 检查是否可以重做
            if self.text_area.edit_redo():
                # 更新状态栏
                self._update_status_bar()
                # 更新字符计数
                self.update_char_count()
                # 应用语法高亮
                self.syntax_highlighter.apply_highlighting(self.current_file_path)
            else:
                self.status_bar.show_notification("没有可重做的操作", 500)
        except Exception as e:
            # 忽略重做操作异常
            pass

    def cut(self):
        """剪切选中的文本"""
        try:
            # 检查是否有选中的文本
            try:
                selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
                if selected_text:
                    # 将选中的文本复制到剪贴板
                    self.clipboard_clear()
                    self.clipboard_append(selected_text)
                    # 删除选中的文本
                    self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
                    # 更新状态栏
                    self._update_status_bar()
                    # 更新
                    # 更新字符计数
                    self.update_char_count()
                    # 显示通知
                    self.status_bar.show_notification(
                        f"已剪切 {len(selected_text)} 个字符", 500
                    )
                else:
                    self.status_bar.show_notification("没有选中的文本", 500)
            except tk.TclError:
                # 没有选中文本
                self.status_bar.show_notification("没有选中的文本", 500)
        except Exception as e:
            # 忽略剪切操作异常
            pass

    def copy(self):
        """复制选中的文本"""
        try:
            # 检查是否有选中的文本
            try:
                selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
                if selected_text:
                    # 将选中的文本复制到剪贴板
                    self.clipboard_clear()
                    self.clipboard_append(selected_text)
                    # 显示通知
                    self.status_bar.show_notification(
                        f"已复制 {len(selected_text)} 个字符", 500
                    )
                else:
                    self.status_bar.show_notification("没有选中的文本", 500)
            except tk.TclError:
                # 没有选中文本
                self.status_bar.show_notification("没有选中的文本", 500)
        except Exception as e:
            # 忽略复制操作异常
            pass

    def paste(self):
        """粘贴剪贴板中的文本"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法粘贴", 500)
                return

            # 获取剪贴板内容
            try:
                clipboard_text = self.clipboard_get()
                if clipboard_text:
                    # 检查是否有选中的文本
                    try:
                        # 如果有选中文本，则替换选中的文本
                        self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
                        self.text_area.insert(tk.INSERT, clipboard_text)
                    except tk.TclError:
                        # 没有选中文本，在当前位置插入
                        self.text_area.insert(tk.INSERT, clipboard_text)

                    # 更新状态栏
                    self._update_status_bar()
                    # 更新字符计数
                    self.update_char_count()
                    # 显示通知
                    self.status_bar.show_notification(
                        f"已粘贴 {len(clipboard_text)} 个字符", 500
                    )
                else:
                    self.status_bar.show_notification("剪贴板为空", 500)
            except tk.TclError:
                # 剪贴板为空
                self.status_bar.show_notification("剪贴板为空", 500)
        except Exception as e:
            # 忽略粘贴操作异常
            pass

    def select_all(self):
        """全选文本"""
        try:
            # 添加选择标记
            self.text_area.tag_add(tk.SEL, "1.0", tk.END)
            # 设置光标位置到文本末尾
            self.text_area.mark_set(tk.INSERT, tk.END)
            # 确保选择可见
            self.text_area.see(tk.INSERT)
            # 更新状态栏
            self._update_status_bar()
            # 显示通知
            total_chars = self.get_char_count()
            self.status_bar.show_notification(f"已选择全部 {total_chars} 个字符", 500)
        except Exception as e:
            # 忽略全选操作异常
            pass

    def clear_all(self):
        """清除所有文本"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法清除", 500)
                return

            # 获取当前字符数
            total_chars = self.get_char_count()

            # 如果没有内容，直接返回
            if total_chars == 0:
                self.status_bar.show_notification("文本区域已经为空", 500)
                return

            # 确认是否清除所有文本
            confirmed = messagebox.askyesno(
                "确认清除", f"确定要清除所有文本吗？\n这将删除 {total_chars} 个字符。"
            )

            if confirmed:
                # 清除所有文本
                self.text_area.delete("1.0", tk.END)
                # 更新状态栏
                self._update_status_bar()
                # 更新字符计数
                self.update_char_count()
                # 更新修改状态
                self.set_modified(True)
                # 显示通知
                self.status_bar.show_notification(f"已清除 {total_chars} 个字符", 500)
        except Exception as e:
            # 忽略清除操作异常
            pass

    def clear_selection(self):
        """清除选中的文本"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法清除", 500)
                return

            # 检查是否有选中的文本
            try:
                selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
                if selected_text:
                    # 删除选中的文本
                    self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
                    # 更新状态栏
                    self._update_status_bar()
                    # 更新字符计数
                    self.update_char_count()
                    # 更新修改状态
                    self.set_modified(True)
                    # 显示通知
                    self.status_bar.show_notification(
                        f"已清除 {len(selected_text)} 个字符", 500
                    )
                else:
                    self.status_bar.show_notification("没有选中的文本", 500)
            except tk.TclError:
                # 没有选中文本
                self.status_bar.show_notification("没有选中的文本", 500)
        except Exception as e:
            # 忽略清除操作异常
            pass

    def insert_text(self, text):
        """在光标位置插入文本"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 在光标位置插入文本
            self.text_area.insert(tk.INSERT, text)

            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)

            # 显示通知
            self.status_bar.show_notification(f"已插入 {len(text)} 个字符", 500)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_shebang(self):
        """脚本的shebang行"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 在光标位置插入shebang行
            self.text_area.insert(tk.INSERT, "#!/usr/bin/env ")

            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)

            # 显示通知
            self.status_bar.show_notification("已插入脚本 shebang 行", 500)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_encoding(self):
        """插入Python脚本的编码声明"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 在光标位置插入编码声明
            self.text_area.insert(tk.INSERT, "# -*- coding: utf-8 -*-\n")

            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)

            # 显示通知
            self.status_bar.show_notification("已插入编码声明", 500)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_go_basic(self):
        """插入Go语言基本结构"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 在光标位置插入Go语言基本结构
            go_code = """package main\n\nimport "fmt"\n\nfunc main() {\n\tfmt.Println("Hello, World!")\n}"""
            self.text_area.insert(tk.INSERT, go_code)

            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)

            # 显示通知
            self.status_bar.show_notification("已插入Go语言基本结构", 500)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_python_function_template(self):
        """插入Python函数模板"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 在光标位置插入Python函数模板
            python_function = """def function_name(parameter1, parameter2):
    \"\"\"
    函数功能描述
    
    Args:
        parameter1: 参数1描述
        parameter2: 参数2描述
        
    Returns:
        返回值描述
    \"\"\"
    # 函数实现
    pass
"""
            self.text_area.insert(tk.INSERT, python_function)

            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)

            # 显示通知
            self.status_bar.show_notification("已插入Python函数模板", 500)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_python_class_template(self):
        """插入Python类模板"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 在光标位置插入Python类模板
            python_class = """class ClassName:
    \"\"\"
    类功能描述
    
    Attributes:
        attribute1: 属性1描述
        attribute2: 属性2描述
    \"\"\"
    
    def __init__(self, parameter1, parameter2):
        \"\"\"
        初始化方法
        
        Args:
            parameter1: 参数1描述
            parameter2: 参数2描述
        \"\"\"
        self.attribute1 = parameter1
        self.attribute2 = parameter2
    
    def method_name(self, parameter):
        \"\"\"
        方法功能描述
        
        Args:
            parameter: 参数描述
            
        Returns:
            返回值描述
        \"\"\"
        # 方法实现
        pass
"""
            self.text_area.insert(tk.INSERT, python_class)

            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)

            # 显示通知
            self.status_bar.show_notification("已插入Python类模板", 500)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_html_basic_structure(self):
        """插入HTML基本结构"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 在光标位置插入HTML基本结构
            html_structure = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>网页标题</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <h1>网站标题</h1>
    </header>
    
    <main>
        <section>
            <h2>内容标题</h2>
            <p>这是网页的内容部分。</p>
        </section>
    </main>
    
    <footer>
        <p>&copy; 2023 版权所有</p>
    </footer>
    
    <script src="script.js"></script>
</body>
</html>"""
            self.text_area.insert(tk.INSERT, html_structure)

            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)

            # 显示通知
            self.status_bar.show_notification("已插入HTML基本结构", 500)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_css_basic_structure(self):
        """插入CSS基本结构"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 在光标位置插入CSS基本结构
            css_structure = """/* CSS基本样式 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f8f9fa;
}

.container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* 头部样式 */
header {
    background-color: #4285f4;
    color: white;
    padding: 1rem 0;
    text-align: center;
}

/* 主要内容样式 */
main {
    padding: 2rem 0;
}

section {
    margin-bottom: 2rem;
}

h1, h2, h3, h4, h5, h6 {
    margin-bottom: 1rem;
}

p {
    margin-bottom: 1rem;
}

/* 底部样式 */
footer {
    background-color: #f1f1f1;
    text-align: center;
    padding: 1rem 0;
    margin-top: 2rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .container {
        padding: 0 10px;
    }
}"""
            self.text_area.insert(tk.INSERT, css_structure)

            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)

            # 显示通知
            self.status_bar.show_notification("已插入CSS基本结构", 500)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_javascript_function_template(self):
        """插入JavaScript函数模板"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 在光标位置插入JavaScript函数模板
            js_function = """/**
 * 函数描述
 * @param {参数类型} 参数名 - 参数描述
 * @returns {返回类型} 返回值描述
 */
function functionName(param1, param2) {
    // 验证参数
    if (!param1 || !param2) {
        throw new Error('缺少必要参数');
    }
    
    try {
        // 函数逻辑
        const result = param1 + param2;
        
        // 返回结果
        return result;
    } catch (error) {
        console.error('函数执行出错:', error);
        throw error;
    }
}

// 使用示例
try {
    const result = functionName('value1', 'value2');
    console.log('结果:', result);
} catch (error) {
    console.error('调用失败:', error);
}

// ES6箭头函数示例
const arrowFunction = (param1, param2) => {
    // 函数逻辑
    return param1 + param2;
};"""
            self.text_area.insert(tk.INSERT, js_function)

            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)

            # 显示通知
            self.status_bar.show_notification("已插入JavaScript函数模板", 500)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_sql_query_template(self):
        """插入SQL查询模板"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 在光标位置插入SQL查询模板
            sql_query = """-- SQL查询模板
-- 基本查询
SELECT 
    column1, 
    column2, 
    column3
FROM 
    table_name
WHERE 
    condition = 'value'
ORDER BY 
    column1 ASC
LIMIT 100;

-- 连接查询
SELECT 
    a.column1, 
    b.column2
FROM 
    table_a AS a
INNER JOIN 
    table_b AS b ON a.id = b.id
WHERE 
    a.condition = 'value';

-- 插入数据
INSERT INTO table_name (column1, column2, column3)
VALUES ('value1', 'value2', 'value3');

-- 更新数据
UPDATE table_name
SET 
    column1 = 'new_value1',
    column2 = 'new_value2'
WHERE 
    id = 1;

-- 删除数据
DELETE FROM table_name
WHERE 
    condition = 'value';

-- 创建表
CREATE TABLE table_name (
    id INT PRIMARY KEY AUTO_INCREMENT,
    column1 VARCHAR(255) NOT NULL,
    column2 INT,
    column3 DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_table_name_column1 ON table_name(column1);

-- 分组查询
SELECT 
    column1, 
    COUNT(*) AS count,
    AVG(column2) AS average
FROM 
    table_name
GROUP BY 
    column1
HAVING 
    COUNT(*) > 1;"""
            self.text_area.insert(tk.INSERT, sql_query)

            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)

            # 显示通知
            self.status_bar.show_notification("已插入SQL查询模板", 500)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_go_function_template(self):
        """插入GO函数模板"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 在光标位置插入GO函数模板
            go_function = """// FunctionName 函数描述
// 参数说明:
//   - param1: 参数1描述
//   - param2: 参数2描述
// 返回值:
//   - returnType: 返回值描述
//   - error: 错误信息
func FunctionName(param1 string, param2 int) (returnType string, err error) {
    // 参数验证
    if param1 == "" {
        return "", errors.New("param1不能为空")
    }
    if param2 <= 0 {
        return "", errors.New("param2必须大于0")
    }
    
    // 函数逻辑
    result := fmt.Sprintf("%s_%d", param1, param2)
    
    // 返回结果
    return result, nil
}

// 示例调用函数
func exampleFunction() {
    // 调用FunctionName函数
    result, err := FunctionName("example", 123)
    if err != nil {
        log.Printf("调用FunctionName出错: %v", err)
        return
    }
    
    fmt.Printf("结果: %s\\n", result)
}

// 带有接收者的方法
func (s *StructType) MethodName(param string) (string, error) {
    // 方法实现
    return fmt.Sprintf("方法调用: %s", param), nil
}

// 带有多个返回值的函数
func multiReturnFunction() (int, string, bool) {
    return 42, "多返回值示例", true
}

// 变参函数
func variadicFunction(params ...int) int {
    sum := 0
    for _, param := range params {
        sum += param
    }
    return sum
}

// 闭包函数
func closureFunction() func(int) int {
    return func(x int) int {
        return x * x
    }
}"""
            self.text_area.insert(tk.INSERT, go_function)

            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)

            # 显示通知
            self.status_bar.show_notification("已插入GO函数模板", 500)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_go_struct_template(self):
        """插入GO结构体模板"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 在光标位置插入GO结构体模板
            go_struct = """// StructName 结构体描述
type StructName struct {
    // 字段描述
    ID       int    `json:"id" db:"id"`              // ID字段
    Name     string `json:"name" db:"name"`          // 名称字段
    Email    string `json:"email" db:"email"`        // 邮箱字段
    Age      int    `json:"age" db:"age"`            // 年龄字段
    IsActive bool   `json:"is_active" db:"is_active"` // 是否激活
    CreatedAt time.Time `json:"created_at" db:"created_at"` // 创建时间
    UpdatedAt time.Time `json:"updated_at" db:"updated_at"` // 更新时间
}

// NewStructName 创建新的StructName实例
func NewStructName(name, email string, age int) *StructName {
    now := time.Now()
    return &StructName{
        ID:       0, // 数据库自动生成
        Name:     name,
        Email:    email,
        Age:      age,
        IsActive: true,
        CreatedAt: now,
        UpdatedAt: now,
    }
}

// String 返回StructName的字符串表示
func (s *StructName) String() string {
    return fmt.Sprintf("StructName{ID: %d, Name: %s, Email: %s, Age: %d, IsActive: %t}",
        s.ID, s.Name, s.Email, s.Age, s.IsActive)
}

// Validate 验证StructName的字段
func (s *StructName) Validate() error {
    if s.Name == "" {
        return errors.New("名称不能为空")
    }
    if s.Email == "" {
        return errors.New("邮箱不能为空")
    }
    if !strings.Contains(s.Email, "@") {
        return errors.New("邮箱格式不正确")
    }
    if s.Age < 0 || s.Age > 150 {
        return errors.New("年龄必须在0-150之间")
    }
    return nil
}

// Update 更新StructName的UpdatedAt字段
func (s *StructName) Update() {
    s.UpdatedAt = time.Now()
}

// Deactivate 停用StructName
func (s *StructName) Deactivate() {
    s.IsActive = false
    s.Update()
}

// Activate 激活StructName
func (s *StructName) Activate() {
    s.IsActive = true
    s.Update()
}

// ToJSON 将StructName转换为JSON字符串
func (s *StructName) ToJSON() (string, error) {
    jsonBytes, err := json.Marshal(s)
    if err != nil {
        return "", err
    }
    return string(jsonBytes), nil
}

// FromJSON 从JSON字符串创建StructName
func FromJSON(jsonStr string) (*StructName, error) {
    var s StructName
    err := json.Unmarshal([]byte(jsonStr), &s)
    if err != nil {
        return nil, err
    }
    return &s, nil
}

// 嵌套结构体示例
type Address struct {
    Street  string `json:"street"`
    City    string `json:"city"`
    Country string `json:"country"`
    ZipCode string `json:"zip_code"`
}

// 包含嵌套结构体的结构体
type PersonWithAddress struct {
    StructName
    Address Address `json:"address"`
}

// 接口示例
type Validator interface {
    Validate() error
}

// 实现接口
func (s *StructName) IsValid() bool {
    return s.Validate() == nil
}"""
            self.text_area.insert(tk.INSERT, go_struct)

            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)

            # 显示通知
            self.status_bar.show_notification("已插入GO结构体模板", 500)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_filename(self):
        """插入当前文件名"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 获取当前文件名
            if hasattr(self, "current_file_path") and self.current_file_path:
                filename = os.path.basename(self.current_file_path)
                self.text_area.insert(tk.INSERT, filename)

                # 更新状态栏
                self._update_status_bar()
                # 更新字符计数
                self.update_char_count()
                # 更新修改状态
                self.set_modified(True)

                # 显示通知
                self.status_bar.show_notification(f"已插入文件名: {filename}", 500)
            else:
                self.status_bar.show_notification("没有当前文件", 500)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_filepath(self):
        """插入当前文件路径"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 获取当前文件路径
            if hasattr(self, "current_file_path") and self.current_file_path:
                self.text_area.insert(tk.INSERT, self.current_file_path)

                # 更新状态栏
                self._update_status_bar()
                # 更新字符计数
                self.update_char_count()
                # 更新修改状态
                self.set_modified(True)

                # 显示通知
                self.status_bar.show_notification(
                    f"已插入文件路径: {self.current_file_path}", 500
                )
            else:
                self.status_bar.show_notification("没有当前文件", 500)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_directory(self):
        """插入当前文件所在目录路径"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 获取当前文件所在目录
            if hasattr(self, "current_file_path") and self.current_file_path:
                directory = os.path.dirname(self.current_file_path)
                self.text_area.insert(tk.INSERT, directory)

                # 更新状态栏
                self._update_status_bar()
                # 更新字符计数
                self.update_char_count()
                # 更新修改状态
                self.set_modified(True)

                # 显示通知
                self.status_bar.show_notification(f"已插入目录路径: {directory}", 500)
            else:
                self.status_bar.show_notification("没有当前文件", 500)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_date(self, format_type="ymd"):
        """插入当前日期"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 根据格式类型获取日期
            now = datetime.datetime.now()
            if format_type == "ymd":
                date_str = now.strftime("%Y-%m-%d")
            elif format_type == "ymd_slash":
                date_str = now.strftime("%Y/%m/%d")
            elif format_type == "dmy":
                date_str = now.strftime("%d-%m-%Y")
            elif format_type == "dmy_slash":
                date_str = now.strftime("%d/%m/%Y")
            elif format_type == "mdy":
                date_str = now.strftime("%m-%d-%Y")
            elif format_type == "mdy_slash":
                date_str = now.strftime("%m/%d/%Y")
            else:
                date_str = now.strftime("%Y-%m-%d")

            # 在光标位置插入日期
            self.text_area.insert(tk.INSERT, date_str)

            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)

            # 显示通知
            self.status_bar.show_notification(f"已插入日期: {date_str}", 500)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_time(self, format_type="24h"):
        """插入当前时间"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 根据格式类型获取时间
            now = datetime.datetime.now()
            if format_type == "24h":
                time_str = now.strftime("%H:%M:%S")
            elif format_type == "12h":
                time_str = now.strftime("%I:%M:%S %p")
            elif format_type == "24h_short":
                time_str = now.strftime("%H:%M")
            elif format_type == "12h_short":
                time_str = now.strftime("%I:%M %p")
            else:
                time_str = now.strftime("%H:%M:%S")

            # 在光标位置插入时间
            self.text_area.insert(tk.INSERT, time_str)

            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)

            # 显示通知
            self.status_bar.show_notification(f"已插入时间: {time_str}", 500)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_datetime(self, format_type="ymd_24h"):
        """插入当前日期和时间"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 根据格式类型获取日期时间
            now = datetime.datetime.now()
            if format_type == "ymd_24h":
                datetime_str = now.strftime("%Y-%m-%d %H:%M:%S")
            elif format_type == "ymd_12h":
                datetime_str = now.strftime("%Y-%m-%d %I:%M:%S %p")
            elif format_type == "ymd_slash_24h":
                datetime_str = now.strftime("%Y/%m/%d %H:%M:%S")
            elif format_type == "ymd_slash_12h":
                datetime_str = now.strftime("%Y/%m/%d %I:%M:%S %p")
            else:
                datetime_str = now.strftime("%Y-%m-%d %H:%M:%S")

            # 在光标位置插入日期时间
            self.text_area.insert(tk.INSERT, datetime_str)

            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)

            # 显示通知
            self.status_bar.show_notification(f"已插入日期时间: {datetime_str}", 500)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_timestamp(self):
        """插入当前时间戳"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 获取当前时间戳
            timestamp = str(int(datetime.datetime.now().timestamp()))

            # 在光标位置插入时间戳
            self.text_area.insert(tk.INSERT, timestamp)

            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)

            # 显示通知
            self.status_bar.show_notification(f"已插入时间戳: {timestamp}", 500)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_uuid_v4(self):
        """插入UUID v4"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 生成UUID v4
            uuid_str = str(uuid.uuid4())

            # 在光标位置插入UUID
            self.text_area.insert(tk.INSERT, uuid_str)

            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)

            # 显示通知
            self.status_bar.show_notification(f"已插入UUID v4: {uuid_str}", 500)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_uuid_no_hyphens(self):
        """插入无连字符的UUID"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 生成UUID v4并移除连字符
            uuid_str = str(uuid.uuid4()).replace("-", "")

            # 在光标位置插入UUID
            self.text_area.insert(tk.INSERT, uuid_str)

            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)

            # 显示通知
            self.status_bar.show_notification(f"已插入无连字符UUID: {uuid_str}", 500)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_uuid_uppercase(self):
        """插入大写UUID"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 生成UUID v4并转换为大写
            uuid_str = str(uuid.uuid4()).upper()

            # 在光标位置插入UUID
            self.text_area.insert(tk.INSERT, uuid_str)

            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)

            # 显示通知
            self.status_bar.show_notification(f"已插入大写UUID: {uuid_str}", 500)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_uuid_uppercase_no_hyphens(self):
        """插入大写无连字符UUID"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 生成UUID v4，移除连字符并转换为大写
            uuid_str = str(uuid.uuid4()).replace("-", "").upper()

            # 在光标位置插入UUID
            self.text_area.insert(tk.INSERT, uuid_str)

            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)

            # 显示通知
            self.status_bar.show_notification(
                f"已插入大写无连字符UUID: {uuid_str}", 500
            )
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_uuid_with_braces(self):
        """插入带花括号的UUID"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 生成UUID v4并添加花括号
            uuid_str = "{" + str(uuid.uuid4()) + "}"

            # 在光标位置插入UUID
            self.text_area.insert(tk.INSERT, uuid_str)

            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)

            # 显示通知
            self.status_bar.show_notification(f"已插入带花括号的UUID: {uuid_str}", 500)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_uuid_uppercase_with_braces(self):
        """插入带花括号的大写UUID"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 生成UUID v4，转换为大写并添加花括号
            uuid_str = "{" + str(uuid.uuid4()).upper() + "}"

            # 在光标位置插入UUID
            self.text_area.insert(tk.INSERT, uuid_str)

            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)

            # 显示通知
            self.status_bar.show_notification(
                f"已插入带花括号的大写UUID: {uuid_str}", 500
            )
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_uuid_base64(self):
        """插入Base64编码的UUID"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 生成UUID v4并转换为Base64编码
            import base64

            uuid_bytes = uuid.uuid4().bytes
            uuid_str = base64.b64encode(uuid_bytes).decode("utf-8")

            # 在光标位置插入UUID
            self.text_area.insert(tk.INSERT, uuid_str)

            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)

            # 显示通知
            self.status_bar.show_notification(
                f"已插入Base64编码的UUID: {uuid_str}", 500
            )
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_uuid_urn(self):
        """插入URN格式UUID"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 生成URN格式的UUID v4
            uuid_str = "urn:uuid:" + str(uuid.uuid4())

            # 在光标位置插入UUID
            self.text_area.insert(tk.INSERT, uuid_str)

            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)

            # 显示通知
            self.status_bar.show_notification(f"已插入URN格式UUID: {uuid_str}", 500)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_uuid_v1(self):
        """插入UUID v1（基于时间）"""
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 生成UUID v1
            uuid_str = str(uuid.uuid1())

            # 在光标位置插入UUID
            self.text_area.insert(tk.INSERT, uuid_str)

            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)

            # 显示通知
            self.status_bar.show_notification(f"已插入UUID v1: {uuid_str}", 500)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def goto_top(self):
        """转到文件顶部"""
        try:
            # 设置光标位置到文件顶部
            self.text_area.mark_set(tk.INSERT, "1.0")
            # 确保光标可见
            self.text_area.see(tk.INSERT)
            # 更新状态栏
            self._update_status_bar()
            # 显示通知
            self.status_bar.show_notification("已转到文件顶部", 500)
        except Exception as e:
            # 忽略转到顶部操作异常
            pass

    def goto_bottom(self):
        """转到文件底部"""
        try:
            # 设置光标位置到文件底部
            self.text_area.mark_set(tk.INSERT, tk.END)
            # 确保光标可见
            self.text_area.see(tk.INSERT)
            # 更新状态栏
            self._update_status_bar()
            # 显示通知
            self.status_bar.show_notification("已转到文件底部", 500)
        except Exception as e:
            # 忽略转到底部操作异常
            pass

    def page_up(self):
        """向上翻页"""
        try:
            # 使用yview_scroll方法执行向上翻页操作
            self.text_area.yview_scroll(-1, "pages")
            self.text_area.focus_set()
            # 更新状态栏
            self._update_status_bar()
        except Exception as e:
            # 忽略向上翻页操作异常
            pass

    def page_down(self):
        """向下翻页"""
        try:
            # 使用yview_scroll方法执行向下翻页操作
            self.text_area.yview_scroll(1, "pages")
            self.text_area.focus_set()
            # 更新状态栏
            self._update_status_bar()
        except Exception as e:
            # 忽略向下翻页操作异常
            pass

    def clear_clipboard(self):
        """清空剪贴板"""
        try:
            # 清空剪贴板
            self.clipboard_clear()
            # 显示通知
            self.status_bar.show_notification("剪贴板已清空", 500)
        except Exception as e:
            # 忽略清空剪贴板操作异常
            pass

    def copy_filename_to_clipboard(self):
        """复制文件名到剪贴板"""
        try:
            if self.current_file_path:
                # 获取文件名
                filename = os.path.basename(self.current_file_path)
                # 清空剪贴板
                self.clipboard_clear()
                # 添加文件名到剪贴板
                self.clipboard_append(filename)
                # 显示通知
                self.status_bar.show_notification(f"已复制文件名: {filename}", 500)
            else:
                self.status_bar.show_notification("当前没有打开的文件", 500)
        except Exception as e:
            # 忽略复制文件名操作异常
            pass

    def copy_filepath_to_clipboard(self):
        """复制文件路径到剪贴板"""
        try:
            if self.current_file_path:
                # 清空剪贴板
                self.clipboard_clear()
                # 添加文件路径到剪贴板
                self.clipboard_append(self.current_file_path)
                # 显示通知
                self.status_bar.show_notification(
                    f"已复制文件路径: {self.current_file_path}", 500
                )
            else:
                self.status_bar.show_notification("当前没有打开的文件", 500)
        except Exception as e:
            # 忽略复制文件路径操作异常
            pass

    def copy_directory_to_clipboard(self):
        """复制文件所在目录路径到剪贴板"""
        try:
            if self.current_file_path:
                # 获取文件所在目录路径
                directory_path = os.path.dirname(self.current_file_path)
                # 清空剪贴板
                self.clipboard_clear()
                # 添加目录路径到剪贴板
                self.clipboard_append(directory_path)
                # 显示通知
                self.status_bar.show_notification(
                    f"已复制目录路径: {directory_path}", 500
                )
            else:
                self.status_bar.show_notification("当前没有打开的文件", 500)
        except Exception as e:
            # 忽略复制目录路径操作异常
            pass

    def copy_selected_text_info(self):
        """复制选中文本的信息（字符数、行数）"""
        try:
            # 检查是否有选中的文本
            try:
                selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
                if selected_text:
                    # 计算字符数和行数
                    char_count = len(selected_text)
                    line_count = selected_text.count("\n") + 1
                    # 构建信息文本
                    info_text = (
                        f"选中文本信息:\n字符数: {char_count}\n行数: {line_count}"
                    )
                    # 清空剪贴板
                    self.clipboard_clear()
                    # 添加信息到剪贴板
                    self.clipboard_append(info_text)
                    # 显示通知
                    self.status_bar.show_notification(
                        f"已复制选中文本信息: {char_count} 个字符, {line_count} 行",
                        500,
                    )
                else:
                    self.status_bar.show_notification("没有选中的文本", 500)
            except tk.TclError:
                # 没有选中文本
                self.status_bar.show_notification("没有选中的文本", 500)
        except Exception as e:
            # 忽略复制选中文本信息操作异常
            pass

    def goto_line(self):
        """
        转到指定行

        弹出对话框让用户输入行号，然后跳转到指定行
        """
        # 获取组件字体配置
        font_config = config_manager.get_font_config("components")
        font_family = font_config.get("font", "Microsoft YaHei UI")
        font_size = 15
        font_weight = "bold"

        # 创建自定义对话框窗口
        dialog = ctk.CTkToplevel(self)
        dialog.title("转到行")
        dialog.geometry("350x150")
        dialog.resizable(False, False)

        # 设置窗口模态
        dialog.transient(self)
        dialog.grab_set()

        # 创建输入框和标签
        frame = ctk.CTkFrame(dialog)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        label = ctk.CTkLabel(
            frame, text="请输入行号:", font=(font_family, font_size, font_weight)
        )
        label.pack(pady=(0, 10))

        entry = ctk.CTkEntry(frame, font=(font_family, font_size, font_weight))
        entry.pack(pady=(0, 10), fill="x")
        entry.focus_set()

        # 按钮框架
        button_frame = ctk.CTkFrame(frame)
        button_frame.pack(fill="x")

        def on_ok():
            """确认按钮处理函数"""
            try:
                line_num = int(entry.get())
                # 跳转到指定行
                self.text_area.mark_set("insert", f"{line_num}.0")
                self.text_area.see("insert")
                # 更新状态栏
                self._update_status_bar()
                # 关闭对话框
                dialog.destroy()
            except ValueError:
                # 显示错误消息
                error_dialog = ctk.CTkToplevel(dialog)
                error_dialog.title("错误")
                error_dialog.geometry("250x100")
                error_dialog.resizable(False, False)

                error_label = ctk.CTkLabel(
                    error_dialog,
                    text="请输入有效的行号",
                    font=(font_family, font_size, font_weight),
                )
                error_label.pack(pady=20)

                ok_button = ctk.CTkButton(
                    error_dialog,
                    text="确定",
                    font=(font_family, font_size, font_weight),
                    command=error_dialog.destroy,
                )
                ok_button.pack(pady=10)

        def on_cancel():
            """取消按钮处理函数"""
            dialog.destroy()

        # 创建按钮
        ok_button = ctk.CTkButton(
            button_frame,
            text="确定",
            font=(font_family, font_size, font_weight),
            command=on_ok,
        )
        ok_button.pack(side="left", padx=(0, 10), fill="x", expand=True)

        cancel_button = ctk.CTkButton(
            button_frame,
            text="取消",
            font=(font_family, font_size, font_weight),
            command=on_cancel,
        )
        cancel_button.pack(side="right", fill="x", expand=True)

        # 绑定回车键
        entry.bind("<Return>", lambda e: on_ok())

        # 绑定ESC键
        dialog.bind("<Escape>", lambda e: on_cancel())

        # 居中显示对话框
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        # 在对话框完全显示后设置焦点
        dialog.after(100, entry.focus_set)

    def insert_special_character(self, char_type, char_value):
        """
        插入特殊字符

        Args:
            char_type (str): 字符类型
            char_value (str): 字符值
        """
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 插入特殊字符
            self.text_area.insert(tk.INSERT, char_value)

            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)

            # 显示通知
            self.status_bar.show_notification(f"已插入{char_type}: {char_value}", 500)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_copyright_symbol(self):
        """插入版权符号 ©"""
        self.insert_special_character("版权符号", "©")

    def insert_trademark_symbol(self):
        """插入商标符号 ®"""
        self.insert_special_character("商标符号", "®")

    def insert_registered_trademark_symbol(self):
        """插入注册商标符号 ™"""
        self.insert_special_character("注册商标符号", "™")

    def insert_degree_symbol(self):
        """插入度数符号 °"""
        self.insert_special_character("度数符号", "°")

    def insert_euro_symbol(self):
        """插入欧元符号 €"""
        self.insert_special_character("欧元符号", "€")

    def insert_pound_symbol(self):
        """插入英镑符号 £"""
        self.insert_special_character("英镑符号", "£")

    def insert_yen_symbol(self):
        """插入日元符号 ¥"""
        self.insert_special_character("日元符号", "¥")

    def insert_section_symbol(self):
        """插入章节符号 §"""
        self.insert_special_character("章节符号", "§")

    def insert_paragraph_symbol(self):
        """插入段落符号 ¶"""
        self.insert_special_character("段落符号", "¶")

    def insert_ellipsis_symbol(self):
        """插入省略号 …"""
        self.insert_special_character("省略号", "…")

    def insert_dagger_symbol(self):
        """插入匕首符号 †"""
        self.insert_special_character("匕首符号", "†")

    def insert_double_dagger_symbol(self):
        """插入双匕首符号 ‡"""
        self.insert_special_character("双匕首符号", "‡")

    def insert_bullet_symbol(self):
        """插入圆点符号 •"""
        self.insert_special_character("圆点符号", "•")

    def insert_mathematical_symbol(self, symbol_type, symbol_value):
        """
        插入数学符号

        Args:
            symbol_type (str): 符号类型
            symbol_value (str): 符号值
        """
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 插入数学符号
            self.text_area.insert(tk.INSERT, symbol_value)

            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)

            # 显示通知
            self.status_bar.show_notification(
                f"已插入{symbol_type}: {symbol_value}", 500
            )
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_plus_minus_symbol(self):
        """插入正负号 ±"""
        self.insert_mathematical_symbol("正负号", "±")

    def insert_not_equal_symbol(self):
        """插入不等号 ≠"""
        self.insert_mathematical_symbol("不等号", "≠")

    def insert_less_than_or_equal_symbol(self):
        """插入小于等于号 ≤"""
        self.insert_mathematical_symbol("小于等于号", "≤")

    def insert_greater_than_or_equal_symbol(self):
        """插入大于等于号 ≥"""
        self.insert_mathematical_symbol("大于等于号", "≥")

    def insert_infinity_symbol(self):
        """插入无穷符号 ∞"""
        self.insert_mathematical_symbol("无穷符号", "∞")

    def insert_summation_symbol(self):
        """插入求和符号 ∑"""
        self.insert_mathematical_symbol("求和符号", "∑")

    def insert_product_symbol(self):
        """插入乘积符号 ∏"""
        self.insert_mathematical_symbol("乘积符号", "∏")

    def insert_integral_symbol(self):
        """插入积分符号 ∫"""
        self.insert_mathematical_symbol("积分符号", "∫")

    def insert_partial_derivative_symbol(self):
        """插入偏导数符号 ∂"""
        self.insert_mathematical_symbol("偏导数符号", "∂")

    def insert_nabla_symbol(self):
        """插入梯度符号 ∇"""
        self.insert_mathematical_symbol("梯度符号", "∇")

    def insert_square_root_symbol(self):
        """插入平方根符号 √"""
        self.insert_mathematical_symbol("平方根符号", "√")

    def insert_cubic_root_symbol(self):
        """插入立方根符号 ∛"""
        self.insert_mathematical_symbol("立方根符号", "∛")

    def insert_fourth_root_symbol(self):
        """插入四次根符号 ∜"""
        self.insert_mathematical_symbol("四次根符号", "∜")

    def insert_alpha_symbol(self):
        """插入希腊字母 α"""
        self.insert_mathematical_symbol("希腊字母α", "α")

    def insert_beta_symbol(self):
        """插入希腊字母 β"""
        self.insert_mathematical_symbol("希腊字母β", "β")

    def insert_gamma_symbol(self):
        """插入希腊字母 γ"""
        self.insert_mathematical_symbol("希腊字母γ", "γ")

    def insert_delta_symbol(self):
        """插入希腊字母 δ"""
        self.insert_mathematical_symbol("希腊字母δ", "δ")

    def insert_epsilon_symbol(self):
        """插入希腊字母 ε"""
        self.insert_mathematical_symbol("希腊字母ε", "ε")

    def insert_zeta_symbol(self):
        """插入希腊字母 ζ"""
        self.insert_mathematical_symbol("希腊字母ζ", "ζ")

    def insert_eta_symbol(self):
        """插入希腊字母 η"""
        self.insert_mathematical_symbol("希腊字母η", "η")

    def insert_theta_symbol(self):
        """插入希腊字母 θ"""
        self.insert_mathematical_symbol("希腊字母θ", "θ")

    def insert_iota_symbol(self):
        """插入希腊字母 ι"""
        self.insert_mathematical_symbol("希腊字母ι", "ι")

    def insert_kappa_symbol(self):
        """插入希腊字母 κ"""
        self.insert_mathematical_symbol("希腊字母κ", "κ")

    def insert_lambda_symbol(self):
        """插入希腊字母 λ"""
        self.insert_mathematical_symbol("希腊字母λ", "λ")

    def insert_mu_symbol(self):
        """插入希腊字母 μ"""
        self.insert_mathematical_symbol("希腊字母μ", "μ")

    def insert_nu_symbol(self):
        """插入希腊字母 ν"""
        self.insert_mathematical_symbol("希腊字母ν", "ν")

    def insert_xi_symbol(self):
        """插入希腊字母 ξ"""
        self.insert_mathematical_symbol("希腊字母ξ", "ξ")

    def insert_omicron_symbol(self):
        """插入希腊字母 ο"""
        self.insert_mathematical_symbol("希腊字母ο", "ο")

    def insert_pi_symbol(self):
        """插入希腊字母 π"""
        self.insert_mathematical_symbol("希腊字母π", "π")

    def insert_rho_symbol(self):
        """插入希腊字母 ρ"""
        self.insert_mathematical_symbol("希腊字母ρ", "ρ")

    def insert_sigma_symbol(self):
        """插入希腊字母 σ"""
        self.insert_mathematical_symbol("希腊字母σ", "σ")

    def insert_tau_symbol(self):
        """插入希腊字母 τ"""
        self.insert_mathematical_symbol("希腊字母τ", "τ")

    def insert_upsilon_symbol(self):
        """插入希腊字母 υ"""
        self.insert_mathematical_symbol("希腊字母υ", "υ")

    def insert_phi_symbol(self):
        """插入希腊字母 φ"""
        self.insert_mathematical_symbol("希腊字母φ", "φ")

    def insert_chi_symbol(self):
        """插入希腊字母 χ"""
        self.insert_mathematical_symbol("希腊字母χ", "χ")

    def insert_psi_symbol(self):
        """插入希腊字母 ψ"""
        self.insert_mathematical_symbol("希腊字母ψ", "ψ")

    def insert_omega_symbol(self):
        """插入希腊字母 ω"""
        self.insert_mathematical_symbol("希腊字母ω", "ω")

    def insert_capital_alpha_symbol(self):
        """插入大写希腊字母 Α"""
        self.insert_mathematical_symbol("大写希腊字母Α", "Α")

    def insert_capital_beta_symbol(self):
        """插入大写希腊字母 Β"""
        self.insert_mathematical_symbol("大写希腊字母Β", "Β")

    def insert_capital_gamma_symbol(self):
        """插入大写希腊字母 Γ"""
        self.insert_mathematical_symbol("大写希腊字母Γ", "Γ")

    def insert_capital_delta_symbol(self):
        """插入大写希腊字母 Δ"""
        self.insert_mathematical_symbol("大写希腊字母Δ", "Δ")

    def insert_capital_epsilon_symbol(self):
        """插入大写希腊字母 Ε"""
        self.insert_mathematical_symbol("大写希腊字母Ε", "Ε")

    def insert_capital_zeta_symbol(self):
        """插入大写希腊字母 Ζ"""
        self.insert_mathematical_symbol("大写希腊字母Ζ", "Ζ")

    def insert_capital_eta_symbol(self):
        """插入大写希腊字母 Η"""
        self.insert_mathematical_symbol("大写希腊字母Η", "Η")

    def insert_capital_theta_symbol(self):
        """插入大写希腊字母 Θ"""
        self.insert_mathematical_symbol("大写希腊字母Θ", "Θ")

    def insert_capital_iota_symbol(self):
        """插入大写希腊字母 Ι"""
        self.insert_mathematical_symbol("大写希腊字母Ι", "Ι")

    def insert_capital_kappa_symbol(self):
        """插入大写希腊字母 Κ"""
        self.insert_mathematical_symbol("大写希腊字母Κ", "Κ")

    def insert_capital_lambda_symbol(self):
        """插入大写希腊字母 Λ"""
        self.insert_mathematical_symbol("大写希腊字母Λ", "Λ")

    def insert_capital_mu_symbol(self):
        """插入大写希腊字母 Μ"""
        self.insert_mathematical_symbol("大写希腊字母Μ", "Μ")

    def insert_capital_nu_symbol(self):
        """插入大写希腊字母 Ν"""
        self.insert_mathematical_symbol("大写希腊字母Ν", "Ν")

    def insert_capital_xi_symbol(self):
        """插入大写希腊字母 Ξ"""
        self.insert_mathematical_symbol("大写希腊字母Ξ", "Ξ")

    def insert_capital_omicron_symbol(self):
        """插入大写希腊字母 Ο"""
        self.insert_mathematical_symbol("大写希腊字母Ο", "Ο")

    def insert_capital_pi_symbol(self):
        """插入大写希腊字母 Π"""
        self.insert_mathematical_symbol("大写希腊字母Π", "Π")

    def insert_capital_rho_symbol(self):
        """插入大写希腊字母 Ρ"""
        self.insert_mathematical_symbol("大写希腊字母Ρ", "Ρ")

    def insert_capital_sigma_symbol(self):
        """插入大写希腊字母 Σ"""
        self.insert_mathematical_symbol("大写希腊字母Σ", "Σ")

    def insert_capital_tau_symbol(self):
        """插入大写希腊字母 Τ"""
        self.insert_mathematical_symbol("大写希腊字母Τ", "Τ")

    def insert_capital_upsilon_symbol(self):
        """插入大写希腊字母 Υ"""
        self.insert_mathematical_symbol("大写希腊字母Υ", "Υ")

    def insert_capital_phi_symbol(self):
        """插入大写希腊字母 Φ"""
        self.insert_mathematical_symbol("大写希腊字母Φ", "Φ")

    def insert_capital_chi_symbol(self):
        """插入大写希腊字母 Χ"""
        self.insert_mathematical_symbol("大写希腊字母Χ", "Χ")

    def insert_capital_psi_symbol(self):
        """插入大写希腊字母 Ψ"""
        self.insert_mathematical_symbol("大写希腊字母Ψ", "Ψ")

    def insert_capital_omega_symbol(self):
        """插入大写希腊字母 Ω"""
        self.insert_mathematical_symbol("大写希腊字母Ω", "Ω")

    def insert_color_code(self, code_type, code_value):
        """
        插入颜色代码

        Args:
            code_type (str): 代码类型
            code_value (str): 代码值
        """
        try:
            # 检查是否为只读模式
            if self.is_read_only:
                self.status_bar.show_notification("当前为只读模式，无法插入", 500)
                return

            # 插入颜色代码
            self.text_area.insert(tk.INSERT, code_value)

            # 更新状态栏
            self._update_status_bar()
            # 更新字符计数
            self.update_char_count()
            # 更新修改状态
            self.set_modified(True)

            # 显示通知
            self.status_bar.show_notification(f"已插入{code_type}: {code_value}", 500)
        except Exception as e:
            # 忽略插入操作异常
            pass

    def insert_hex_color_picker(self):
        """插入HEX颜色代码选择器"""
        # 显示颜色选择器对话框
        color_code = show_color_picker(self)

        # 如果用户选择了颜色，则插入颜色代码
        if color_code:
            self.insert_color_code("HEX颜色代码", color_code)

    def insert_rgb_color_picker(self):
        """插入RGB颜色代码选择器"""
        # 获取组件字体配置
        font_config = config_manager.get_font_config("components")
        font_family = font_config.get("font", "Microsoft YaHei UI")
        font_size = 15
        font_weight = "bold"

        # 创建自定义对话框窗口
        dialog = ctk.CTkToplevel(self)
        dialog.title("RGB颜色代码选择器")
        dialog.geometry("400x500")
        dialog.resizable(False, False)

        # 设置窗口模态
        dialog.transient(self)
        dialog.grab_set()

        # 创建主框架
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # 标题标签
        title_label = ctk.CTkLabel(
            main_frame, text="选择颜色", font=(font_family, font_size, font_weight)
        )
        title_label.pack(pady=(0, 10))

        # 颜色预览框架
        preview_frame = ctk.CTkFrame(main_frame)
        preview_frame.pack(fill="x", pady=(0, 10))

        # 颜色预览标签
        preview_label = ctk.CTkLabel(
            preview_frame,
            text="颜色预览",
            font=(font_family, font_size - 2, font_weight),
        )
        preview_label.pack(side="left", padx=(10, 20))

        # 颜色预览框
        color_preview = ctk.CTkLabel(preview_frame, text="", width=100, height=30)
        color_preview.pack(side="left", padx=(0, 10))
        color_preview.configure(fg_color="#000000")

        # RGB代码显示标签
        rgb_label = ctk.CTkLabel(
            preview_frame, text="rgb(0, 0, 0)", font=(font_family, font_size - 2)
        )
        rgb_label.pack(side="left")

        # RGB滑块框架
        slider_frame = ctk.CTkFrame(main_frame)
        slider_frame.pack(fill="both", expand=True, pady=(0, 10))

        # 红色滑块
        red_label = ctk.CTkLabel(
            slider_frame,
            text="红色 (R):",
            font=(font_family, font_size - 2, font_weight),
        )
        red_label.pack(anchor="w", padx=(10, 0), pady=(10, 0))

        red_slider = ctk.CTkSlider(slider_frame, from_=0, to=255, number_of_steps=255)
        red_slider.pack(fill="x", padx=(10, 10), pady=(0, 5))
        red_slider.set(0)

        red_value_label = ctk.CTkLabel(
            slider_frame, text="0", font=(font_family, font_size - 2)
        )
        red_value_label.pack(anchor="e", padx=(0, 10))

        # 绿色滑块
        green_label = ctk.CTkLabel(
            slider_frame,
            text="绿色 (G):",
            font=(font_family, font_size - 2, font_weight),
        )
        green_label.pack(anchor="w", padx=(10, 0), pady=(10, 0))

        green_slider = ctk.CTkSlider(slider_frame, from_=0, to=255, number_of_steps=255)
        green_slider.pack(fill="x", padx=(10, 10), pady=(0, 5))
        green_slider.set(0)

        green_value_label = ctk.CTkLabel(
            slider_frame, text="0", font=(font_family, font_size - 2)
        )
        green_value_label.pack(anchor="e", padx=(0, 10))

        # 蓝色滑块
        blue_label = ctk.CTkLabel(
            slider_frame,
            text="蓝色 (B):",
            font=(font_family, font_size - 2, font_weight),
        )
        blue_label.pack(anchor="w", padx=(10, 0), pady=(10, 0))

        blue_slider = ctk.CTkSlider(slider_frame, from_=0, to=255, number_of_steps=255)
        blue_slider.pack(fill="x", padx=(10, 10), pady=(0, 5))
        blue_slider.set(0)

        blue_value_label = ctk.CTkLabel(
            slider_frame, text="0", font=(font_family, font_size - 2)
        )
        blue_value_label.pack(anchor="e", padx=(0, 10))

        def update_color():
            """更新颜色预览和RGB代码"""
            r = int(red_slider.get())
            g = int(green_slider.get())
            b = int(blue_slider.get())

            # 更新值标签
            red_value_label.configure(text=str(r))
            green_value_label.configure(text=str(g))
            blue_value_label.configure(text=str(b))

            # 转换为HEX
            hex_color = f"#{r:02x}{g:02x}{b:02x}"

            # 更新预览
            color_preview.configure(fg_color=hex_color)

            # 更新RGB代码
            rgb_label.configure(text=f"rgb({r}, {g}, {b})")

        # 绑定滑块事件
        red_slider.configure(command=lambda v: update_color())
        green_slider.configure(command=lambda v: update_color())
        blue_slider.configure(command=lambda v: update_color())

        # 按钮框架
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x")

        def on_ok():
            """确认按钮处理函数"""
            rgb_code = rgb_label.cget("text")
            self.insert_color_code("RGB颜色代码", rgb_code)
            dialog.destroy()

        def on_cancel():
            """取消按钮处理函数"""
            dialog.destroy()

        # 创建按钮
        ok_button = ctk.CTkButton(
            button_frame,
            text="确定",
            font=(font_family, font_size, font_weight),
            command=on_ok,
        )
        ok_button.pack(side="left", padx=(0, 10), fill="x", expand=True)

        cancel_button = ctk.CTkButton(
            button_frame,
            text="取消",
            font=(font_family, font_size, font_weight),
            command=on_cancel,
        )
        cancel_button.pack(side="right", fill="x", expand=True)

        # 居中显示对话框
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
