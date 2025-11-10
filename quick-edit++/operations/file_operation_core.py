"""
文件操作核心功能模块
"""

import os
import sys
import codecs
import chardet
import concurrent.futures


class FileOperationCore:
    """文件操作核心功能类，提供基础的文件操作功能"""

    def __init__(self):
        """初始化文件操作核心"""
        # 创建线程池，最多同时处理1个文件读取任务
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        # 跟踪当前正在执行的Future对象
        self.current_futures = []
        # 标记线程池是否已关闭
        self._shutdown = False

    def shutdown(self):
        """关闭线程池，释放资源"""
        if not self._shutdown:
            # 取消所有未完成的任务
            self.cancel_all_reads()
            # 关闭线程池
            self.executor.shutdown(wait=True)
            self._shutdown = True

    def __del__(self):
        """析构函数，确保资源被释放"""
        try:
            self.shutdown()
        except:
            # 忽略析构时的异常
            pass

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

            # 检测编码 - 添加异常处理以防止chardet库的线程问题
            if raw_data:
                try:
                    result = chardet.detect(raw_data)
                    encoding = result["encoding"] if result["encoding"] else "UTF-8"

                    # 改进：将ASCII编码统一显示为UTF-8，因为ASCII是UTF-8的子集
                    if encoding and encoding.lower() == "ascii":
                        encoding = "UTF-8"
                except Exception as e:
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

    def read_file_async(self, file_path, max_file_size=10 * 1024 * 1024):
        """
        异步读取文件内容

        Args:
            file_path: 要读取的文件路径
            max_file_size: 最大允许的文件大小（字节），默认10MB

        Returns:
            concurrent.futures.Future: Future对象，可通过result()方法获取结果字典
        """
        # 检查线程池是否已关闭
        if self._shutdown:
            # 创建一个已完成的Future对象，返回错误结果
            future = concurrent.futures.Future()
            error_result = {
                "success": False,
                "data": None,
                "title": "线程池已关闭",
                "message": "文件读取功能已不可用，请重新启动应用程序",
            }
            future.set_result(error_result)
            return future

        def _read_file():
            """实际读取文件的工作函数"""
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

                # 读取样本数据用于检测
                sample_data = None
                with open(file_path, "rb") as file:
                    # 读取1KB样本数据用于二进制文件检测、编码检测和换行符检测
                    sample_data = file.read(1024)

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
                encoding, line_ending = self.detect_file_encoding_and_line_ending(
                    sample_data=sample_data
                )

                # 全量读取文件内容
                with codecs.open(
                    file_path, "r", encoding=encoding, errors="replace"
                ) as file:
                    content = file.read()

                # 构建成功结果
                result["success"] = True
                result["data"] = {
                    "file_path": file_path,
                    "content": content,
                    "encoding": encoding,
                    "line_ending": line_ending,
                    "file_size": file_size,
                }
                result["title"] = "文件读取成功"
                result["message"] = f"成功读取文件: {os.path.basename(file_path)}"

                return result

            except Exception as e:
                result["title"] = "读取文件错误"
                result["message"] = f"无法打开文件: {str(e)}"
                return result

        # 提交任务到线程池
        future = self.executor.submit(_read_file)
        self.current_futures.append(future)

        # 定期清理已完成的Future对象
        self._cleanup_completed_futures()

        return future

    def _cleanup_completed_futures(self):
        """清理已完成的Future对象，避免内存泄漏"""
        # 使用列表推导式过滤掉已完成的Future对象
        self.current_futures = [f for f in self.current_futures if not f.done()]

    def get_active_future_count(self):
        """获取当前活跃的Future对象数量"""
        self._cleanup_completed_futures()
        return len(self.current_futures)

    def cancel_all_reads(self):
        """取消所有正在进行的文件读取操作"""
        # 如果线程池已关闭，无需取消
        if self._shutdown:
            return

        for future in self.current_futures:
            future.cancel()
        self.current_futures = []

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
