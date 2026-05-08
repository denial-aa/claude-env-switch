# Claude Code 环境管理器

通过可视化界面轻松管理多个 Claude Code 研发环境，支持 Windows 系统。

## 功能特性

- **多环境管理**：创建、切换、删除不同的 Claude Code 配置环境
- **现代化界面**：基于 PyQt6 的美观 GUI 操作界面
- **快速启动脚本**：自动生成 .bat 脚本，一键启动指定环境
- **环境变量管理**：自动配置 CLAUDE_CONFIG_DIR
- **环境隔离**：不同项目使用独立的 Claude Code 配置

## 系统要求

- Windows 10/11
- Python 3.8+
- Claude Code 已安装

## 快速开始

### 安装

```bash
# 克隆项目
git clone <repository-url>
cd claude-env-switch

# 安装依赖
pip install PyQt6

# 运行程序
python main.py
```

### 使用指南

1. **添加环境**
   - 点击"添加环境"按钮
   - 输入环境名称（如：work、personal）
   - 选择配置目录路径
   - 可选：添加描述信息

2. **从默认环境创建**
   - 点击"从默认创建"按钮
   - 输入新环境名称
   - 程序将自动复制 ~/.claude 目录

3. **切换环境**
   - 在环境列表中选择目标环境
   - 点击"切换环境"按钮

4. **创建快速启动脚本**
   - 选择环境后点击"创建脚本"
   - 点击"添加到 PATH"按钮
   - 之后可在任意终端直接输入环境名称启动

## 项目结构

```
claude-env-switch/
├── main.py              # PyQt6 可视化界面主程序
├── config_manager.py    # 环境管理核心功能
├── script_manager.py    # 快速启动脚本管理
├── test.py              # 测试脚本
├── requirements.txt     # Python 依赖
├── .gitignore           # Git 忽略配置
└── README.md            # 项目说明文档
```

## 环境变量

程序通过设置 `CLAUDE_CONFIG_DIR` 环境变量来切换 Claude Code 的配置目录。

## 快速启动脚本示例

生成的 .bat 脚本内容如下：

```bat
@echo off
set CLAUDE_CONFIG_DIR=D:\claude-work
claude %*
```

## 开发

### 运行测试

```bash
python test.py
```

## 许可证

MIT License
