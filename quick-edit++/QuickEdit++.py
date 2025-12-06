#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QuickEdit++ 主程序入口
"""

import sys
import os
import argparse
import traceback
from app.editor import QuickEditApp
from loguru import logger


def handle_exception(exc_type, exc_value, exc_traceback):
    """
    全局异常处理函数，捕获未处理的异常并记录日志，防止程序意外退出

    Args:
        exc_type: 异常类型
        exc_value: 异常值
        exc_traceback: 异常追踪信息
    """
    if issubclass(exc_type, KeyboardInterrupt):
        # 允许Ctrl+C正常退出
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # 记录异常到日志
    logger.critical("未处理的异常", exc_info=(exc_type, exc_value, exc_traceback))

    # 打印友好的错误信息
    error_msg = f"程序遇到错误: {exc_type.__name__}: {exc_value}"
    print(error_msg, file=sys.stderr)

    # 在开发环境中可以选择显示详细错误信息
    if os.environ.get("QUICKEDIT_DEBUG", "0") == "1":
        traceback.print_exception(exc_type, exc_value, exc_traceback)


def main():
    """主函数"""
    # 设置全局异常处理
    sys.excepthook = handle_exception

    # 获取运行时程序名（去掉扩展名）
    program_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]

    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description=f"{program_name} - 轻量级文本编辑器")
    parser.add_argument("file", nargs="?", help="要打开的文件路径")

    # 解析命令行参数
    args = parser.parse_args()

    # 检查是否有多个参数
    if len(sys.argv) > 2:
        print("error: 只支持打开单个文件，请一次只提供一个文件路径")
        sys.exit(1)

    # 创建并运行应用
    try:
        app = QuickEditApp()

        # 初始化拖拽功能
        app.init_drag_drop()

        # 如果提供了文件路径参数
        if args.file:
            # 检查路径是否存在
            if os.path.exists(args.file):
                # 检查是否是目录
                if os.path.isdir(args.file):
                    print("error: 无法打开目录")
                    sys.exit(1)

                # 文件存在，直接打开
                app.open_file_with_path(args.file)
            else:
                # 文件不存在，检查上级目录是否存在
                dir_path = os.path.dirname(args.file)
                if dir_path and not os.path.exists(dir_path):
                    print("error: 上级目录不存在")
                    sys.exit(1)

                # 作为新文件创建
                try:
                    # 先创建空文件
                    with open(args.file, "w", encoding="utf-8") as f:
                        f.write("")
                    # 然后通过文件操作打开它
                    app.open_file_with_path(args.file)
                except Exception as e:
                    print(f"error: 无法创建文件: {args.file}，错误信息: {str(e)}")
                    logger.error(f"无法创建文件: {args.file}，错误信息: {str(e)}")
                    sys.exit(1)

        # 运行应用
        app.run()

    except Exception as e:
        logger.error(f"应用程序运行时发生错误: {str(e)}")
        print(f"应用程序运行时发生错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
