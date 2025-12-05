#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通知组件模块
提供各种通知样式的UI组件, 包括成功通知、错误通知、警告通知等

基本使用方法:
    from ui.notification import Notification, NotificationType, NotificationPosition

    # 显示不同类型的通知
    Notification.show_success("成功", "操作已完成")
    Notification.show_error("错误", "操作失败, 请重试")
    Notification.show_warning("警告", "磁盘空间不足")
    Notification.show_info("提示", "新版本已发布")

    # 在模态窗口中显示通知, 用于在模态窗口中被阻塞时显示通知
    Notification.set_next_parent(self)
    Notification.show_success("成功", "操作已完成")

    # 自定义通知位置和持续时间
    Notification.show(
        "自定义通知",
        "这是一个自定义的通知",
        NotificationType.INFO,
        duration=6000,
        position=NotificationPosition.TOP_LEFT
    )

    # 全局配置
    Notification.set_default_position(NotificationPosition.TOP_RIGHT)
    Notification.set_default_duration(4000)
    Notification.set_max_notifications(5)

    # 关闭所有通知
    Notification.close_all()

功能特点:
    - 支持四种通知类型: 成功、错误、警告、信息
    - 支持六种显示位置: 左上、右上、左下、右下、上方居中、屏幕居中
    - 支持自定义持续时间和最大同时显示数量
    - 支持固定通知 (不会自动消失)
    - 支持复制通知内容
    - 支持淡入淡出动画效果
    - 自动调整位置避免重叠
    - DPI感知, 适配高分辨率屏幕
"""

import customtkinter as ctk
import sys

# Windows API 导入
if sys.platform == "win32":
    import ctypes


def get_screen_size():
    """
    获取DPI感知的真实屏幕尺寸

    Returns:
        tuple: (屏幕宽度, 屏幕高度), 如果获取失败则返回默认值(1920, 1080)
    """
    # 非Windows系统直接返回默认值
    if sys.platform != "win32":
        return 1920, 1080

    try:
        # 定义Windows API常量和结构
        user32 = ctypes.windll.user32

        # 设置进程为DPI感知, 获取真实物理分辨率
        if hasattr(user32, "SetProcessDPIAware"):
            user32.SetProcessDPIAware()

        # 使用GetSystemMetrics获取屏幕尺寸
        # SM_CXSCREEN = 0 (屏幕宽度)
        # SM_CYSCREEN = 1 (屏幕高度)
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)

        # 验证获取的值是否合理
        if screen_width > 0 and screen_height > 0:
            return screen_width, screen_height
        else:
            return 1920, 1080  # 默认值

    except Exception as e:
        # 如果获取失败, 返回默认值
        print(f"获取屏幕尺寸失败: {e}")
        return 1920, 1080  # 默认值


class NotificationType:
    """通知类型枚举"""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class NotificationPosition:
    """通知位置枚举"""

    TOP_LEFT = "top_left"  # 屏幕左上角显示
    TOP_RIGHT = "top_right"  # 屏幕右上角显示
    BOTTOM_LEFT = "bottom_left"  # 屏幕左下角显示
    BOTTOM_RIGHT = "bottom_right"  # 屏幕右下角显示
    TOP_CENTER = "top_center"  # 屏幕上方居中显示
    CENTER = "center"  # 屏幕居中显示

    # 位置选项列表 - 用于菜单显示
    OPTIONS = [
        ("左上角", TOP_LEFT),
        ("右上角", TOP_RIGHT),
        ("左下角", BOTTOM_LEFT),
        ("右下角", BOTTOM_RIGHT),
        ("上方居中", TOP_CENTER),
        ("屏幕居中", CENTER),
    ]

    # 位置名称映射 - 用于显示
    NAMES = {
        TOP_LEFT: "左上角",
        TOP_RIGHT: "右上角",
        BOTTOM_LEFT: "左下角",
        BOTTOM_RIGHT: "右下角",
        TOP_CENTER: "上方居中",
        CENTER: "屏幕居中",
    }

    # 位置映射 - 用于字符串转换
    MAP = {
        "top_left": TOP_LEFT,
        "top_right": TOP_RIGHT,
        "bottom_left": BOTTOM_LEFT,
        "bottom_right": BOTTOM_RIGHT,
        "top_center": TOP_CENTER,
        "center": CENTER,
    }

    @classmethod
    def get_all_positions(cls):
        """获取所有可用的通知位置"""
        return [
            cls.TOP_LEFT,
            cls.TOP_RIGHT,
            cls.BOTTOM_LEFT,
            cls.BOTTOM_RIGHT,
            cls.TOP_CENTER,
            cls.CENTER,
        ]

    @classmethod
    def from_string(cls, position_str):
        """
        将字符串转换为通知位置枚举值

        Args:
            position_str: 位置字符串，如 "top_left", "top_right" 等

        Returns:
            对应的NotificationPosition枚举值，如果字符串不匹配则返回默认值BOTTOM_RIGHT
        """
        # 转换为小写并去除前后空格
        position_str = str(position_str).strip().lower()

        # 使用位置映射
        return cls.MAP.get(position_str, cls.BOTTOM_RIGHT)


class Notification:
    """通知类 - 负责创建和管理通知窗口"""

    # 类变量 - 全局配置
    _default_position = NotificationPosition.BOTTOM_RIGHT  # 默认位置
    _default_duration = 3000  # 默认持续时间 (毫秒)
    _max_notifications = 5  # 最大同时显示的通知数量
    _notification_spacing = 30  # 通知之间的间距 (像素)

    # 类变量 - 当前活动通知
    _active_notifications = []  # 活动通知列表
    _notification_counter = 0  # 通知计数器, 用于生成唯一ID

    # 类变量 - 下一个通知的父窗口引用 (用于模态对话框场景)
    _next_parent_window = None  # 下一个通知的父窗口引用

    # 通知组件字体大小配置
    ICON_FONT_SIZE = 25  # 图标字体大小
    TITLE_FONT_SIZE = 18  # 标题字体大小
    MESSAGE_FONT_SIZE = 15  # 消息字体大小
    BUTTON_FONT_SIZE = 12  # 按钮字体大小

    # 通知窗口配置
    DEFAULT_WIDTH = 320  # 默认宽度
    MIN_HEIGHT = 100  # 最小高度
    MAX_HEIGHT = 200  # 最大高度
    LINE_HEIGHT = 27  # 每行高度估算
    CHAR_PER_LINE = 40  # 每行字符数估算
    CORNER_RADIUS = 15  # 圆角半径
    BORDER_WIDTH = 2  # 边框宽度
    INDICATOR_WIDTH = 5  # 指示条宽度

    # 动态宽度计算配置
    MIN_NOTIFICATION_WIDTH = 200  # 最小通知宽度
    MIN_DYNAMIC_WIDTH = 280  # 动态宽度最小值
    TITLE_CHAR_WIDTH = 30  # 标题字符宽度估算
    MESSAGE_CHAR_WIDTH = 10  # 消息字符宽度估算
    UI_ELEMENTS_WIDTH = 145  # UI元素宽度（按钮和图标）

    # 动画配置
    FADE_STEPS = 10  # 淡入淡出步数
    FADE_DELAY = 30  # 淡入淡出延迟 (毫秒)

    @classmethod
    def set_default_position(cls, position):
        """
        设置默认通知位置

        Args:
            position: 通知位置, 使用NotificationPosition枚举值
        """
        cls._default_position = position

    @classmethod
    def set_default_duration(cls, duration):
        """
        设置默认通知持续时间

        Args:
            duration: 持续时间 (毫秒)
        """
        cls._default_duration = duration

    @classmethod
    def set_max_notifications(cls, max_count):
        """
        设置最大同时显示的通知数量

        Args:
            max_count: 最大通知数量
        """
        cls._max_notifications = max_count

    @classmethod
    def set_next_parent(cls, parent_window=None):
        """
        设置下一个通知的父窗口引用 (用于模态对话框场景)

        注意：此设置只对下一个创建的通知有效，使用后会自动清除

        Args:
            parent_window: 父窗口对象, 通常为模态对话框
        """
        if parent_window is None:
            print("warn: 提供的父窗口对象为空")
            return

        if parent_window and (
            not isinstance(parent_window, ctk.CTkToplevel)
            and not isinstance(parent_window, ctk.CTk)
        ):
            print("warn: 提供的父窗口对象不是 CTkToplevel 类型或 CTk 类型")
            return

        cls._next_parent_window = parent_window

    @classmethod
    def show(
        cls,
        title="提示",
        message="",
        notification_type=NotificationType.INFO,
        duration=None,
        position=None,
    ):
        """
        显示通知

        Args:
            title: 通知标题
            message: 通知消息内容
            notification_type: 通知类型, 默认为信息通知
            duration: 通知显示持续时间 (毫秒) , 默认使用类默认值
            position: 通知位置, 默认使用类默认值

        Returns:
            Notification: 创建的通知对象
        """
        # 消息持续时间
        if duration is None:
            duration = cls._default_duration

        # 消息位置
        if position is None:
            position = cls._default_position

        # 检查是否超过最大通知数量
        if len(cls._active_notifications) >= cls._max_notifications:
            # 关闭最早的通知
            oldest_notification = cls._active_notifications[0]
            oldest_notification.close()

        # 创建新通知
        notification = cls(title, message, notification_type, duration, position)

        # 添加到活动通知列表
        cls._active_notifications.append(notification)

        # 设置通知位置 - 确保在添加到列表后再设置位置
        try:
            notification._set_notification_geometry()
        except Exception as e:
            # 如果设置位置失败, 从列表中移除并销毁通知
            if notification in cls._active_notifications:
                cls._active_notifications.remove(notification)
            notification._destroy_notification()
            print(f"设置通知位置失败: {e}")
            return None

        return notification

    @classmethod
    def show_success(cls, title="成功", message="", duration=None, position=None):
        """
        显示成功通知

        Args:
            title: 通知标题
            message: 通知消息内容
            duration: 通知显示持续时间 (毫秒) , 默认使用类默认值
            position: 通知位置, 默认使用类默认值

        Returns:
            Notification: 创建的通知对象
        """
        return cls.show(title, message, NotificationType.SUCCESS, duration, position)

    @classmethod
    def show_error(cls, title="错误", message="", duration=None, position=None):
        """
        显示错误通知

        Args:
            title: 通知标题
            message: 通知消息内容
            duration: 通知显示持续时间 (毫秒) , 默认使用类默认值
            position: 通知位置, 默认使用类默认值

        Returns:
            Notification: 创建的通知对象
        """
        return cls.show(title, message, NotificationType.ERROR, duration, position)

    @classmethod
    def show_warning(cls, title="警告", message="", duration=None, position=None):
        """
        显示警告通知

        Args:
            title: 通知标题
            message: 通知消息内容
            duration: 通知显示持续时间 (毫秒) , 默认使用类默认值
            position: 通知位置, 默认使用类默认值

        Returns:
            Notification: 创建的通知对象
        """
        return cls.show(title, message, NotificationType.WARNING, duration, position)

    @classmethod
    def show_info(cls, title="提示", message="", duration=None, position=None):
        """
        显示信息通知

        Args:
            title: 通知标题
            message: 通知消息内容
            duration: 通知显示持续时间 (毫秒) , 默认使用类默认值
            position: 通知位置, 默认使用类默认值

        Returns:
            Notification: 创建的通知对象
        """
        return cls.show(title, message, NotificationType.INFO, duration, position)

    @classmethod
    def close_all(cls):
        """关闭所有活动通知"""
        # 创建列表副本以避免在迭代时修改列表
        notifications = cls._active_notifications.copy()
        for notification in notifications:
            notification.close()

    def __init__(
        self,
        title,
        message,
        notification_type=NotificationType.SUCCESS,
        duration=3000,
        position=NotificationPosition.BOTTOM_RIGHT,
    ):
        """
        初始化通知

        Args:
            title: 通知标题
            message: 通知消息内容
            notification_type: 通知类型, 默认为成功通知
            duration: 通知显示持续时间 (毫秒) , 默认为3秒
            position: 通知位置, 默认为屏幕右下角显示
        """
        # 生成唯一ID
        Notification._notification_counter += 1
        self.notification_id = Notification._notification_counter

        self.title = title
        self.message = message
        self.notification_type = notification_type
        self.duration = duration
        self.position = position
        self.font_family = "Microsoft YaHei UI"

        # 状态变量
        self.fade_out_job = None  # 存储淡出任务的ID
        self.auto_hide_job = None  # 存储自动隐藏任务的ID
        self.is_pinned = False  # 通知是否被固定

        # 存储当前通知的父窗口引用
        self._parent_window = Notification._next_parent_window
        # 使用后立即清除类级别的父窗口引用，确保只对下一个通知有效
        Notification._next_parent_window = None

        # 计算通知窗口大小 - 在创建内容前计算
        self._calculate_notification_size()

        # 创建通知窗口 - 检查是否有父窗口
        parent = None
        if self._parent_window:
            parent = self._parent_window

        self.notification = ctk.CTkToplevel(parent)
        self.notification.title(f"Notification_{self.notification_id}")  # 设置唯一标题
        self.notification.resizable(False, False)

        # 立即禁用CustomTkinter的窗口标题栏颜色设置功能，避免销毁后回调错误
        self.notification._deactivate_windows_window_header_manipulation = True

        # 设置窗口属性
        self.notification.overrideredirect(True)  # 移除窗口边框
        self.notification.attributes("-topmost", True)  # 始终置顶
        self.notification.attributes("-transparentcolor", self.notification["bg"])

        # 如果有父窗口, 设置通知为父窗口的子窗口
        if self._parent_window:
            self.notification.transient(self._parent_window)

        # 创建通知内容
        self._create_notification_content()

        # 开始淡入动画
        self._fade_in()

    def _calculate_notification_size(self):
        """计算通知窗口的大小"""
        # 根据消息长度动态计算通知窗口大小
        estimated_lines = max(1, len(self.message) // self.CHAR_PER_LINE)
        self.notification_height = max(
            self.MIN_HEIGHT,
            min(self.MAX_HEIGHT, self.MIN_HEIGHT + estimated_lines * self.LINE_HEIGHT),
        )

        # 动态计算通知宽度
        # 计算标题和消息的预估宽度
        title_width = len(self.title) * self.TITLE_CHAR_WIDTH  # 标题字符宽度估算
        message_width = min(
            len(self.message) * self.MESSAGE_CHAR_WIDTH,
            self.CHAR_PER_LINE * self.MESSAGE_CHAR_WIDTH,
        )  # 消息字符宽度估算，但不超过单行最大宽度

        # 计算所需的最小宽度（标题、消息和UI元素的最大值）
        min_required_width = max(title_width, message_width) + self.UI_ELEMENTS_WIDTH

        # 设置通知宽度：在最小宽度和默认宽度之间选择，不超过最大宽度
        self.notification_width = max(
            self.MIN_NOTIFICATION_WIDTH,  # 最小宽度
            min(
                self.DEFAULT_WIDTH, max(min_required_width, self.MIN_DYNAMIC_WIDTH)
            ),  # 不超过默认宽度，但至少最小动态宽度
        )

    def _set_notification_geometry(self):
        """设置通知窗口的位置和大小"""
        # 计算通知窗口大小
        self._calculate_notification_size()

        # 使用提供的函数获取屏幕尺寸
        screen_width, screen_height = get_screen_size()

        # 获取当前通知在活动列表中的索引
        try:
            notification_index = self._active_notifications.index(self)
        except ValueError:
            notification_index = 0

        # 确保position是字符串, 避免属性访问错误
        position_str = (
            str(self.position)
            if self.position is not None
            else NotificationPosition.BOTTOM_RIGHT
        )

        # 根据位置设置计算坐标
        if position_str == NotificationPosition.TOP_LEFT:
            # 左上角
            x = 20
            y = 20 + notification_index * (
                self.notification_height + self._notification_spacing
            )

        elif position_str == NotificationPosition.TOP_RIGHT:
            # 右上角
            x = screen_width - self.notification_width - 350
            y = 20 + notification_index * (
                self.notification_height + self._notification_spacing
            )

        elif position_str == NotificationPosition.TOP_CENTER:
            # 上方居中
            x = screen_width // 2 - 200
            y = 20 + notification_index * (
                self.notification_height + self._notification_spacing
            )

        elif position_str == NotificationPosition.BOTTOM_LEFT:
            # 左下角
            x = 20
            y = (
                screen_height
                - self.notification_height
                - 300
                - notification_index
                * (self.notification_height + self._notification_spacing)
            )

        elif position_str == NotificationPosition.BOTTOM_RIGHT:
            # 右下角
            x = screen_width - self.notification_width - 350
            y = (
                screen_height
                - self.notification_height
                - 300
                - notification_index
                * (self.notification_height + self._notification_spacing)
            )

        elif position_str == NotificationPosition.CENTER:
            # 屏幕居中
            x = screen_width // 2 - 200
            y = screen_height // 2 - notification_index * (
                self.notification_height + self._notification_spacing
            )

        else:  # 默认为BOTTOM_RIGHT
            # 默认右下角
            x = screen_width - self.notification_width - 350
            y = (
                screen_height
                - self.notification_height
                - 300
                - notification_index
                * (self.notification_height + self._notification_spacing)
            )

        # 确保通知窗口不会超出屏幕边界
        if x < 10:
            x = 10
        elif x + self.notification_width > screen_width - 10:
            x = screen_width - self.notification_width - 10

        if y < 10:
            y = 10
        elif y + self.notification_height > screen_height - 10:
            y = screen_height - self.notification_height - 10

        # 设置窗口位置和大小
        self.notification.geometry(
            f"{self.notification_width}x{self.notification_height}+{x}+{y}"
        )

    def _create_notification_content(self):
        """创建通知内容"""
        # 根据通知类型获取颜色配置
        colors = self._get_notification_colors()

        # 主框架 - 使用圆角设计, 设置为透明背景
        main_frame = ctk.CTkFrame(
            self.notification,
            corner_radius=self.CORNER_RADIUS,
            fg_color="transparent",
            border_width=0,
        )
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # 内容框架 - 实际的通知容器
        content_frame = ctk.CTkFrame(
            main_frame,
            corner_radius=self.CORNER_RADIUS,
            fg_color=colors["bg"],
            border_width=self.BORDER_WIDTH,
            border_color=colors["border"],
        )
        content_frame.pack(fill="both", expand=True)

        # 内部内容框架 - 包含图标、标题和消息
        inner_content_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        inner_content_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # 左侧彩色指示条 - 垂直条, 与内容框架高度一致
        indicator_frame = ctk.CTkFrame(
            inner_content_frame,
            width=self.INDICATOR_WIDTH,
            corner_radius=3,
            fg_color=colors["indicator"],
        )
        indicator_frame.pack(side="left", fill="y", padx=(0, 10))
        indicator_frame.pack_propagate(False)

        # 右侧内容区域 - 包含图标、标题和消息
        right_content_frame = ctk.CTkFrame(inner_content_frame, fg_color="transparent")
        right_content_frame.pack(side="left", fill="both", expand=True)

        # 图标和标题框架
        header_frame = ctk.CTkFrame(right_content_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 5))

        # 通知图标
        icon_label = ctk.CTkLabel(
            header_frame,
            text=colors["icon"],
            font=(self.font_family, self.ICON_FONT_SIZE, "bold"),
            text_color=colors["icon_color"],
        )
        icon_label.pack(side="left", padx=(0, 10))

        # 标题标签
        title_label = ctk.CTkLabel(
            header_frame,
            text=self.title,
            font=(self.font_family, self.TITLE_FONT_SIZE, "bold"),
            text_color=colors["title"],
        )
        title_label.pack(side="left")

        # 复制按钮 - 添加到标题栏右侧
        self.copy_button = ctk.CTkButton(
            header_frame,
            text="复制",
            width=45,
            height=25,
            corner_radius=5,
            fg_color="transparent",
            #  hover_color="transparent",
            hover=False,
            text_color=("#757575", "#b0b0b0"),
            font=(self.font_family, self.BUTTON_FONT_SIZE, "bold"),
            command=self._copy_notification_content,
        )
        self.copy_button.pack(side="right", padx=(5, 0))

        # 固定按钮 - 添加到标题栏右侧, 在复制按钮左侧
        self.pin_button = ctk.CTkButton(
            header_frame,
            text="固定",
            width=45,
            height=25,
            corner_radius=5,
            fg_color="transparent",
            # hover_color="transparent",
            hover=False,
            text_color=("#757575", "#b0b0b0"),
            font=(self.font_family, self.BUTTON_FONT_SIZE, "bold"),
            command=self._toggle_pin_notification,
        )
        self.pin_button.pack(side="right", padx=(5, 0))

        # 消息标签 - 设置为可滚动文本区域以处理长消息
        msg_frame = ctk.CTkFrame(right_content_frame, fg_color="transparent")
        msg_frame.pack(fill="both", expand=True, pady=(5, 0))

        # 创建可滚动的文本框
        self.msg_text = ctk.CTkTextbox(
            msg_frame,
            font=(self.font_family, self.MESSAGE_FONT_SIZE),
            text_color=colors["message"],
            fg_color="transparent",
            border_width=0,
            wrap="word",
            height=self.notification_height - 80,  # 根据通知高度调整文本框高度
        )
        self.msg_text.pack(fill="both", expand=True)

        # 插入消息内容并设置为只读
        self.msg_text.insert("0.0", self.message)
        self.msg_text.configure(state="disabled")

    def _get_notification_colors(self):
        """
        根据通知类型获取颜色配置

        Returns:
            dict: 包含各种颜色配置的字典
        """
        if self.notification_type == NotificationType.SUCCESS:
            return {
                "bg": ("#ffffff", "#1e1e1e"),
                "border": ("#d0d0d0", "#505050"),
                "indicator": ("#4CAF50", "#45a049"),
                "icon": "✓",
                "icon_color": ("#4CAF50", "#45a049"),
                "title": ("#212121", "#ffffff"),
                "message": ("#424242", "#e0e0e0"),
            }
        elif self.notification_type == NotificationType.ERROR:
            return {
                "bg": ("#ffffff", "#1e1e1e"),
                "border": ("#d0d0d0", "#505050"),
                "indicator": ("#F44336", "#d32f2f"),
                "icon": "✕",
                "icon_color": ("#F44336", "#d32f2f"),
                "title": ("#212121", "#ffffff"),
                "message": ("#424242", "#e0e0e0"),
            }
        elif self.notification_type == NotificationType.WARNING:
            return {
                "bg": ("#ffffff", "#1e1e1e"),
                "border": ("#d0d0d0", "#505050"),
                "indicator": ("#FF9800", "#f57c00"),
                "icon": "⚠",
                "icon_color": ("#FF9800", "#f57c00"),
                "title": ("#212121", "#ffffff"),
                "message": ("#424242", "#e0e0e0"),
            }
        else:  # INFO
            return {
                "bg": ("#ffffff", "#1e1e1e"),
                "border": ("#d0d0d0", "#505050"),
                "indicator": ("#2196F3", "#1976D2"),
                "icon": "ℹ",
                "icon_color": ("#2196F3", "#1976D2"),
                "title": ("#212121", "#ffffff"),
                "message": ("#424242", "#e0e0e0"),
            }

    def _fade_in(self, step=0):
        """淡入效果"""
        if step <= self.FADE_STEPS:
            self.notification.attributes("-alpha", step / self.FADE_STEPS)
            self.notification.after(self.FADE_DELAY, lambda: self._fade_in(step + 1))
        else:
            # 淡入完成后, 只有在通知未被固定时才等待指定时间后淡出
            if not self.is_pinned:
                self.auto_hide_job = self.notification.after(
                    self.duration, self._start_fade_out
                )

    def _start_fade_out(self):
        """开始淡出的函数"""
        self._fade_out()

    def _fade_out(self, step=None):
        """淡出效果"""
        if step is None:
            step = self.FADE_STEPS

        if step > 0:
            self.notification.attributes("-alpha", step / self.FADE_STEPS)
            self.fade_out_job = self.notification.after(
                self.FADE_DELAY, lambda: self._fade_out(step - 1)
            )
        else:
            # 完全透明后销毁窗口
            self._destroy_notification()

    def _destroy_notification(self):
        """销毁通知窗口并从活动列表中移除"""
        # 从活动通知列表中移除
        if self in self._active_notifications:
            self._active_notifications.remove(self)

        # 取消所有待处理的回调
        if hasattr(self, "auto_hide_job") and self.auto_hide_job:
            try:
                self.notification.after_cancel(self.auto_hide_job)
            except:
                pass
            self.auto_hide_job = None

        if hasattr(self, "fade_out_job") and self.fade_out_job:
            try:
                self.notification.after_cancel(self.fade_out_job)
            except:
                pass
            self.fade_out_job = None

        # 直接销毁窗口
        try:
            if hasattr(self, "notification") and self.notification.winfo_exists():
                # 完全禁用CustomTkinter的窗口标题栏颜色设置功能
                if hasattr(
                    self.notification, "_deactivate_windows_window_header_manipulation"
                ):
                    self.notification._deactivate_windows_window_header_manipulation = (
                        True
                    )

                # 禁用CustomTkinter的标题栏颜色设置功能，避免销毁后回调错误
                if hasattr(self.notification, "_windows_set_titlebar_color_called"):
                    self.notification._windows_set_titlebar_color_called = False

                # 先移除窗口属性, 避免回调函数访问已销毁的窗口
                self.notification.overrideredirect(False)
                self.notification.attributes("-topmost", False)

                # 直接销毁窗口，不使用延迟
                self.notification.destroy()
        except:
            # 窗口可能已经被销毁, 忽略错误
            pass

    def close(self):
        """立即关闭通知"""
        self._destroy_notification()

    def _toggle_pin_notification(self):
        """切换通知固定状态"""
        self.is_pinned = not self.is_pinned

        if self.is_pinned:
            # 取消自动隐藏计时器
            if self.auto_hide_job:
                self.notification.after_cancel(self.auto_hide_job)
                self.auto_hide_job = None

            # 更新按钮样式为固定状态 (红色背景)
            self.pin_button.configure(
                fg_color=("#f44336", "#d32f2f"),
                text_color=("#ffffff", "#ffffff"),
                text="取消固定",
            )
        else:
            # 重新启动自动隐藏计时器
            self.auto_hide_job = self.notification.after(
                self.duration, self._start_fade_out
            )

            # 恢复按钮样式为未固定状态
            self.pin_button.configure(
                fg_color="transparent", text_color=("#757575", "#b0b0b0"), text="固定"
            )

    def _copy_notification_content(self):
        """复制通知内容到剪贴板"""
        try:
            # 只复制消息内容, 不包含标题
            message_content = self.message
            self.notification.clipboard_clear()
            self.notification.clipboard_append(message_content)

            # 显示复制成功的反馈
            self._show_copy_feedback()
        except Exception as e:
            print(f"复制失败: {e}")

    def _show_copy_feedback(self):
        """显示复制成功的反馈"""
        # 临时更改按钮文本为"✓"并改变背景色为绿色表示复制成功
        if hasattr(self, "copy_button"):
            original_text = self.copy_button.cget("text")
            original_fg_color = self.copy_button.cget("fg_color")
            original_text_color = self.copy_button.cget("text_color")

            self.copy_button.configure(
                text="✓",
                fg_color=("#4caf50", "#2e7d32"),
                text_color=("#ffffff", "#ffffff"),
            )

            # 800毫秒后恢复原样式
            self.notification.after(
                800,
                lambda: self.copy_button.configure(
                    text=original_text,
                    fg_color=original_fg_color,
                    text_color=original_text_color,
                ),
            )
