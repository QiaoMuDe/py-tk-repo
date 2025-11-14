@echo off

@REM nuitka --standalone --windows-console-mode=disable --enable-plugin=tk-inter --windows-icon-from-ico=.\ico\QuickEdit++.ico  .\QuickEdit++.py
@REM cd QuickEdit++.dist
@REM 7z a -tzip nuitka-QuickEditPlus.zip QuickEdit++

pyinstaller.exe -w -D -i .\ico\QuickEdit++.ico .\QuickEdit++.py
cd dist
7z a -tzip pyinstaller-QuickEditPlus.zip QuickEdit++
