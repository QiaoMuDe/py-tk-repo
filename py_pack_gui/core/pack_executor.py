"""
打包执行器核心模块
处理PyInstaller和Nuitka打包命令的执行
"""

import os
import sys
import subprocess
import threading
from typing import Optional, Callable, Any
from core.pyinstaller_config import PyInstallerConfig


class PackExecutor:
    """打包执行器类，用于执行PyInstaller和Nuitka打包命令"""
    
    def __init__(self):
        """初始化打包执行器"""
        self.process: Optional[subprocess.Popen] = None
        self.is_running: bool = False
        self.current_config: Optional[Any] = None
        self.is_stopped_by_user: bool = False
        
        # 回调函数
        self.output_callback: Optional[Callable[[str], None]] = None
        self.status_callback: Optional[Callable[[str], None]] = None
        self.finish_callback: Optional[Callable[[bool, str], None]] = None
        self.lock_tab_callback: Optional[Callable[[bool], None]] = None
    
    def set_output_callback(self, callback: Callable[[str], None]) -> None:
        """设置输出回调函数
        
        Args:
            callback: 输出回调函数，接收输出文本
        """
        self.output_callback = callback
    
    def set_status_callback(self, callback: Callable[[str], None]) -> None:
        """设置状态回调函数
        
        Args:
            callback: 状态回调函数，接收状态文本
        """
        self.status_callback = callback
    
    def set_finish_callback(self, callback: Callable[[bool, str], None]) -> None:
        """设置完成回调函数
        
        Args:
            callback: 完成回调函数，接收成功标志和消息
        """
        self.finish_callback = callback
    
    def set_lock_tab_callback(self, callback: Callable[[bool], None]) -> None:
        """设置标签页锁定回调函数
        
        Args:
            callback: 标签页锁定回调函数，接收锁定状态
        """
        self.lock_tab_callback = callback
    
    def execute(self, config: PyInstallerConfig) -> bool:
        """执行打包命令
        
        Args:
            config: PyInstaller配置对象
            
        Returns:
            bool: 是否成功启动执行
        """
        # 验证配置
        is_valid, error_msg = config.validate()
        if not is_valid:
            if self.output_callback:
                self.output_callback(f"配置验证失败: {error_msg}\n")
            return False
        
        # 设置当前配置
        self.current_config = config
        self.is_running = True
        self.is_stopped_by_user = False
        
        # 锁定标签页
        if self.lock_tab_callback:
            self.lock_tab_callback(True)
        
        # 更新状态
        if self.status_callback:
            self.status_callback("运行中")
        
        # 在新线程中执行
        threading.Thread(target=self._run_command, args=(config,), daemon=True).start()
        return True
    
    def _run_command(self, config: PyInstallerConfig) -> None:
        """执行打包命令的内部方法
        
        Args:
            config: PyInstaller配置对象
        """
        try:
            # 获取脚本目录并切换
            script_dir = os.path.dirname(os.path.abspath(config.script))
            original_dir = os.getcwd()
            
            # 打印配置摘要
            if self.output_callback:
                self.output_callback("=" * 50 + "\n")
                self.output_callback("配置摘要:\n")
                self.output_callback(config.get_summary())
                self.output_callback("=" * 50 + "\n")
            
            # 构建命令
            cmd = config.get_command()
            
            # 打印命令
            if self.output_callback:
                self.output_callback("构建命令:\n")
                self.output_callback(f"{' '.join(cmd)}\n")
                self.output_callback(f"工作目录: {script_dir}\n")
                self.output_callback("=" * 50 + "\n")
            
            # 切换到脚本目录
            os.chdir(script_dir)
            
            # 执行命令
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # 读取输出
            for line in self.process.stdout:
                if self.output_callback:
                    self.output_callback(line)
                
            # 等待进程结束
            self.process.wait()
            exit_code = self.process.returncode
            
            # 恢复原目录
            os.chdir(original_dir)
            
            # 处理执行结果
            if self.is_stopped_by_user:
                success = True
                message = "用户已中断打包过程"
            elif exit_code == 0:
                success = True
                message = "打包成功完成！"
            else:
                success = False
                message = f"打包失败，退出码: {exit_code}"
            
        except Exception as e:
            # 恢复原目录
            os.chdir(original_dir)
            
            if self.is_stopped_by_user:
                success = True
                message = "用户已中断打包过程"
            else:
                success = False
                message = f"执行命令时出错: {str(e)}"
                if self.output_callback:
                    self.output_callback(f"错误: {str(e)}\n")
        finally:
            # 清理资源
            self.process = None
            self.is_running = False
            
            # 解锁标签页
            if self.lock_tab_callback:
                self.lock_tab_callback(False)
            
            # 更新状态
            if self.status_callback:
                self.status_callback("完成")
            
            # 调用完成回调
            if self.finish_callback:
                self.finish_callback(success, message)
    
    def stop(self) -> bool:
        """停止当前执行的命令
        
        Returns:
            bool: 是否成功停止
        """
        if self.process and self.is_running:
            try:
                # 设置用户停止标志
                self.is_stopped_by_user = True
                
                # 先设置状态为停止中
                if self.status_callback:
                    self.status_callback("停止中")
                
                # 尝试关闭标准输出管道，避免子进程写入错误
                if hasattr(self.process.stdout, 'close'):
                    try:
                        self.process.stdout.close()
                    except Exception:
                        pass
                
                # 终止进程
                self.process.terminate()
                
                # 等待进程结束，超时5秒
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # 超时后强制终止
                    self.process.kill()
                
                self.is_running = False
                
                # 解锁标签页
                if self.lock_tab_callback:
                    self.lock_tab_callback(False)
                
                # 更新状态
                if self.status_callback:
                    self.status_callback("已停止")
                
                # 输出停止信息
                if self.output_callback:
                    self.output_callback("\n用户中断了打包过程\n")
                
                return True
            except Exception as e:
                if self.output_callback:
                    self.output_callback(f"停止命令时出错: {str(e)}\n")
                # 确保状态正确更新
                self.is_running = False
                self.is_stopped_by_user = True
                if self.lock_tab_callback:
                    self.lock_tab_callback(False)
                if self.status_callback:
                    self.status_callback("已停止")
                return False
        return False
    
    def is_executing(self) -> bool:
        """检查是否正在执行命令
        
        Returns:
            bool: 是否正在执行
        """
        return self.is_running