#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QuickEdit++ 主程序入口
"""

import sys
import os
import argparse

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.editor import QuickEditApp


def main():
    """主函数"""
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='QuickEdit++ - 轻量级文本编辑器')
    parser.add_argument('file', nargs='?', help='要打开的文件路径')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 检查是否有多个参数
    if len(sys.argv) > 2:
        print("error: 只支持打开单个文件，请一次只提供一个文件路径")
        sys.exit(1)
    
    # 创建并运行应用
    app = QuickEditApp()
    
    # 初始化拖拽功能
    app.init_drag_drop()
    
    # 如果提供了文件路径参数
    if args.file:
        # 检查路径是否存在
        if os.path.exists(args.file):
            # 检查是否是目录
            if os.path.isdir(args.file):
                print(f"error: 无法打开目录: {args.file}")
                sys.exit(1)
            
            # 文件存在，直接打开
            app.open_file_with_path(args.file)
        else:
            # 文件不存在，检查上级目录是否存在
            dir_path = os.path.dirname(args.file)
            if dir_path and not os.path.exists(dir_path):
                print(f"error: 上级目录不存在: {dir_path}")
                sys.exit(1)
            
            # 作为新文件创建
            app.new_file_with_path(args.file)
    
    app.run()


if __name__ == "__main__":
    main()