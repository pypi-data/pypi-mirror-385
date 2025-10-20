# welllog_ui

WellLog UI 是一个基于 PySide6 的井筒测井数据可视化与深度学习处理界面组件集合。它提供交互式曲线展示、筛选、选择等功能，并集成了深度学习相关流程。

## 特性
- 交互式测井曲线展示（基于 `pyqtgraph`）
- 井筛选与数据过滤对话框
- 深度学习流程对话框
- 命令行入口 `welllog_ui`

## 环境要求
- Python `3.9`
- Windows 平台（包含已编译的 `.pyd` 扩展）

## 安装
```bash
pip install welllog_ui
```

## 使用
安装后可直接在命令行运行：
```bash
welllog_ui
```
或在 Python 中：
```python
import welllog_ui
# 入口函数由项目脚本 `welllog_ui` 指向 `welllog_ui.main_V2:main`
```

## 许可
本项目以专有许可发布。

## 问题反馈
- 主页：<https://github.com/wxiong_swpu/welllog_ui>
- 问题：<https://github.com/wxiong_swpu/welllog_ui/issues>