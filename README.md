# py-tk-repo 🐍

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey)](https://github.com/username/py-tk-repo)

py-tk-repo是一个集合了多个基于Python Tkinter开发的桌面应用程序的代码仓库。该仓库包含了各种实用工具，涵盖了从社交媒体数据采集、轻量级文本编辑器、AI模型界面到代码编辑器等多个领域，为用户提供了一站式的桌面应用解决方案。

## 项目概览

本仓库目前包含了五个主要项目：

1. **f2_douyin_gui** - 抖音数据采集工具的图形用户界面
2. **goLite** - 轻量级文本编辑器，具有现代化界面和搜索功能
3. **ollama-gui** - Ollama AI模型的图形用户界面
4. **quick-edit** - 功能丰富的文本编辑器，支持多种高级特性
5. **quick-edit++** - quick-edit的增强版本，提供更强大的编辑功能和现代化界面

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

#### quick-edit++

```bash
# 进入项目目录
cd ../quick-edit++

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

# 运行quick-edit++
python QuickEdit++.py
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

### quick-edit++ - 增强版文本编辑器

quick-edit++是quick-edit的增强版本，提供更现代化的界面和更强大的编辑功能：

1. **启动应用**：
   ```bash
   python QuickEdit++.py
   ```
   或者打开特定文件：
   ```bash
   python QuickEdit++.py example.txt
   ```

2. **核心特性**：
   - 模块化架构设计
   - 基于CustomTkinter的现代化界面
   - 增强的语法高亮系统
   - 智能文件编码检测
   - 自动保存和备份功能
   - 查找替换引擎优化
   - 文件变更监控和通知

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

### quick-edit++

- **应用初始化**：`app_initializer`模块负责应用启动和组件初始化
- **编辑操作**：`edit_operations`模块提供核心编辑功能
- **语法高亮**：增强的语法高亮系统支持多种编程语言
- **配置管理**：`config_manager`处理应用配置的读写和持久化
- **UI组件**：模块化UI组件设计，包括菜单、工具栏和状态栏

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

### quick-edit++

| 功能 | 描述 |
|------|------|
| 📝 增强编辑 | 基于CTkTextbox的现代编辑体验，支持高级编辑操作 |
| 🌗 美观主题 | 提供精心设计的亮色和暗色主题，支持自定义色彩 |
| 🔍 智能查找 | 增强的查找替换引擎，支持正则表达式和大小写敏感搜索 |
| 📊 文档统计 | 实时显示文档统计信息，包括字符数、行数等 |
| 💾 自动保存 | 智能自动保存功能，防止意外关闭导致数据丢失 |
| 🔄 文件监控 | 自动检测外部文件变更，提供重新加载选项 |
| 👁️ 行号显示 | 提供行号显示功能，便于导航和引用 |
| ⌨️ 快捷键支持 | 丰富的快捷键配置，提升编辑效率 |

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

### quick-edit++

quick-edit++提供了现代化的配置系统，支持更多高级选项：

1. **界面设置**
   - **主题选择**：多种精心设计的预设主题
   - **字体配置**：支持等宽字体和非等宽字体，可调整字体大小
   - **UI缩放**：界面缩放支持，适应不同显示设备
   - **颜色定制**：支持自定义语法高亮颜色

2. **编辑设置**
   - **自动缩进**：智能自动缩进，支持制表符和空格
   - **行号显示**：可配置行号显示格式和颜色
   - **语法高亮**：可配置不同语言的语法高亮规则
   - **滚动行为**：自定义滚动速度和行为

3. **文件处理**
   - **默认编码**：可配置默认文件编码
   - **自动保存**：可设置保存间隔和条件
   - **备份管理**：自动备份策略配置
   - **文件监控**：外部文件变更检测配置

4. **性能优化**
   - **语法高亮性能**：大文件处理优化选项
   - **自动完成**：代码自动完成配置
   - **缓存策略**：文件内容缓存设置

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
├── quick-edit++/           # 增强版文本编辑器
│   ├── QuickEdit++.py      # 主程序文件
│   ├── app/                # 应用核心模块
│   │   ├── __init__.py
│   │   ├── app_initializer.py    # 应用初始化
│   │   ├── auto_save_manager.py  # 自动保存管理
│   │   ├── edit_operations.py    # 编辑操作
│   │   ├── editor.py             # 编辑器核心
│   │   └── file_operations.py    # 文件操作
│   ├── config/             # 配置管理
│   │   ├── __init__.py
│   │   └── config_manager.py     # 配置管理器
│   ├── customtkinter/      # CustomTkinter库
│   │   ├── __init__.py
│   │   └── assets/               # 资源文件
│   ├── ico/                # 图标文件
│   │   └── QuickEdit++.ico       # 应用图标
│   ├── requirements.txt    # 依赖包列表
│   ├── syntax_highlighter/ # 语法高亮
│   │   ├── __init__.py
│   │   ├── handlers/             # 语言处理器
│   │   └── highlighter.py        # 高亮引擎
│   └── ui/                 # UI组件
│       ├── __init__.py
│       ├── about_dialog.py       # 关于对话框
│       ├── find_replace_dialog.py # 查找替换对话框
│       ├── menu.py               # 菜单栏
│       └── status_bar.py         # 状态栏
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

#### quick-edit++
- **主要功能**：quick-edit的增强版本，提供现代化界面和强大编辑功能
- **技术栈**：Python + CustomTkinter + 模块化架构
- **依赖**：customtkinter, 自定义语法高亮引擎, 配置管理系统