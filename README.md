# README

## Operator List

目前支持的操作有：

| 操作                      | 格式    | 示例    |
|---------------------------|---------|---------|
| 打x点伤害                 | x       | 3       |
| 打x点伤害并且进行触发判定 | xt      | 3t      |
| moka x张牌                | moka(x) | moka(3) |

这些操作对大小写不敏感。

## 使用的库

以下是本项目使用到的库：

1. `matplotlib`: 用于绘制图形以及将Matplotlib图形嵌入到Tkinter窗口中。
2. `networkx`: 用于构建有向图。
3. `graphviz`: 用于绘制有向图。

## 快速开始

### 环境准备

确保你的Python环境中已经安装了上述库。如果没有安装，可以使用以下命令进行安装：

```bash
pip install matplotlib networkx graphviz
```

### 运行程序

克隆或下载本项目到本地计算机后，进入项目目录，通过以下命令运行程序：

```bash
python gui.py
```

运行上述命令后，一个Tkinter窗口将会弹出，用户可以在该窗口中进行相应的操作。
