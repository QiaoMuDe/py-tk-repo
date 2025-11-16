# 这是一个测试文件
import os
import sys


def hello_world():
    """打印hello world"""
    name = "world"
    print(f"Hello, {name}!")  # 注释测试

    if name:
        for i in range(5):
            print(i)
    else:
        print("No name")


class TestClass:
    def __init__(self):
        self.value = 42

    def get_value(self):
        return self.value


# 测试字符串和注释
string_test = "这是一个字符串"
another_string = "这也是一个字符串"
