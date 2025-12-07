"""
Nuitka核心逻辑模块
处理Nuitka打包的核心逻辑和配置
"""

import os
import sys
import subprocess
import importlib


class NuitkaConfig:
    """Nuitka配置类"""

    def __init__(self):
        """初始化Nuitka配置"""
        self.reset_config()

    def reset_config(self):
        """重置配置为默认值"""
        self.script = ""  # 脚本路径
        self.output_dir = ""  # 输出目录
        self.output_filename = ""  # 输出文件名
        self.icon = ""  # 图标文件
        self.mode = "standalone"  # 编译模式: accelerated, standalone, onefile, app, app-dist, module, package
        self.console_mode = "force"  # Windows控制台模式: force, disable, attach, hide
        self.remove_output = False  # 是否删除build目录
        self.progress_bar = "auto"  # 进度条模式: auto, tqdm, rich, none
        self.show_memory = False  # 是否显示内存使用信息
        self.jobs = 0  # 并行C编译任务数，0表示自动
        self.lto = "auto"  # 链接时优化: yes, no, auto
        self.static_libpython = "auto"  # 静态链接Python库: yes, no, auto
        self.clang = False  # 是否强制使用clang
        self.mingw64 = False  # 是否在Windows使用MinGW64
        self.msvc = ""  # 强制使用的MSVC版本
        self.company_name = ""  # 公司名称
        self.product_name = ""  # 产品名称
        self.file_version = ""  # 文件版本
        self.product_version = ""  # 产品版本
        self.file_description = ""  # 文件描述
        self.copyright = ""  # 版权信息
        self.trademarks = ""  # 商标信息
        self.include_packages = []  # 包含的包列表
        self.include_modules = []  # 包含的模块列表
        self.include_plugin_dirs = []  # 包含的插件目录列表
        self.exclude_modules = []  # 排除的模块列表
        self.enable_plugins = []  # 启用的插件列表
        self.disable_plugins = []  # 禁用的插件列表
        self.user_plugins = []  # 用户插件列表
        self.onefile_tempdir_spec = ""  # onefile模式下解压目录规范
        self.onefile_cache_mode = ""  # onefile缓存模式
        self.onefile_as_archive = False  # 是否使用归档格式
        self.onefile_no_dll = False  # 是否强制使用可执行文件而非DLL
        self.warn_implicit_exceptions = False  # 是否对隐式异常发出警告
        self.warn_unusual_code = False  # 是否对异常代码发出警告
        self.assume_yes_for_downloads = False  # 是否允许自动下载外部代码
        self.clean_cache = ""  # 清理的缓存名
        self.force_dll_dependency_cache_update = False  # 是否强制更新DLL依赖缓存
        self.extra_args = ""  # 额外参数

    def get_command(self):
        """获取Nuitka命令

        Returns:
            list: Nuitka命令列表
        """
        cmd = [sys.executable, "-m", "nuitka"]

        # 添加编译模式
        if self.mode != "accelerated":
            cmd.extend(["--mode", self.mode])

        # 添加输出目录
        if self.output_dir:
            cmd.extend(["--output-dir", self.output_dir])

        # 添加输出文件名
        if self.output_filename:
            cmd.extend(["--output-filename", self.output_filename])

        # 添加图标
        if self.icon:
            cmd.extend(["--windows-icon-from-ico", self.icon])

        # 添加删除build目录选项
        if self.remove_output:
            cmd.append("--remove-output")

        # 添加进度条模式
        if self.progress_bar != "auto":
            cmd.extend(["--progress-bar", self.progress_bar])

        # 添加内存使用信息
        if self.show_memory:
            cmd.append("--show-memory")

        # 添加Windows控制台模式
        if self.console_mode != "force":
            cmd.extend(["--windows-console-mode", self.console_mode])

        # 添加版本信息
        if self.company_name:
            cmd.extend(["--company-name", self.company_name])

        if self.product_name:
            cmd.extend(["--product-name", self.product_name])

        if self.file_version:
            cmd.extend(["--file-version", self.file_version])

        if self.product_version:
            cmd.extend(["--product-version", self.product_version])

        if self.file_description:
            cmd.extend(["--file-description", self.file_description])

        if self.copyright:
            cmd.extend(["--copyright", self.copyright])

        if self.trademarks:
            cmd.extend(["--trademarks", self.trademarks])

        # 添加包含的包
        for package in self.include_packages:
            cmd.extend(["--include-package", package])

        # 添加包含的模块
        for module in self.include_modules:
            cmd.extend(["--include-module", module])

        # 添加包含的插件目录
        for plugin_dir in self.include_plugin_dirs:
            cmd.extend(["--include-plugin-directory", plugin_dir])

        # 添加排除的模块
        for module in self.exclude_modules:
            cmd.extend(["--nofollow-import-to", module])

        # 添加启用的插件
        for plugin in self.enable_plugins:
            cmd.extend(["--enable-plugins", plugin])

        # 添加禁用的插件
        for plugin in self.disable_plugins:
            cmd.extend(["--disable-plugins", plugin])

        # 添加用户插件
        for plugin in self.user_plugins:
            cmd.extend(["--user-plugin", plugin])

        # 添加编译选项
        if self.jobs != 0:
            cmd.extend(["--jobs", str(self.jobs)])

        if self.lto != "auto":
            cmd.extend(["--lto", self.lto])

        if self.static_libpython != "auto":
            cmd.extend(["--static-libpython", self.static_libpython])

        # 添加onefile选项
        if self.onefile_tempdir_spec:
            cmd.extend(["--onefile-tempdir-spec", self.onefile_tempdir_spec])

        if self.onefile_cache_mode:
            cmd.extend(["--onefile-cache-mode", self.onefile_cache_mode])

        if self.onefile_as_archive:
            cmd.append("--onefile-as-archive")

        if self.onefile_no_dll:
            cmd.append("--onefile-no-dll")

        # 添加警告控制
        if self.warn_implicit_exceptions:
            cmd.append("--warn-implicit-exceptions")

        if self.warn_unusual_code:
            cmd.append("--warn-unusual-code")

        if self.assume_yes_for_downloads:
            cmd.append("--assume-yes-for-downloads")

        # 添加缓存控制
        if self.clean_cache:
            cmd.extend(["--clean-cache", self.clean_cache])

        if self.force_dll_dependency_cache_update:
            cmd.append("--force-dll-dependency-cache-update")

        # 添加编译器选择
        if self.clang:
            cmd.append("--clang")

        if self.mingw64:
            cmd.append("--mingw64")

        if self.msvc:
            cmd.extend(["--msvc", self.msvc])

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
            result = subprocess.run(
                [sys.executable, "--version"], capture_output=True, text=True
            )
            if result.returncode != 0:
                return False, "Python环境不可用"
        except Exception:
            return False, "无法验证Python环境"

        # 验证Nuitka模块
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list"], capture_output=True, text=True
            )
            if result.returncode == 0:
                # 检查输出中是否包含nuitka (不区分大小写)
                if "nuitka" not in result.stdout.lower():
                    return False, "Nuitka模块未安装, 请使用 pip install nuitka 安装"
            else:
                return False, "无法获取已安装的Python包列表"
        except Exception:
            return False, "无法验证Nuitka模块"

        # 验证脚本文件
        if not self.script:
            return False, "请选择要打包的文件"

        if not os.path.exists(self.script):
            return False, "要打包的文件不存在"

        # 验证图标文件
        if self.icon and not os.path.exists(self.icon):
            return False, "图标文件不存在"

        # 验证输出目录
        if self.output_dir and not os.path.exists(self.output_dir):
            try:
                os.makedirs(self.output_dir, exist_ok=True)
            except Exception:
                return False, "无法创建输出目录"

        # 验证包含的插件目录
        for plugin_dir in self.include_plugin_dirs:
            if not os.path.exists(plugin_dir):
                return False, f"插件目录不存在: {plugin_dir}"

        # 验证用户插件
        for plugin in self.user_plugins:
            if not os.path.exists(plugin):
                return False, f"用户插件文件不存在: {plugin}"

        return True, ""

    def get_summary(self):
        """获取配置摘要

        Returns:
            str: 配置摘要文本
        """
        mode_names = {
            "accelerated": "加速模式",
            "standalone": "独立文件夹",
            "onefile": "单文件",
            "app": "应用包",
            "app-dist": "应用包(分发)",
            "module": "扩展模块",
            "package": "扩展包",
        }

        console_mode_names = {
            "force": "强制创建",
            "disable": "不创建",
            "attach": "附加已有",
            "hide": "隐藏新控制台",
        }

        summary = f"脚本: {self.script}\n"
        summary += f"编译模式: {mode_names.get(self.mode, self.mode)}\n"
        summary += f"删除build目录: {'是' if self.remove_output else '否'}\n"
        summary += f"进度条: {self.progress_bar}\n"
        summary += f"显示内存信息: {'是' if self.show_memory else '否'}\n"

        if sys.platform == "win32":
            summary += f"控制台模式: {console_mode_names.get(self.console_mode, self.console_mode)}\n"

        if self.output_dir:
            summary += f"输出目录: {self.output_dir}\n"

        if self.output_filename:
            summary += f"输出文件名: {self.output_filename}\n"

        if self.icon:
            summary += f"图标: {self.icon}\n"

        # 编译选项
        if self.jobs != 0:
            summary += f"并行任务数: {self.jobs}\n"

        if self.lto != "auto":
            summary += f"链接时优化: {self.lto}\n"

        if self.static_libpython != "auto":
            summary += f"静态链接Python库: {self.static_libpython}\n"

        if self.clang:
            summary += "使用Clang编译器: 是\n"

        if self.mingw64:
            summary += "使用MinGW64: 是\n"

        if self.msvc:
            summary += f"MSVC版本: {self.msvc}\n"

        # 版本信息
        if self.company_name:
            summary += f"公司名称: {self.company_name}\n"

        if self.product_name:
            summary += f"产品名称: {self.product_name}\n"

        if self.file_version:
            summary += f"文件版本: {self.file_version}\n"

        if self.product_version:
            summary += f"产品版本: {self.product_version}\n"

        if self.file_description:
            summary += f"文件描述: {self.file_description}\n"

        if self.copyright:
            summary += f"版权信息: {self.copyright}\n"

        if self.trademarks:
            summary += f"商标信息: {self.trademarks}\n"

        # 包含和排除
        if self.include_packages:
            summary += f"包含的包: {', '.join(self.include_packages)}\n"

        if self.include_modules:
            summary += f"包含的模块: {', '.join(self.include_modules)}\n"

        if self.include_plugin_dirs:
            summary += f"包含的插件目录: {', '.join(self.include_plugin_dirs)}\n"

        if self.exclude_modules:
            summary += f"排除的模块: {', '.join(self.exclude_modules)}\n"

        # 插件
        if self.enable_plugins:
            summary += f"启用的插件: {', '.join(self.enable_plugins)}\n"

        if self.disable_plugins:
            summary += f"禁用的插件: {', '.join(self.disable_plugins)}\n"

        if self.user_plugins:
            summary += f"用户插件: {', '.join(self.user_plugins)}\n"

        # onefile选项
        if self.onefile_tempdir_spec:
            summary += f"解压目录规范: {self.onefile_tempdir_spec}\n"

        if self.onefile_cache_mode:
            summary += f"缓存模式: {self.onefile_cache_mode}\n"

        if self.onefile_as_archive:
            summary += "使用归档格式: 是\n"

        if self.onefile_no_dll:
            summary += "强制使用可执行文件: 是\n"

        return summary
