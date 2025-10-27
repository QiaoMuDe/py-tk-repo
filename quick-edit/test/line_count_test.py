#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
行数统计方法正确性测试
"""

def count_lines_split(content):
    """使用split方法统计行数"""
    return len(content.split('\n'))

def count_lines_count(content):
    """使用count方法统计行数"""
    return content.count('\n') + 1

def test_line_counting():
    """测试行数统计方法"""
    test_cases = [
        ("", 1),  # 空字符串应该有1行
        ("hello", 1),  # 单行无换行符
        ("hello\n", 2),  # 一行加换行符
        ("hello\nworld", 2),  # 两行
        ("hello\nworld\n", 3),  # 两行加末尾换行符
        ("line1\nline2\nline3", 3),  # 三行
        ("line1\nline2\nline3\n", 4),  # 三行加末尾换行符
        ("\n", 2),  # 只有一个换行符
        ("\n\n", 3),  # 两个换行符
        ("a\nb\nc\nd\ne", 5),  # 五行
    ]
    
    print("测试行数统计方法:")
    print("内容 -> 期望行数 | split方法 | count方法 | 结果")
    print("-" * 50)
    
    all_passed = True
    for content, expected in test_cases:
        split_result = count_lines_split(content)
        count_result = count_lines_count(content)
        
        split_correct = "✓" if split_result == expected else "✗"
        count_correct = "✓" if count_result == expected else "✗"
        overall_correct = "✓" if (split_result == expected and count_result == expected) else "✗"
        
        if split_result != expected or count_result != expected:
            all_passed = False
            
        # 显示内容时处理空字符串和换行符的可视化
        display_content = content.replace('\n', '\\n')
        if display_content == "":
            display_content = "(空)"
            
        print(f"{display_content:>10} -> {expected:>2} | {split_result:>2} {split_correct} | {count_result:>2} {count_correct} | {overall_correct}")
    
    print("-" * 50)
    if all_passed:
        print("所有测试通过! 两种方法结果一致。")
    else:
        print("部分测试失败! 方法结果不一致。")
        
    return all_passed

if __name__ == "__main__":
    test_line_counting()