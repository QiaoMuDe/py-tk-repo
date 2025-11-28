#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文件监听模块，用于检测文件变更并通知用户重新加载
"""

import os
import time
import tkinter as tk
from tkinter import messagebox
from config.config_manager import config_manager
from loguru import logger


class FileWatcher:
    """
    文件监听器类，用于检测文件变更

    功能：
    - 缓存文件的大小和修改时间
    - 定时检查文件是否发生变更
    - 检测到变更时通知用户是否重新加载
    - 在保存文件前更新缓存，防止程序的保存被误认为外部修改
    """

    def __init__(self, app_instance):
        """
        初始化文件监听器

        Args:
            app_instance: 应用程序实例，用于访问文本区域和文件操作以及配置管理器
        """
        self.app = app_instance
        self.watched_file = None  # 当前监听的文件路径
        self.file_info = {}  # 缓存的文件信息 {path: (size, mtime)}
        self.check_job = None  # 定时任务ID
        self.is_checking = False  # 是否正在检查中，防止重复提示
        self.user_notified = False  # 是否已经通知过用户
        self.save_time = 0  # 记录最近一次保存操作的时间戳
        self.last_saved_mtime = 0  # 记录最后一次保存时的文件修改时间

        # 从配置管理器获取文件监听器配置
        self.config = config_manager.get("file_watcher")
        # 计算实际使用的值（将秒转换为毫秒）
        self.check_interval = (
            self.config["check_interval"] * 1000
        )  # 文件变更检查间隔（毫秒）
        self.save_buffer = self.config["save_buffer"]  # 保存后的缓冲时间（秒）
        self.readonly_notify_delay = (
            self.config["readonly_notify_delay"] * 1000
        )  # 只读模式下通知重置延迟（毫秒）
        self.edit_notify_delay = (
            self.config["edit_notify_delay"] * 1000
        )  # 编辑模式下通知重置延迟（毫秒）
        self.monitoring_enabled = self.config.get(
            "monitoring_enabled", True
        )  # 是否启用文件变更监控
        self.silent_reload = self.config.get("silent_reload", False)  # 是否静默自动重载

    def start_watching(self, file_path: str) -> None:
        """
        开始监听指定文件

        Args:
            file_path: 要监听的文件路径
        """
        if not file_path or not os.path.exists(file_path):
            return

        # 检查是否启用了文件变更监控
        if not self.monitoring_enabled:
            return

        # 停止之前的监听
        self.stop_watching()

        # 设置当前监听文件
        self.watched_file = file_path

        # 缓存文件信息并记录当前修改时间
        self._update_file_cache(file_path, update_mtime=True)

        # 启动定时检查
        self._schedule_check()

    def _update_file_cache(self, file_path: str, update_mtime: bool = False) -> None:
        """
        更新文件缓存信息

        Args:
            file_path: 文件路径
            update_mtime: 是否更新last_saved_mtime
        """
        try:
            stat = os.stat(file_path)
            self.file_info[file_path] = (stat.st_size, stat.st_mtime)
            if update_mtime:
                self.last_saved_mtime = stat.st_mtime  # 记录修改时间

        except (OSError, IOError) as e:
            logger.error(f"更新文件缓存时出错: {file_path}, 错误信息: {str(e)}")
            # 文件可能被删除或无法访问
            self.file_info[file_path] = (0, 0)
            if update_mtime:
                self.last_saved_mtime = 0

    def stop_watching(self) -> None:
        """
        停止文件监听
        """
        # 取消定时任务
        if self.check_job:
            self.app.after_cancel(self.check_job)
            self.check_job = None

        # 清除监听状态
        self.watched_file = None
        self.is_checking = False
        self.user_notified = False

    def update_cache_before_save(self, file_path: str) -> None:
        """
        在保存文件前更新缓存，防止程序的保存被误认为外部修改

        Args:
            file_path: 即将保存的文件路径
        """
        if file_path and os.path.exists(file_path):
            self._update_file_cache(file_path)
            # 记录保存操作的时间戳
            self.save_time = time.time()

    def update_cache_after_save(self, file_path: str) -> None:
        """
        在保存文件后更新缓存，确保缓存包含最新的文件信息

        Args:
            file_path: 已保存的文件路径
        """
        if file_path and os.path.exists(file_path):
            # 等待一小段时间确保文件系统完成写入
            self.app.after(
                100, lambda: self._update_file_cache(file_path, update_mtime=True)
            )
            # 记录保存操作的时间戳
            self.save_time = time.time()

    def update_file_info(self) -> None:
        """
        更新当前监听文件的缓存信息

        这个方法用于在文件打开后更新缓存，确保文件信息是最新的
        """
        if self.watched_file and os.path.exists(self.watched_file):
            self._update_file_cache(self.watched_file)

    def _schedule_check(self) -> None:
        """
        安排下一次检查
        """
        if self.watched_file:
            self.check_job = self.app.after(
                self.check_interval, self._check_file_changes
            )

    def _check_file_changes(self) -> None:
        """
        检查文件是否发生变更
        """
        if not self.watched_file or not os.path.exists(self.watched_file):
            self._schedule_check()
            return

        # 获取当前文件信息
        try:
            stat = os.stat(self.watched_file)
            current_size = stat.st_size
            current_mtime = stat.st_mtime

            # 获取缓存的文件信息
            cached_info = self.file_info.get(self.watched_file, (0, 0))
            cached_size, cached_mtime = cached_info

            # 检查文件是否发生变更
            if (
                current_size != cached_size or current_mtime != cached_mtime
            ) and not self.is_checking:
                # 检查是否在保存后的缓冲时间内
                current_time = time.time()
                in_save_buffer = (current_time - self.save_time) < self.save_buffer

                # 如果在缓冲时间内，且修改时间与保存时的修改时间相同或更早，则忽略
                if in_save_buffer and current_mtime <= self.last_saved_mtime:
                    # 更新缓存但不提示用户
                    self._update_file_cache(self.watched_file)
                    self._schedule_check()
                    return

                # 如果在缓冲时间内，但修改时间比保存时更新，说明是外部修改
                if in_save_buffer and current_mtime > self.last_saved_mtime:
                    # 重置保存时间，避免后续检测被忽略
                    self.save_time = 0

                # 文件已变更，通知用户
                self._notify_file_changed()
            else:
                # 文件未变更，继续检查
                self._schedule_check()

        except (OSError, IOError) as e:
            logger.error(f"检查文件变更时出错: {self.watched_file}, 错误信息: {str(e)}")
            # 文件可能被删除或无法访问，继续检查
            self._schedule_check()

    def _notify_file_changed(self) -> None:
        """
        通知用户文件已变更
        """
        # 防止重复通知
        if self.is_checking or self.user_notified:
            self._schedule_check()
            return

        # 检查是否启用了文件变更监控
        if not self.monitoring_enabled:
            # 如果禁用了监控，不执行任何检查
            self._schedule_check()
            return

        self.is_checking = True

        # 检查是否处于静默重载模式
        if self.silent_reload:
            # 静默模式下直接重新加载文件
            self._reload_file()
            self.is_checking = False
            self._schedule_check()
            self.app.nm.show_info(message="文件发生变更, 已静默重载")
            return

        # 检查是否处于只读模式
        is_read_only = self.app.is_read_only

        # 根据只读模式调整提示信息
        if is_read_only:
            message = f"文件 '{os.path.basename(self.watched_file)}' 已被外部程序修改。\n\n当前处于只读模式，是否重新加载文件以查看最新内容？"
            title = "文件已变更（只读模式）"
        else:
            message = f"文件 '{os.path.basename(self.watched_file)}' 已被外部程序修改。\n\n是否重新加载文件？\n\n选择'是'将丢失当前未保存的更改。"
            title = "文件已变更"

        # 询问用户是否重新加载文件
        result = messagebox.askyesno(title, message, icon=messagebox.WARNING)

        if result:
            # 用户选择重新加载
            self._reload_file()
        else:
            # 用户选择不重新加载，更新缓存以避免再次提示
            self._update_file_cache(self.watched_file)

            if is_read_only:
                # 在只读模式下，设置一个较短的通知延迟，以便稍后再次提醒用户
                self.user_notified = True
                # 使用配置的只读模式通知延迟（已经是毫秒）
                self.app.after(
                    self.readonly_notify_delay, self._reset_notification_state
                )
            else:
                # 在编辑模式下，也设置相对较短的通知延迟，但比只读模式稍长一些
                self.user_notified = True
                # 使用配置的编辑模式通知延迟（已经是毫秒）
                self.app.after(self.edit_notify_delay, self._reset_notification_state)

        self.is_checking = False
        self._schedule_check()

    def _reset_notification_state(self) -> None:
        """
        重置通知状态，允许再次提醒用户
        延迟时间在初始化时已从配置中的秒数转换为毫秒
        """
        self.user_notified = False

    def _reload_file(self) -> None:
        """
        重新加载文件
        """
        if self.watched_file and hasattr(self.app, "file_ops"):
            try:
                # 获取当前光标位置和滚动位置
                cursor_pos = self.app.text_area.index(tk.INSERT)
                scroll_pos = self.app.text_area.yview()

                # 检查是否处于只读模式
                was_read_only = self.app.is_read_only

                # 如果是只读模式，临时启用文本框以便重新加载
                if was_read_only:
                    self.app.text_area.configure(state="normal")

                # 重新加载文件
                self.app.file_ops._open_file(
                    file_path=self.watched_file, is_auto_reload=True
                )

                # 尝试恢复光标位置和滚动位置
                try:
                    self.app.text_area.mark_set(tk.INSERT, cursor_pos)
                    self.app.text_area.see(tk.INSERT)
                    self.app.text_area.yview_moveto(scroll_pos[0])
                except:
                    # 如果恢复位置失败，不做特殊处理
                    pass

                # 如果原本是只读模式，恢复禁用状态
                if was_read_only:
                    self.app.text_area.configure(state="disabled")

                # 更新缓存
                self._update_file_cache(self.watched_file)
                self.user_notified = False  # 重置通知状态

            except Exception as e:
                logger.error(
                    f"重新加载文件时出错: {self.watched_file}, 错误信息: {str(e)}"
                )
                # messagebox.showerror("错误", f"重新加载文件时出错: {str(e)}")
                self.app.nm.show_error(message=f"重新加载文件时出错: {str(e)}")

                # 如果出错且原本是只读模式，确保恢复禁用状态
                if was_read_only:
                    try:
                        self.app.text_area.configure(state="disabled")
                    except:
                        pass

    def is_watching_file(self, file_path: str) -> bool:
        """
        检查是否正在监听指定文件

        Args:
            file_path: 文件路径

        Returns:
            bool: 是否正在监听该文件
        """
        return self.watched_file == file_path

    def update_monitoring_setting(self, enabled: bool) -> None:
        """
        更新文件变更监控设置

        Args:
            enabled: 是否启用文件变更监控
        """
        self.monitoring_enabled = enabled
        # 更新配置
        config_manager.set("file_watcher.monitoring_enabled", enabled)
        config_manager.save_config()

        # 如果禁用了监控，停止当前的文件监听
        if not enabled and self.watched_file:
            self.stop_watching()
        # 如果启用了监控，且当前有打开的文件，则开始监听
        elif enabled and self.app.current_file_path and not self.watched_file:
            self.start_watching(self.app.current_file_path)

    def set_silent_reload(self, silent: bool) -> None:
        """
        设置静默重载模式

        Args:
            silent: 是否启用静默重载模式
        """
        self.silent_reload = silent
        # 更新配置
        config_manager.set("file_watcher.silent_reload", silent)
        config_manager.save_config()
