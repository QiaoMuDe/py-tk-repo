@echo off

echo 开始编译...
nuitka --standalone --windows-console-mode=disable --enable-plugin=tk-inter --windows-icon-from-ico=.\icons\QuickEdit++.ico  .\QuickEdit++.py
move QuickEdit++.dist QuickEdit++
7z a -tzip nuitka-QuickEditPlus.zip QuickEdit++