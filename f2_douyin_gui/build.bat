@echo off

@REM nuitka --standalone --show-scons --windows-console-mode=disable --enable-plugin=tk-inter  f2_douyin_gui.py

pyinstaller.exe -w -D f2_douyin_gui_ctk.py