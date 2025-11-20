"""
文件操作核心功能模块
"""

import os
import sys
import codecs
import chardet
import threading


class FileOperationCore:
    """文件操作核心功能类，提供基础的文件操作功能"""

    def is_binary_file(self, file_path=None, sample_data=None, sample_size=4096):
        """
        检测文件是否为二进制文件

        原理：结合多种启发式方法判断，减少对包含少量乱码的文本文件的误判

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

            # 方法1: 检查NULL字节 (二进制文件通常包含大量NULL字节)
            if b'\x00' in sample:
                # 如果NULL字节数量很少，可能是文本文件中的乱码
                null_count = sample.count(b'\x00')
                if null_count / len(sample) > 0.02:  # 2%以上认为是二进制
                    return True

            # 方法2: 统计控制字符（更宽松的阈值）
            control_chars = 0
            for byte in sample:
                # 检查是否为控制字符（ASCII值小于32的字符）
                # 排除换行符(10)、回车符(13)和制表符(9)
                if byte < 32 and byte not in (9, 10, 13):
                    control_chars += 1

            # 降低阈值到10%，减少对包含少量乱码的文本文件的误判
            control_char_ratio = control_chars / len(sample)
            if control_char_ratio > 0.10:
                return True

            # 方法3: 尝试使用常见编码解码文件
            # 如果能成功解码，更可能是文本文件
            encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'gb2312', 'gbk']
            success_decodings = 0
            max_errors = len(sample) * 0.15  # 允许15%的解码错误
            
            for encoding in encodings_to_try:
                try:
                    # 尝试解码，但允许一些错误
                    decoded_text = sample.decode(encoding, errors='replace')
                    # 计算解码后的替换字符数量（乱码）
                    replacement_count = decoded_text.count('\ufffd')  # Unicode替换字符
                    if replacement_count <= max_errors:
                        success_decodings += 1
                except Exception:
                    pass

            # 如果能成功解码一种以上的编码，更可能是文本文件
            if success_decodings > 0:
                return False

            # 综合判断：如果通过了上述所有检查，可能是文本文件
            return control_char_ratio > 0.05  # 最后使用一个较低的阈值
            
        except Exception:
            # 如果读取文件出错，先尝试从错误类型判断
            # 大多数情况下保持保守判断
            return True

    def detect_file_encoding_and_line_ending(self, file_path=None, sample_data=None):
        """
        检测文件编码和换行符类型

        Args:
            file_path: 文件路径 (如果提供了sample_data, 则忽略此参数)
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
                    # 减少读取量，对于编码检测和换行符识别，通常4KB就足够了
                    raw_data = file.read(4096)

            # 检测编码
            if raw_data:
                try:
                    result = chardet.detect(raw_data)
                    encoding = result["encoding"] if result["encoding"] else "UTF-8"

                    # 将ASCII编码统一显示为UTF-8，因为ASCII是UTF-8的子集
                    if encoding and encoding.lower() == "ascii":
                        encoding = "UTF-8"
                except Exception:
                    # 如果chardet检测失败，使用默认编码
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

    def read_file_sync(self, file_path, max_file_size=10 * 1024 * 1024, encoding=None):
        """
        同步读取文件内容

        Args:
            file_path: 要读取的文件路径
            max_file_size: 最大允许的文件大小(字节), 默认10MB
            encoding (str, optional): 指定文件编码, 如果为None则自动检测

        Returns:
            dict: 包含读取结果的字典
        """
        result = {"success": False, "data": None, "title": "", "message": ""}

        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                result["title"] = "文件不存在"
                result["message"] = f"指定的文件不存在：{file_path}"
                return result

            # 检查文件大小
            file_size = os.path.getsize(file_path)
            if file_size > max_file_size:
                result["title"] = "文件过大"
                result["message"] = (
                    f"文件大小: {self.format_file_size(file_size)}\n"
                    f"最大限制: {self.format_file_size(max_file_size)}\n\n"
                    f"建议：\n"
                    f"• 使用专业的大型文件编辑器打开此文件\n"
                    f"• 或在设置中增加最大文件大小限制"
                )
                return result

            # 读取4KB样本数据用于检测
            sample_data = None
            with open(file_path, "rb") as file:
                sample_data = file.read(4096)

            # 检测是否为二进制文件
            if self.is_binary_file(sample_data=sample_data):
                result["title"] = "无法打开二进制文件"
                result["message"] = (
                    "QuickEdit++ 是一个文本编辑器，不支持打开二进制文件。\n\n"
                    f"建议：\n"
                    f"• 使用十六进制编辑器查看此文件\n"
                    f"• 或使用支持二进制文件的专业编辑器"
                )
                return result

            # 检测编码和换行符类型
            if encoding is None:
                # 如果没有指定编码，自动检测
                encoding, line_ending = self.detect_file_encoding_and_line_ending(
                    sample_data=sample_data
                )
            else:
                # 如果指定了编码，只检测换行符类型
                _, line_ending = self.detect_file_encoding_and_line_ending(
                    sample_data=sample_data
                )

            # 全量读取文件内容
            with codecs.open(
                file_path, "r", encoding=encoding, errors="replace"
            ) as file:
                content = file.read()

            # 构建成功结果
            result["success"] = True  # 读取成功
            result["data"] = {  # 文件读取成功数据
                "file_path": file_path,  # 文件路径
                "content": content,  # 文件内容
                "encoding": encoding,  # 文件编码
                "line_ending": line_ending,  # 文件换行符格式
                "file_size": file_size,  # 文件大小（字节）
            }
            result["title"] = "文件读取成功"
            result["message"] = f"成功读取文件: {os.path.basename(file_path)}"

            return result

        except Exception as e:
            result["title"] = "读取文件错误"
            result["message"] = f"无法打开文件: {str(e)}"
            return result

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
        has_crlf = "\r\n" in content
        has_lf = "\n" in content
        has_cr = "\r" in content

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
                return content.replace("\n", "\r\n")
            # 如果内容只有CR，先转换为LF再转换为CRLF
            elif has_cr and not has_crlf and not has_lf:
                return content.replace("\r", "\r\n")
            # 混合格式，先统一为LF再转换为CRLF
            else:
                normalized_content = content.replace("\r\n", "\n").replace("\r", "\n")
                return normalized_content.replace("\n", "\r\n")
        elif line_ending == "CR":
            # 如果内容只有LF，直接替换
            if has_lf and not has_crlf and not has_cr:
                return content.replace("\n", "\r")
            # 如果内容只有CRLF，先转换为LF再转换为CR
            elif has_crlf and not has_lf and not has_cr:
                normalized_content = content.replace("\r\n", "\n")
                return normalized_content.replace("\n", "\r")
            # 混合格式，先统一为LF再转换为CR
            else:
                normalized_content = content.replace("\r\n", "\n").replace("\r", "\n")
                return normalized_content.replace("\n", "\r")
        else:  # LF
            # 如果内容只有CRLF，直接替换
            if has_crlf and not has_lf and not has_cr:
                return content.replace("\r\n", "\n")
            # 如果内容只有CR，直接替换
            elif has_cr and not has_crlf and not has_lf:
                return content.replace("\r", "\n")
            # 混合格式，先统一为LF
            else:
                return content.replace("\r\n", "\n").replace("\r", "\n")

    def read_file_async(self, file_path, max_file_size=10 * 1024 * 1024, callback=None):
        """
        异步读取文件内容

        此方法在新线程中执行文件读取操作，避免阻塞主线程UI

        Args:
            file_path: 要读取的文件路径
            max_file_size: 最大允许的文件大小（字节），默认10MB
            callback: 读取完成后的回调函数，接收一个参数（读取结果字典）

        Returns:
            None: 结果通过回调函数返回

        Note:
            - 回调函数在后台线程中执行，如果需要更新UI，请确保在主线程中执行
            - 读取过程完全复用read_file_sync方法的逻辑
        """

        def _read_task():
            # 在后台线程中执行同步读取
            result = self.read_file_sync(file_path, max_file_size)
            # 调用回调函数处理结果
            if callback:
                try:
                    callback(result)
                except Exception as e:
                    # 捕获并记录回调中的异常，防止线程崩溃
                    print(f"回调函数执行出错: {str(e)}")

        # 创建并启动线程
        thread = threading.Thread(target=_read_task)
        thread.daemon = True  # 设置为守护线程，主程序退出时自动结束
        thread.start()
