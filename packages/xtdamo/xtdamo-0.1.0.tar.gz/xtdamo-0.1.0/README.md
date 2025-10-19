# xtdamo

xtdamo 是一个基于大漠插件（Dm) 的封装库，用于自动化操作，包括窗口管理、鼠标控制、键盘模拟、图像识别、文本查找等功能。适用于游戏脚本、自动化测试等场景。

## 简介

xtdamo 提供了对大漠插件的高级封装，简化了与窗口、鼠标、键盘和图像识别相关的操作。主要功能包括：

-   窗口绑定与管理
-   鼠标移动与点击
-   键盘按键模拟
-   图像识别与查找
-   文本识别与查找
-   文件与注册表操作

## 安装

### 系统要求

-   **Python 3.8+ (32 位版本)** - 大漠插件仅支持 32 位 Python 环境
-   Windows 操作系统
-   大漠插件（dm.dll）

> **重要提示**: 大漠插件只能在 32 位 Python 环境下运行，请确保使用 32 位 Python 版本。

### 安装方法

1. **创建 32 位 Python 虚拟环境**：

```bash
# 确保使用32位Python创建虚拟环境
python -m venv .venv --python=python3.12-32  # 或指定32位Python路径
.venv\Scripts\activate  # Windows
```

2. **从源码安装**：

```bash
git clone https://github.com/sandorn/xtdamo.git
cd xtdamo
pip install -e .
```

3. **从 PyPI 安装**（计划中）：

```bash
pip install xtdamo
```

> **注意**: 请确保在 32 位 Python 环境中安装和运行项目。

### 大漠插件配置

将大漠插件（dm.dll）放置在项目目录中，或通过环境变量指定路径：

```bash
# 设置大漠插件认证信息（可选）
set DM_REG_CODE=your_registration_code
set DM_VER_INFO=your_version_info
```

## 使用示例

### 初始化大漠插件

```python
from xtdamo import DmExcute

# 使用默认配置初始化
dm = DmExcute()

# 或指定大漠插件路径
dm = DmExcute(dm_dirpath="path_to_dm_dll")
```

### 基本操作

```python
# 获取插件信息
print(f"版本: {dm.ver()}")
print(f"ID: {dm.GetID()}")

# 获取当前鼠标位置
x, y = dm.position
print(f"鼠标位置: ({x}, {y})")

# 移动鼠标
dm.move_to(100, 200)

# 安全点击
dm.safe_click(300, 400)
```

### 窗口操作

```python
# 查找窗口
hwnd = dm.FindWindow("Notepad", "无标题 - 记事本")

# 绑定窗口
dm.BindWindow(hwnd, "gdi", "windows3", "windows", 101)

# 在窗口内查找图像
result = dm.FindPic(0, 0, 800, 600, "button.png")
if result[0] == 1:
    x, y = result[1], result[2]
    dm.safe_click(x, y)
```

### 鼠标操作

```python
from xtdamo.mouse import Mouse

mouse = Mouse(dm)
mouse.move_to(100, 200)  # 移动鼠标到指定坐标
mouse.click_left(100, 200)  # 左键点击
```

### 键盘操作

```python
from xtdamo.key import Key

key = Key(dm)
key.press("A")  # 按下 A 键
key.down("Enter")  # 按下 Enter 键
key.up("Enter")  # 释放 Enter 键
```

## 贡献

欢迎贡献代码或提出建议！请参考 [贡献指南](CONTRIBUTING.md) 获取更多信息。

## 许可证

本项目遵循 [MIT 许可证](LICENSE)。
