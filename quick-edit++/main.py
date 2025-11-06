#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QuickEdit++ 主程序入口
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.editor import QuickEditApp


def main():
    """主函数"""
    # 创建并运行应用
    app = QuickEditApp()
    app.run()


if __name__ == "__main__":
    main()