#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QuickEdit++ Python构建脚本
使用PyInstaller打包应用程序，并可选择使用7z进行压缩
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


def format_version(version):
    """
    格式化版本号为标准格式（vX.X.X）

    Args:
        version (str): 原始版本号

    Returns:
        str: 格式化后的版本号，如果不符合标准格式则返回None
    """
    import re

    # 匹配标准版本格式：vX.X.X（其中X是数字）
    match = re.match(r"^v(\d+)\.(\d+)\.(\d+)$", version)
    if match:
        return version  # 已经是标准格式，直接返回

    # 尝试从带哈希的版本中提取标准部分（如vX.X.X-xxx）
    match = re.match(r"^v(\d+)\.(\d+)\.(\d+)-", version)
    if match:
        # 提取标准部分
        major, minor, patch = match.groups()
        return f"v{major}.{minor}.{patch}"

    # 如果都不匹配，返回None
    return None


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
            version_with_hash = f"{tag}-{commit_hash}"

            # 尝试格式化版本号
            formatted_version = format_version(version_with_hash)
            if formatted_version:
                return formatted_version

            # 如果格式化失败，尝试只使用标签
            formatted_tag = format_version(tag)
            if formatted_tag:
                return formatted_tag

            return "unknown"
        elif tag_result.returncode == 0:
            tag = tag_result.stdout.strip()
            # 尝试格式化标签
            formatted_tag = format_version(tag)
            if formatted_tag:
                return formatted_tag

            return "unknown"
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
        print("=== QuickEdit++ 构建脚本 ===\n")

        # 检查PyInstaller
        print("检查必要工具...")
        pyinstaller_exists, pyinstaller_path = check_command_exists("pyinstaller")
        if not pyinstaller_exists:
            print("错误: 找不到pyinstaller，请确保已安装PyInstaller")
            print("安装命令: pip install pyinstaller")
            input("按回车键退出...")
            return 1

        print(f"找到pyinstaller: {pyinstaller_path}")

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

        # 构建PyInstaller命令
        icon_path = script_dir / "icons" / "QuickEdit++.ico"
        main_script = script_dir / "QuickEdit++.py"

        pyinstaller_cmd = [
            pyinstaller_path,  # 使用完整路径
            "--noconfirm",  # 覆盖输出目录而不询问
            "--clean",  # 清理临时文件
            "-w",  # 不显示控制台窗口
            "-D",  # 创建目录分发
            f"-i={icon_path}",
            str(main_script),
        ]

        # 执行编译
        print("\n开始编译 QuickEdit++...")
        if not run_command(pyinstaller_cmd, "PyInstaller编译"):
            input("按回车键退出...")
            return 1

        # 如果7z可用，则进行压缩
        if use_7z:
            print("\n开始打包...")
            dist_dir = script_dir / "dist"

            # 根据Git版本信息生成压缩文件名
            if git_version:
                zip_path = dist_dir / f"pyinstaller-QuickEditPlus-{git_version}.zip"
            else:
                zip_path = dist_dir / "pyinstaller-QuickEditPlus.zip"

            # 切换到dist目录
            os.chdir(dist_dir)

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
