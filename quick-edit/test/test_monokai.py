# 这是一个用于测试Monokai Dimmed配色方案的Python文件
# 注释应该显示为灰色 (#999999)

import os  # import关键字应该显示为紫色 (#AE81FF)
import sys


def hello_world():  # def关键字应该显示为紫色 (#AE81FF)
    """这是一个示例函数"""
    # 字符串应该显示为米黄色 (#E6DB74)
    message = "Hello, Monokai Dimmed!"
    print(message)  # print是内置函数，应该显示为粉红色 (#F92672)

    # 数字
    number = 42

    # 条件语句
    if number > 0:  # if关键字应该显示为紫色 (#AE81FF)
        return True
    else:  # else关键字应该显示为紫色 (#AE81FF)
        return False


class MyClass:  # class关键字应该显示为紫色 (#AE81FF)
    def __init__(self):  # __init__是内置方法，应该显示为粉红色 (#F92672)
        self.value = 0


# TODO: 这是一个待办事项，应该显示为橙黄色 (#FD971F)
# 这里有一些需要完成的任务

# ERROR: 这是一个错误标记，应该显示为粉红色 (#F92672)
# 这里标记了一些错误或需要注意的地方

# 测试各种语法元素
try:
    result = 10 / 0  # 除零错误
except ZeroDivisionError:  # except关键字应该显示为紫色 (#AE81FF)
    print("不能除以零")  # print是内置函数，应该显示为粉红色 (#F92672)

# 列表和字典
my_list = [1, 2, 3]  # 列表
my_dict = {"key": "value"}  # 字典

# 循环
for i in range(5):  # for关键字应该显示为紫色 (#AE81FF)
    print(i)  # print是内置函数，应该显示为粉红色 (#F92672)
