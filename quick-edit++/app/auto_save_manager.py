#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
自动保存管理器模块
负责处理应用程序的自动保存功能，包括定时保存、焦点离开保存等
"""

import time
import tkinter as tk
from config.config_manager import config_manager
from loguru import logger


class AutoSaveManager:
    """自动保存管理器类"""

    def __init__(self, app):
        """
        初始化自动保存管理器

        Args:
            app: 应用程序实例
        """
        self.app = app

        # 自动保存相关属性
        self.auto_save_enabled = config_manager.get(
            "app.auto_save", False
        )  # 是否启用自动保存
        self.auto_save_interval = config_manager.get(
            "app.auto_save_interval", 5
        )  # 自动保存间隔，单位秒
        self.last_auto_save_time = 0  # 上次自动保存时间
        self._auto_save_job = None  # 自动保存任务ID

    def start_auto_save(self):
        """
        启动自动保存功能

        创建一个每秒运行的定时任务，检查是否需要自动保存文件内容
        """
        # 先停止现有的自动保存任务
        self.stop_auto_save()

        # 记录自动保存启动时间
        self.auto_save_start_time = time.time()

        # 启动每秒运行一次的检查任务
        self._auto_save_job = self.app.after(1000, self._auto_save_check)

    def stop_auto_save(self):
        """
        停止自动保存功能

        取消现有的自动保存任务（如果有）
        """
        if self._auto_save_job is not None:
            self.app.after_cancel(self._auto_save_job)  # 取消自动保存任务
            self._auto_save_job = None  # 清除自动保存任务ID

    def _auto_save_check(self):
        """
        每秒运行一次的自动保存检查方法

        此方法每秒都会被调用，但只有在达到指定间隔时间时才会执行实际的自动保存
        """
        # 检查是否启用了自动保存功能
        if not self.auto_save_enabled:
            # 如果自动保存被禁用，则不再调度下一次检查
            return

        # 计算距离上次自动保存的时间间隔
        current_time = time.time()
        time_since_last_save = current_time - self.last_auto_save_time

        # 检查是否有当前打开的文件
        if self.app.current_file_path:
            # 检查是否达到了指定的自动保存间隔
            if time_since_last_save >= self.auto_save_interval:
                # 达到间隔时间，执行自动保存
                self._auto_save()
            else:
                # 未达到间隔时间，只更新状态栏显示倒计时
                remaining_time = self.auto_save_interval - time_since_last_save
                self.app.status_bar.show_auto_save_countdown(remaining_time)
        else:
            # 没有打开的文件，不执行自动保存
            self.app.status_bar.show_auto_save_status(saved=False)

        # 调度下一次检查（每秒一次）
        self._auto_save_job = self.app.after(1000, self._auto_save_check)

    def _auto_save(self):
        """
        执行自动保存操作

        此方法在达到指定间隔时间时被调用，执行实际的文件保存操作
        """
        # 检查文件是否已修改
        if self.app.is_modified():
            # 检查是否为只读模式
            if self.app.is_read_only:
                # 文件处于只读模式，跳过自动保存并记录日志
                logger.debug(
                    f"文件处于只读模式，跳过自动保存: {self.app.current_file_path}"
                )
                # 更新状态栏显示只读模式下的自动保存状态
                self.app.status_bar.show_auto_save_status(saved=False, read_only=True)
                # 更新上次自动保存时间，以重置计时器
                self.last_auto_save_time = time.time()
                return

            # 执行保存操作
            file_path = self.app.current_file_path
            try:
                # 传递is_auto_save=True，表示这是自动保存
                self.app.file_ops._save_file(is_auto_save=True)

                # 更新上次自动保存时间
                self.last_auto_save_time = time.time()

                # 更新状态栏的自动保存信息，显示具体的保存时间
                self.app.status_bar.show_auto_save_status(saved=True)
                logger.info(f"自动保存成功: {file_path}")

            except Exception as e:
                logger.error(f"自动保存失败: {file_path}, 错误: {str(e)}")
                self.app.status_bar.show_notification(f"自动保存失败: {str(e)}")
        else:
            # 文件未修改，更新状态栏显示检查状态
            self.app.status_bar.show_auto_save_status(saved=False)
            # 即使没有保存，也要更新上次自动保存时间，以重置计时器
            self.last_auto_save_time = time.time()
            logger.debug("文件未修改，跳过自动保存")

    def on_text_area_focus_out(self, event=None):
        """
        文本区域失去焦点事件处理

        当焦点离开文本框时，立即执行自动保存（如果文件已修改且自动保存已启用）
        这与定时自动保存是独立的，确保在用户切换到其他应用时也能保存
        """
        # 检查是否启用了自动保存功能
        if self.auto_save_enabled and self.app.current_file_path:
            # 记录焦点离开事件
            logger.debug(
                f"文本区域失去焦点，触发焦点离开自动保存: {self.app.current_file_path}"
            )
            # 立即执行保存操作
            self._auto_save()

    def toggle_auto_save(self):
        """
        切换自动保存模式

        功能：
        - 获取Checkbutton已更新的状态值
        - 保存配置
        - 更新内部状态
        - 更新状态栏显示
        - 根据状态启动或停止自动保存
        """
        # 获取Checkbutton已更新的当前状态值
        if self.app.auto_save_var is not None:
            current_state = self.app.auto_save_var.get()
        else:
            # 如果没有var，则保持原有逻辑
            current_state = config_manager.get("app.auto_save", False)
            current_state = not current_state

        # 保存配置
        config_manager.set("app.auto_save", current_state)
        config_manager.save_config()

        # 更新内部状态
        self.auto_save_enabled = current_state

        # 使用状态栏的方法更新显示
        self.app.status_bar.set_auto_save_status()

        # 根据状态启动或停止自动保存
        if current_state:
            # 启用自动保存，启动自动保存任务
            self.start_auto_save()

            # 开启的时候立即保存一次(如果文件已修改)
            if self.app.current_file_path and self.app.is_modified():
                # 调用内部的保存方法
                self._auto_save()
                logger.info(f"启用自动保存时立即保存文件: {self.app.current_file_path}")

        else:
            # 禁用自动保存，取消自动保存任务
            self.stop_auto_save()
            # 禁用自动保存后，将上次的自动保存时间设置为0
            self.last_auto_save_time = 0

        # 更新窗口标题
        self.app._update_window_title()

    def set_auto_save_interval(self, interval):
        """
        设置自动保存间隔

        Args:
            interval (int): 保存间隔，单位为秒
        """
        # 保存配置
        config_manager.set("app.auto_save_interval", interval)
        config_manager.save_config()

        # 更新内部状态
        self.auto_save_interval = interval

        # 更新auto_save_interval_var变量
        self.app.auto_save_interval_var.set(str(interval))

        # 使用状态栏的方法更新显示
        self.app.status_bar.set_auto_save_status()

        # 如果自动保存已启用，重新启动自动保存任务
        if self.auto_save_enabled:
            # 启动新的自动保存任务（start_auto_save方法会自动取消现有任务）
            self.start_auto_save()

        # 显示通知
        self.app.status_bar.show_notification(f"自动保存间隔已设置为: {interval}秒")
