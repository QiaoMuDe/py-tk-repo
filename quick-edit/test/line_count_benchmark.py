#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
行数统计方法性能测试
"""

import time
import random
import string

def generate_test_content(lines, avg_line_length=50):
    """生成测试内容"""
    content = []
    for _ in range(lines):
        line_length = random.randint(1, avg_line_length * 2)
        line = ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=line_length))
        content.append(line)
    return '\n'.join(content)

def count_lines_split(content):
    """使用split方法统计行数"""
    return len(content.split('\n'))

def count_lines_count(content):
    """使用count方法统计行数"""
    return content.count('\n') + 1

def count_lines_manual(content):
    """手动遍历统计行数"""
    count = 1  # 至少有一行
    for char in content:
        if char == '\n':
            count += 1
    return count

def count_lines_sum(content):
    """使用sum和生成器表达式统计行数"""
    return sum(1 for char in content if char == '\n') + 1

def benchmark_methods(content, iterations=1000):
    """测试不同方法的性能"""
    methods = [
        ("split方法", count_lines_split),
        ("count方法", count_lines_count),
        ("手动遍历", count_lines_manual),
        ("sum+生成器", count_lines_sum)
    ]
    
    results = {}
    
    for name, method in methods:
        start_time = time.time()
        for _ in range(iterations):
            result = method(content)
        end_time = time.time()
        elapsed = end_time - start_time
        results[name] = elapsed
        print(f"{name}: {elapsed:.4f}秒 (结果: {result})")
    
    return results

def main():
    """主函数"""
    print("生成测试数据...")
    # 测试不同大小的文件
    test_sizes = [1000, 10000, 100000]
    
    for size in test_sizes:
        print(f"\n=== 测试文件大小: {size} 行 ===")
        content = generate_test_content(size)
        
        print(f"实际字符数: {len(content)}")
        print("性能测试结果:")
        results = benchmark_methods(content, 100)
        
        # 找出最快的方法
        fastest = min(results.items(), key=lambda x: x[1])
        print(f"最快方法: {fastest[0]} ({fastest[1]:.4f}秒)")

if __name__ == "__main__":
    main()