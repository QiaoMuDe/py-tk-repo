@echo off

@REM nuitka --standalone --windows-console-mode=disable --enable-plugin=tk-inter --windows-icon-from-ico=icos\QuickEdit.ico  QuickEdit.py

pyinstaller.exe -w -D -i .\ico\QuickEdit++.ico .\QuickEdit++.py
