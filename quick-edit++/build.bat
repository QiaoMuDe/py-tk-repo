@echo off

@REM nuitka --standalone --windows-console-mode=disable --enable-plugin=tk-inter --windows-icon-from-ico=.\icos\QuickEdit++.ico  .\QuickEdit++.py
@REM move QuickEdit++.dist QuickEdit++
@REM 7z a -tzip nuitka-QuickEditPlus.zip QuickEdit++

pyinstaller.exe -w -D -i .\icos\QuickEdit++.ico .\QuickEdit++.py
cd dist
7z a -tzip pyinstaller-QuickEditPlus.zip QuickEdit++
