# py-tk-repo 🐍

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey)](https://github.com/username/py-tk-repo)

py-tk-repo是一个集合了多个基于Python Tkinter开发的桌面应用程序的代码仓库。该仓库包含了各种实用工具，涵盖了从社交媒体数据采集、轻量级文本编辑器、AI模型界面到代码编辑器等多个领域，为用户提供了一站式的桌面应用解决方案。

## 项目概览

本仓库目前包含了四个主要项目：

1. **f2_douyin_gui** - 抖音数据采集工具的图形用户界面
2. **goLite** - 轻量级文本编辑器，具有现代化界面和搜索功能
3. **ollama-gui** - Ollama AI模型的图形用户界面
4. **quick-edit** - 功能丰富的文本编辑器，支持多种高级特性

每个项目都是独立的，可以单独使用，同时也展示了Python Tkinter在构建现代桌面应用方面的强大能力。

## 🌟 核心特性

- 🖥️ **多平台兼容** - 支持Windows、macOS和Linux操作系统
- 🎨 **现代化UI设计** - 使用CustomTkinter等库打造美观界面
- 🧩 **模块化架构** - 各个项目独立开发，便于维护和扩展
- 🚀 **高性能实现** - 采用多线程和异步处理提升用户体验
- 🔧 **丰富功能集** - 涵盖数据采集、文本编辑、AI交互等多个领域
- 📦 **易于安装** - 简洁的依赖管理和安装流程
- 📖 **详尽文档** - 每个项目都配有完整的使用说明

## 🚀 安装指南

### 系统要求

- Python 3.6 或更高版本
- Windows、macOS 或 Linux 操作系统
- Git（用于克隆仓库）

### 克隆仓库

```bash
git clone https://github.com/username/py-tk-repo.git
cd py-tk-repo
```

### 项目特定安装

由于本仓库包含多个独立项目，每个项目可能有不同的依赖需求。以下是各项目的安装方法：

#### f2_douyin_gui

```bash
# 进入项目目录
cd f2_douyin_gui

# 安装必需的依赖
pip install f2
```

#### goLite

```bash
# 进入项目目录
cd ../goLite

# 安装依赖
pip install -r requirements.txt
```

#### ollama-gui

```bash
# 进入项目目录
cd ../ollama-gui

# 该程序只需Python标准库即可运行
# 如需额外功能，可安装Ollama服务
```

#### quick-edit

```bash
# 进入项目目录
cd ../quick-edit

# 安装依赖
pip install -r requirements.txt
```

### 运行项目

安装完成后，可以通过以下命令运行各个项目：

```bash
# 运行f2_douyin_gui
python f2_douyin_gui.py

# 运行goLite
python GoLite.py

# 运行ollama-gui
python ollama_gui.py

# 运行quick-edit
python main.py
```

## 💡 使用示例

### f2_douyin_gui - 抖音数据采集工具

f2_douyin_gui是一个图形界面工具，用于简化抖音数据采集过程：

1. **启动应用**：
   ```bash
   python f2_douyin_gui.py
   ```

2. **基本使用流程**：
   - 选择工作目录
   - 输入抖音URL链接
   - 选择下载模式（单个作品、用户主页、点赞作品等）
   - 配置保存选项（视频、音频、封面、文案）
   - 点击"执行采集"开始下载

3. **高级功能**：
   - 自定义保存路径
   - Cookie设置（用于需要登录的操作）
   - 日期区间筛选
   - 网络参数调整（超时时间、重试次数、并发连接数）

### goLite - 轻量级文本编辑器

goLite是一个现代化的文本编辑器，具有以下使用方法：

1. **启动应用**：
   ```bash
   python GoLite.py
   ```

2. **主要功能**：
   - 文件打开/保存/另存为操作
   - 文本搜索和高亮显示
   - 统计信息查看（字符数、行数等）
   - 拖拽文件打开支持

### ollama-gui - AI模型界面

ollama-gui为Ollama AI模型提供图形界面：

1. **启动应用**：
   ```bash
   python ollama_gui.py
   ```

2. **使用方法**：
   - 确保Ollama服务正在运行
   - 在界面中选择可用模型
   - 在输入框中输入问题或指令
   - 点击发送或按Enter键获取AI响应
   - 支持对话历史记录和复制功能

### quick-edit - 功能丰富的文本编辑器

quick-edit是一个功能全面的文本编辑器：

1. **启动应用**：
   ```bash
   python main.py
   ```
   或者打开特定文件：
   ```bash
   python main.py example.txt
   ```

2. **高级特性**：
   - 语法高亮
   - 主题切换（亮色/暗色模式）
   - 行号显示
   - 拖拽文件打开
   - 查找和替换功能
   - 文件编码检测和转换

## 📚 API文档概述

本仓库中的项目主要为桌面应用程序，不提供传统意义上的API。但每个项目都有其内部架构和可扩展点：

### f2_douyin_gui

- **核心组件**：基于f2命令行工具的GUI封装
- **扩展性**：可通过修改GUI组件添加新功能
- **配置接口**：支持通过界面调整所有f2命令行参数

### goLite

- **搜索模块**：`TextSearchApp`类提供文本搜索功能
- **文件操作**：内置文件读写和编码处理
- **UI组件**：使用CustomTkinter构建现代化界面

### ollama-gui

- **Ollama接口**：`OllamaInterface`类封装与Ollama服务的通信
- **聊天历史**：支持对话历史管理和显示
- **模型管理**：自动获取和显示可用模型列表

### quick-edit

- **编辑器核心**：`AdvancedTextEditor`类提供文本编辑功能
- **主题管理**：`ThemeManager`类处理主题切换
- **文件处理**：支持多种编码格式的文件读写
- **查找替换**：集成高级查找和替换功能

### 公共组件

所有项目都基于Tkinter构建，遵循相似的架构模式：
- MVC模式分离（模型-视图-控制器）
- 事件驱动的用户交互
- 异步处理避免界面冻结
- 配置文件管理

## 🛠️ 支持的功能/格式列表

### f2_douyin_gui

| 功能 | 描述 |
|------|------|
| 📥 多模式下载 | 支持单个作品、用户主页、点赞作品、收藏作品、收藏夹、合集、直播等多种下载模式 |
| 🎵 多媒体保存 | 可选择保存视频原声、视频封面、视频文案 |
| 📁 文件管理 | 支持自定义保存路径和单独文件夹保存 |
| 🔧 高级配置 | 可配置超时时间、重试次数、并发连接数等网络参数 |
| 📅 时间筛选 | 支持按日期区间筛选下载内容 |
| 🔐 Cookie支持 | 支持输入Cookie以访问需要登录的内容 |

### goLite

| 功能 | 描述 |
|------|------|
| 📝 文本编辑 | 基本的文本编辑功能（新建、打开、保存） |
| 🔍 文本搜索 | 支持文本查找和高亮显示 |
| 📊 统计信息 | 实时显示字符数、行数等统计信息 |
| 🖱️ 拖拽支持 | 支持拖拽文件到编辑器中打开 |
| 🎨 现代界面 | 使用CustomTkinter构建的现代化UI |

### ollama-gui

| 功能 | 描述 |
|------|------|
| 🤖 AI交互 | 与Ollama服务进行对话交互 |
| 📋 模型管理 | 自动获取并显示可用的AI模型列表 |
| 💬 对话历史 | 保存和显示对话历史记录 |
| 📎 内容复制 | 支持复制单条回复或全部对话历史 |
| ⚙️ 参数配置 | 可配置Ollama服务地址 |

### quick-edit

| 功能 | 描述 |
|------|------|
| 📝 高级编辑 | 支持语法高亮、行号显示等高级编辑功能 |
| 🌗 主题切换 | 支持亮色和暗色主题切换 |
| 🔍 查找替换 | 集成强大的查找和替换功能 |
| 🖱️ 拖拽支持 | 支持拖拽文件打开 |
| 📁 文件编码 | 支持多种文件编码格式（UTF-8, GBK等） |
| 🧩 插件扩展 | 支持插件扩展功能 |

## ⚙️ 配置选项说明

### f2_douyin_gui

f2_douyin_gui提供了丰富的配置选项，可通过图形界面进行调整：

1. **网络设置**
   - **超时时间**：设置网络请求的超时时间（默认30秒）
   - **重试次数**：设置请求失败后的重试次数（默认3次）
   - **并发连接**：设置同时建立的网络连接数（默认5个）

2. **任务设置**
   - **最大任务数**：设置异步任务池大小（默认10个）
   - **最大下载数**：设置最多下载的作品数量（0表示无限制）
   - **每页作品数**：设置从接口获取的每页作品数（建议不超过20）

3. **日期筛选**
   - 格式：`YYYY-MM-DD|YYYY-MM-DD`
   - 示例：`2024-01-01|2024-12-31`
   - 下载所有作品：输入`all`

### goLite

goLite的配置相对简单，主要通过界面操作完成：

1. **界面设置**
   - 字体大小和样式调整
   - 窗口大小和位置记忆
   - 主题颜色配置

### ollama-gui

ollama-gui的配置主要涉及与Ollama服务的连接：

1. **服务配置**
   - **主机地址**：设置Ollama服务的主机地址（默认http://127.0.0.1:11434）
   - **模型选择**：从下拉列表中选择要使用的AI模型

### quick-edit

quick-edit提供了丰富的配置选项，可通过配置文件或界面进行调整：

1. **编辑器设置**
   - **主题配置**：亮色/暗色主题切换
   - **字体设置**：字体类型、大小调整
   - **行号显示**：开启/关闭行号显示
   - **语法高亮**：支持多种编程语言的语法高亮

2. **文件处理**
   - **编码设置**：默认文件编码格式
   - **自动保存**：开启/关闭自动保存功能
   - **备份设置**：文件修改时自动创建备份

3. **高级功能**
   - **插件管理**：插件的安装、启用和禁用
   - **快捷键配置**：自定义快捷键绑定
   - **搜索设置**：搜索行为和高亮选项

## 📁 项目结构

```
py-tk-repo/
├── f2_douyin_gui/          # 抖音数据采集工具GUI
│   ├── README.md           # 项目说明文档
│   ├── build.bat           # Windows构建脚本
│   └── f2_douyin_gui.py    # 主程序文件
├── goLite/                 # 轻量级文本编辑器
│   ├── GoLite.py           # 主程序文件
│   ├── image/              # 图标资源文件夹
│   │   └── GoLite.ico      # 应用图标
│   ├── requirements.txt    # 依赖包列表
│   └── v1.3.2.txt          # 版本更新日志
├── ollama-gui/             # Ollama AI模型界面
│   └── ollama_gui.py       # 主程序文件
├── quick-edit/             # 功能丰富的文本编辑器
│   ├── bak/                # 备份文件夹
│   │   └── QuickEdit.py    # 旧版本文件
│   ├── build.bat           # Windows构建脚本
│   ├── editor.py           # 编辑器核心模块
│   ├── find_dialog.py      # 查找对话框模块
│   ├── main.py             # 主程序入口
│   ├── requirements.txt    # 依赖包列表
│   ├── test/               # 测试文件夹
│   │   ├── *.py            # 各种测试脚本
│   ├── theme_manager.py    # 主题管理模块
│   └── utils.py            # 工具函数模块
├── .gitignore              # Git忽略文件配置
└── LICENSE                 # 项目许可证文件
```

### 各项目详细说明

#### f2_douyin_gui
- **主要功能**：提供f2抖音数据采集工具的图形用户界面
- **技术栈**：Python + Tkinter
- **依赖**：f2命令行工具

#### goLite
- **主要功能**：轻量级文本编辑器
- **技术栈**：Python + CustomTkinter
- **依赖**：customtkinter, loguru, windnd

#### ollama-gui
- **主要功能**：Ollama AI模型的图形用户界面
- **技术栈**：Python + Tkinter
- **依赖**：Python标准库

#### quick-edit
- **主要功能**：功能丰富的文本编辑器
- **技术栈**：Python + Tkinter + tkinterdnd2
- **依赖**：多种第三方库（详见requirements.txt）