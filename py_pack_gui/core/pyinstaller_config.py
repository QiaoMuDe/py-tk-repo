"""
PyInstaller核心逻辑模块
处理PyInstaller打包的核心逻辑和配置
"""

import os
import sys
import subprocess
import importlib


class PyInstallerConfig:
    """PyInstaller配置类"""

    def __init__(self):
        """初始化PyInstaller配置"""
        self.reset_config()

    def reset_config(self):
        """重置配置为默认值"""
        self.script = ""  # 脚本路径
        self.name = ""  # 应用名称
        self.output_dir = ""  # 输出目录
        self.work_dir = ""  # 临时工作目录
        self.spec_dir = ""  # spec文件目录
        self.icon = ""  # 图标文件
        self.mode = "onedir"  # 打包模式: onedir 或 onefile
        self.console = False  # 是否显示控制台
        self.clean = False  # 是否清理缓存
        self.yes = False  # 是否自动确认覆盖输出目录
        self.log_level = "INFO"  # 日志级别
        self.hidden_imports = []  # 隐藏导入列表
        self.exclude_modules = []  # 排除模块列表
        self.extra_args = ""  # 额外参数

    def get_command(self):
        """获取PyInstaller命令

        Returns:
            list: PyInstaller命令列表
        """
        cmd = [sys.executable, "-m", "PyInstaller"]

        # 添加打包模式
        if self.mode == "onefile":
            cmd.append("--onefile")
        else:
            cmd.append("--onedir")

        # 添加控制台选项
        if self.console:
            cmd.append("--console")
        else:
            cmd.append("--windowed")

        # 添加输出目录
        if self.output_dir:
            cmd.extend(["--distpath", self.output_dir])

        # 添加临时工作目录
        if self.work_dir:
            cmd.extend(["--workpath", self.work_dir])

        # 添加spec文件目录
        if self.spec_dir:
            cmd.extend(["--specpath", self.spec_dir])

        # 添加应用名称
        if self.name:
            cmd.extend(["--name", self.name])

        # 添加图标
        if self.icon:
            cmd.extend(["--icon", self.icon])

        # 添加清理选项
        if self.clean:
            cmd.append("--clean")

        # 添加自动确认选项
        if self.yes:
            cmd.append("-y")

        # 添加日志级别
        if self.log_level != "INFO":
            cmd.extend(["--log-level", self.log_level])

        # 添加隐藏导入
        for hidden in self.hidden_imports:
            cmd.extend(["--hidden-import", hidden])

        # 添加排除模块
        for exclude in self.exclude_modules:
            cmd.extend(["--exclude-module", exclude])

        # 添加额外参数
        if self.extra_args:
            # 处理额外参数，移除注释行和空行
            for line in self.extra_args.splitlines():
                # 移除注释和空白字符
                line = line.split("#")[0].strip()
                if line:
                    cmd.extend(line.split())

        # 添加脚本文件
        cmd.append(self.script)

        return cmd

    def validate(self):
        """验证配置

        Returns:
            tuple: (is_valid, error_message)
        """
        # 验证Python环境
        try:
            result = subprocess.run([sys.executable, "--version"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                return False, "Python环境不可用"
        except Exception:
            return False, "无法验证Python环境"
        
        # 验证PyInstaller模块
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                # 检查输出中是否包含pyinstaller (不区分大小写)
                if "pyinstaller" not in result.stdout.lower():
                    return False, "PyInstaller模块未安装, 请使用 pip install pyinstaller 安装"
            else:
                return False, "无法获取已安装的Python包列表"
        except Exception:
            return False, "无法验证PyInstaller模块"
        
        # 验证脚本文件
        if not self.script:
            return False, "请选择要打包的文件"

        if not os.path.exists(self.script):
            return False, "要打包的文件不存在"

        # 验证图标文件
        if self.icon and not os.path.exists(self.icon):
            return False, "图标文件不存在"

        # 验证spec文件目录
        if self.spec_dir and not os.path.exists(self.spec_dir):
            return False, "spec文件目录不存在"

        return True, ""

    def get_summary(self):
        """获取配置摘要

        Returns:
            str: 配置摘要文本
        """
        summary = f"脚本: {self.script}\n"
        summary += f"应用名称: {self.name or '默认'}\n"
        summary += f"打包模式: {'单文件' if self.mode == 'onefile' else '单目录'}\n"
        summary += f"控制台: {'显示' if self.console else '隐藏'}\n"
        summary += f"清理缓存: {'是' if self.clean else '否'}\n"
        summary += f"自动确认: {'是' if self.yes else '否'}\n"

        if self.output_dir:
            summary += f"输出目录: {self.output_dir}\n"

        if self.icon:
            summary += f"图标: {self.icon}\n"

        if self.hidden_imports:
            summary += f"隐藏导入: {', '.join(self.hidden_imports)}\n"

        if self.exclude_modules:
            summary += f"排除模块: {', '.join(self.exclude_modules)}\n"

        return summary
