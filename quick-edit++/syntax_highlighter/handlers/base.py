#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
语言处理器基类

提供所有语言处理器的抽象基类
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any


class LanguageHandler(ABC):
    """
    语言处理器抽象基类
    
    所有具体的语言处理器都应该继承此类并实现其抽象方法
    """
    
    # 子类应该定义此属性，指定支持的文件扩展名列表
    file_extensions = []
    
    def __init__(self):
        """初始化语言处理器"""
        self._keywords = []
        self._regex_patterns = {}
        self._tag_styles = {}
        self._setup_language()
    
    @abstractmethod
    def _setup_language(self):
        """
        设置语言特定的规则
        
        子类必须实现此方法来定义：
        - 关键字列表
        - 正则表达式模式
        - 标签样式
        """
        pass
    
    def get_keywords(self) -> List[str]:
        """
        获取关键字列表
        
        Returns:
            List[str]: 关键字列表
        """
        return self._keywords
    
    def get_regex_patterns(self) -> Dict[str, str]:
        """
        获取正则表达式模式字典
        
        Returns:
            Dict[str, str]: 标签名到正则表达式的映射
        """
        return self._regex_patterns
    
    def get_tag_styles(self) -> Dict[str, Dict[str, Any]]:
        """
        获取标签样式字典
        
        Returns:
            Dict[str, Dict[str, Any]]: 标签名到样式属性的映射
        """
        return self._tag_styles
    
    @classmethod
    def get_file_extensions(cls) -> List[str]:
        """
        获取支持的文件扩展名列表
        
        Returns:
            List[str]: 支持的文件扩展名列表
        """
        return cls.file_extensions