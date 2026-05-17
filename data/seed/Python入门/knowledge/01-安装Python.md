# 安装 Python

## 下载

1. 打开 [python.org](https://www.python.org/downloads/)
2. 点击黄色的 **Download Python 3.x** 按钮
3. 下载完成后运行安装程序

## 安装（Windows）

⚠️ **最重要的一步**：安装时勾选 **"Add Python to PATH"**（添加到环境变量）。

然后点"Install Now"等待完成。

## 安装（Mac）

Mac 通常自带 Python，但版本较旧。推荐用 Homebrew 安装：

```bash
brew install python
```

## 验证安装

打开终端（Windows 叫"命令提示符"或"PowerShell"），输入：

```bash
python --version
```

如果看到类似 `Python 3.12.0` 的输出，说明安装成功。

## 第一行代码

在终端里输入 `python` 进入交互模式，然后输入：

```python
print("你好，世界！")
```

看到 `你好，世界！` 就成功了！

输入 `exit()` 退出交互模式。

## 写 Python 文件

1. 用任何文本编辑器（推荐 VS Code）新建一个文件
2. 命名为 `hello.py`（注意后缀是 `.py`）
3. 写入：
```python
print("你好，世界！")
print("我开始学 Python 了！")
```
4. 在终端运行：
```bash
python hello.py
```

## 推荐编辑器

| 编辑器 | 适合人群 | 特点 |
|--------|---------|------|
| VS Code | 所有人 | 免费、插件丰富、最流行 |
| PyCharm | 专业开发 | 功能强大，社区版免费 |
| Thonny | 纯新手 | 界面简单，自带 Python |
