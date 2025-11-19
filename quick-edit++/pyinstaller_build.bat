@echo off

pyinstaller.exe -w -D -i .\icons\QuickEdit++.ico .\QuickEdit++.py
cd dist
7z a -tzip pyinstaller-QuickEditPlus.zip QuickEdit++
