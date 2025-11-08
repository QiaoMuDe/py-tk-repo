"""
文件操作核心功能模块
"""

import os
import sys
import threading
import queue
import codecs
import chardet

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class FileOperationCore:
    """文件操作核心功能类，提供基础的文件操作功能"""
    
    def __init__(self):
        """初始化文件操作核心"""
        self.file_read_cancelled = False
        self.read_queue = queue.Queue()
        
    def is_binary_file(self, file_path=None, sample_data=None, sample_size=1024):
        """
        检测文件是否为二进制文件
        
        原理：通过检查文件中是否包含非文本字符（控制字符）来判断
        
        Args:
            file_path: 文件路径（如果提供了sample_data，则忽略此参数）
            sample_data: 已读取的文件样本数据（字节类型）
            sample_size: 用于检测的样本大小（字节）
            
        Returns:
            bool: 如果是二进制文件返回True，否则返回False
        """
        try:
            # 如果提供了样本数据，直接使用
            if sample_data is not None:
                sample = sample_data
            else:
                # 否则从文件中读取样本
                with open(file_path, "rb") as file:
                    sample = file.read(sample_size)
            
            # 如果文件为空，不视为二进制文件
            if not sample:
                return False
                
            # 统计控制字符的数量（除了换行符、回车符和制表符）
            control_chars = 0
            for byte in sample:
                # 检查是否为控制字符（ASCII值小于32的字符）
                # 排除换行符(10)、回车符(13)和制表符(9)
                if byte < 32 and byte not in (9, 10, 13):
                    control_chars += 1
                    
            # 如果控制字符占比超过5%，认为是二进制文件
            # 这个阈值可以根据需要调整
            return control_chars / len(sample) > 0.05
        except Exception:
            # 如果读取文件出错，保守地认为可能是二进制文件
            return True
    
    def detect_file_encoding_and_line_ending(self, file_path=None, sample_data=None):
        """
        检测文件编码和换行符类型
        
        Args:
            file_path: 文件路径（如果提供了sample_data，则忽略此参数）
            sample_data: 已读取的文件样本数据（字节类型）
            
        Returns:
            tuple: (编码, 换行符类型)
        """
        if file_path is None and sample_data is None:
            return "UTF-8", "LF"  # 默认值
            
        if file_path is not None and not os.path.exists(file_path):
            return "UTF-8", "LF"  # 默认值
            
        try:
            # 如果提供了样本数据，直接使用
            if sample_data is not None:
                raw_data = sample_data
            else:
                # 否则从文件中读取样本
                with open(file_path, "rb") as file:
                    # 减少读取量，对于编码检测和换行符识别，通常1KB就足够了
                    raw_data = file.read(1024)
            
            # 检测编码
            if raw_data:
                result = chardet.detect(raw_data)
                encoding = result["encoding"] if result["encoding"] else "UTF-8"
                
                # 改进：将ASCII编码统一显示为UTF-8，因为ASCII是UTF-8的子集
                if encoding and encoding.lower() == "ascii":
                    encoding = "UTF-8"
            else:
                encoding = "UTF-8"
                
            # 检测换行符类型
            if b"\r\n" in raw_data:
                line_ending = "CRLF"
            elif b"\n" in raw_data:
                line_ending = "LF"
            elif b"\r" in raw_data:
                line_ending = "CR"
            else:
                line_ending = "LF"  # 默认
                
            return encoding, line_ending
        except Exception:
            return "UTF-8", "LF"  # 出错时返回默认值
    
    def async_read_file(self, file_path, callback=None, error_callback=None, progress_callback=None, max_file_size=10*1024*1024):
        """
        异步读取文件内容
        
        Args:
            file_path: 要读取的文件路径
            callback: 读取完成后的回调函数，接收参数 (file_path, content, encoding, line_ending)
            error_callback: 错误回调函数，接收参数 (error_message)
            progress_callback: 进度回调函数，接收参数 (bytes_read, total_bytes)
            max_file_size: 最大允许的文件大小（字节），默认10MB
        """
        # 重置取消标志
        self.file_read_cancelled = False
        
        def read_worker():
            """工作线程函数"""
            try:
                # 检查文件大小
                file_size = os.path.getsize(file_path)
                if file_size > max_file_size:
                    if error_callback:
                        error_callback(f"无法打开文件：文件大小为 {file_size/1024/1024:.2f} MB，超过了最大文件打开限制 {max_file_size/1024/1024:.2f} MB。\n请使用其他专业的编辑器打开此文件。")
                    return
                
                # 只打开一次文件，读取样本数据用于所有检测
                sample_data = None
                with open(file_path, "rb") as file:
                    # 读取1KB样本数据用于二进制文件检测、编码检测和换行符检测
                    sample_data = file.read(1024)
                
                # 首先检测是否为二进制文件
                if self.is_binary_file(sample_data=sample_data):
                    if error_callback:
                        error_callback("文件似乎是二进制文件，无法作为文本文件打开")
                    return
                
                # 使用同一样本数据检测编码和换行符类型
                encoding, line_ending = self.detect_file_encoding_and_line_ending(sample_data=sample_data)
                
                # 分块读取文件内容以避免内存问题
                content_chunks = []
                chunk_size = 8192  # 8KB chunks
                bytes_read = 0
                
                # 使用检测到的编码打开文件
                with codecs.open(file_path, "r", encoding=encoding, errors="replace") as file:
                    while not self.file_read_cancelled:
                        chunk = file.read(chunk_size)
                        if not chunk:
                            break
                        content_chunks.append(chunk)
                        bytes_read += len(chunk.encode(encoding))
                        
                        # 如果提供了进度回调，调用它
                        if progress_callback:
                            progress_callback(bytes_read, file_size)
                
                if self.file_read_cancelled:
                    return
                    
                content = "".join(content_chunks)
                
                # 调用完成回调
                if callback:
                    callback(file_path, content, encoding, line_ending)
                    
            except Exception as e:
                # 调用错误回调
                if error_callback:
                    error_callback(str(e))
        
        # 启动工作线程
        thread = threading.Thread(target=read_worker, daemon=True)
        thread.start()
        
        return thread
    
    def cancel_file_read(self):
        """取消文件读取操作"""
        self.file_read_cancelled = True
    
    def format_file_size(self, size_bytes):
        """
        格式化文件大小显示
        
        Args:
            size_bytes: 文件大小（字节）
            
        Returns:
            str: 格式化后的文件大小字符串
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
    
    def convert_line_endings(self, content, line_ending):
        """
        转换文本内容的换行符格式
        
        Args:
            content: 原始文本内容
            line_ending: 目标换行符格式 ("LF", "CRLF", "CR")
            
        Returns:
            str: 转换后的文本内容
        """
        # 如果内容为空，直接返回
        if not content:
            return content
            
        # 检测当前内容的换行符格式
        has_crlf = '\r\n' in content
        has_lf = '\n' in content
        has_cr = '\r' in content
        
        # 如果已经是目标格式，直接返回原内容
        if line_ending == "CRLF" and has_crlf and not has_lf and not has_cr:
            return content
        elif line_ending == "LF" and has_lf and not has_crlf and not has_cr:
            return content
        elif line_ending == "CR" and has_cr and not has_crlf and not has_lf:
            return content
            
        # 需要转换，使用更高效的方法
        if line_ending == "CRLF":
            # 如果内容只有LF，直接替换
            if has_lf and not has_crlf and not has_cr:
                return content.replace('\n', '\r\n')
            # 如果内容只有CR，先转换为LF再转换为CRLF
            elif has_cr and not has_crlf and not has_lf:
                return content.replace('\r', '\r\n')
            # 混合格式，先统一为LF再转换为CRLF
            else:
                normalized_content = content.replace('\r\n', '\n').replace('\r', '\n')
                return normalized_content.replace('\n', '\r\n')
        elif line_ending == "CR":
            # 如果内容只有LF，直接替换
            if has_lf and not has_crlf and not has_cr:
                return content.replace('\n', '\r')
            # 如果内容只有CRLF，先转换为LF再转换为CR
            elif has_crlf and not has_lf and not has_cr:
                normalized_content = content.replace('\r\n', '\n')
                return normalized_content.replace('\n', '\r')
            # 混合格式，先统一为LF再转换为CR
            else:
                normalized_content = content.replace('\r\n', '\n').replace('\r', '\n')
                return normalized_content.replace('\n', '\r')
        else:  # LF
            # 如果内容只有CRLF，直接替换
            if has_crlf and not has_lf and not has_cr:
                return content.replace('\r\n', '\n')
            # 如果内容只有CR，直接替换
            elif has_cr and not has_crlf and not has_lf:
                return content.replace('\r', '\n')
            # 混合格式，先统一为LF
            else:
                return content.replace('\r\n', '\n').replace('\r', '\n')