#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QuickEdit++ Nuitka构建脚本
使用Nuitka打包应用程序，并可选择使用7z进行压缩
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_command_exists(command):
    """检查命令是否存在于系统PATH中"""
    cmd_path = shutil.which(command)
    return cmd_path is not None, cmd_path


def get_git_version():
    """获取Git版本信息"""
    try:
        # 检查是否是Git仓库
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

        # 获取最新标签
        tag_result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # 获取当前提交的简短哈希
        hash_result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if tag_result.returncode == 0 and hash_result.returncode == 0:
            tag = tag_result.stdout.strip()
            commit_hash = hash_result.stdout.strip()
            return f"{tag}-{commit_hash}"
        elif tag_result.returncode == 0:
            return tag_result.stdout.strip()
        else:
            return "unknown"
    except subprocess.CalledProcessError:
        return None


def run_command(command, description):
    """运行命令并处理结果"""
    print(f"正在执行: {description}")
    print(f"命令: {' '.join(command)}")

    try:
        # 不捕获输出，直接显示在当前终端
        result = subprocess.run(command, check=True)
        print(f"\n{description}成功完成!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n{description}失败!")
        print(f"错误代码: {e.returncode}")
        return False


def main():
    """主函数"""
    try:
        print("=== QuickEdit++ Nuitka构建脚本 ===\n")

        # 检查Nuitka
        print("检查必要工具...")
        nuitka_exists, nuitka_path = check_command_exists("nuitka")
        if not nuitka_exists:
            print("错误: 找不到nuitka，请确保已安装Nuitka")
            print("安装命令: pip install nuitka")
            input("按回车键退出...")
            return 1

        print(f"找到nuitka: {nuitka_path}")

        # 检查7z
        use_7z, seven_zip_path = check_command_exists("7z")

        if use_7z:
            print("找到7z，将进行压缩打包")
        else:
            print("警告: 找不到7z，将跳过压缩步骤")
            print("如需压缩，请安装7-Zip: https://www.7-zip.org/")

        # 检查Git工具和仓库
        git_version = None
        git_exists, git_path = check_command_exists("git")
        if git_exists:
            print(f"找到Git工具: {git_path}")
            print("检查版本信息...")
            git_version = get_git_version()
            if git_version:
                print(f"Git版本信息: {git_version}")
            else:
                print("当前目录不是Git仓库或无法获取版本信息")
        else:
            print("未找到Git工具")

        # 获取脚本目录
        script_dir = Path(__file__).parent
        os.chdir(script_dir)

        # 构建Nuitka命令
        icon_path = script_dir / "icons" / "QuickEdit++.ico"
        main_script = script_dir / "QuickEdit++.py"

        nuitka_cmd = [
            nuitka_path,  # 使用完整路径
            "--standalone",  # 创建独立可执行文件
            "--windows-console-mode=disable",  # 禁用控制台窗口
            "--enable-plugin=tk-inter",  # 启用tkinter插件
            f"--windows-icon-from-ico={icon_path}",  # 设置图标
            str(main_script),
        ]

        # 执行编译
        print("\n开始编译 QuickEdit++...")
        if not run_command(nuitka_cmd, "Nuitka编译"):
            input("按回车键退出...")
            return 1

        # 重命名输出目录
        print("\n重命名输出目录...")
        dist_dir = script_dir / "QuickEdit++.dist"
        target_dir = script_dir / "QuickEdit++"

        try:
            if target_dir.exists():
                import shutil

                shutil.rmtree(target_dir)

            if dist_dir.exists():
                dist_dir.rename(target_dir)
                print("目录重命名成功!")
            else:
                print("警告: 找不到Nuitka输出目录")
        except Exception as e:
            print(f"重命名目录失败: {e}")
            input("按回车键退出...")
            return 1

        # 如果7z可用，则进行压缩
        if use_7z:
            print("\n开始打包...")

            # 根据Git版本信息生成压缩文件名
            if git_version:
                zip_path = script_dir / f"nuitka-QuickEditPlus-{git_version}.zip"
            else:
                zip_path = script_dir / "nuitka-QuickEditPlus.zip"

            # 构建7z命令
            seven_zip_cmd = [
                seven_zip_path,
                "a",
                "-tzip",
                str(zip_path),
                "QuickEdit++",
            ]  # 使用完整路径

            if run_command(seven_zip_cmd, "7z压缩"):
                print(f"\n压缩完成! 文件位置: {zip_path}")
            else:
                print("\n压缩失败!")
                input("按回车键退出...")
                return 1
        else:
            print("\n编译完成! (跳过压缩步骤)")

        print("\n构建过程完成!")
        input("按回车键退出...")
        return 0

    except Exception as e:
        print(f"\n发生未预期的错误: {e}")
        import traceback

        traceback.print_exc()
        input("按回车键退出...")
        return 1


if __name__ == "__main__":
    sys.exit(main())
