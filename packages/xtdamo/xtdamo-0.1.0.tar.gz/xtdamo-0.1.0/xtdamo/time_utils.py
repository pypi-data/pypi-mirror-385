# !/usr/bin/env python3
"""
==============================================================
Description  : 时间工具模块 - 提供时间跟踪、虚拟键码、时间控制等功能
Develop      : VSCode
Author       : sandorn sandorn@live.cn
LastEditTime : 2025-10-18 22:00:00
Github       : https://github.com/sandorn/xtdamo

本模块提供以下核心功能:
- 时间跟踪器 (TimeTracker) - 替代bdtime.tt
- 虚拟键码常量 (VirtualKeys) - 替代bdtime.vk
- 时间控制与延迟 (sleep, during)
- 按键状态检测 (get_key_state, is_pressed)
- 时间戳获取 (now)

主要特性:
- 完全替代bdtime依赖
- 高性能时间跟踪
- 丰富的虚拟键码支持
- 智能按键状态检测
- 异常处理和错误恢复
==============================================================
"""

from __future__ import annotations

import time


class TimeTracker:
    """时间跟踪器，用于替代bdtime.tt"""

    def __init__(self, timeout: float = 0):
        """初始化时间跟踪器

        Args:
            timeout: 超时时间（秒），0表示无限制
        """
        self.start_time = time.time()
        self.timeout = timeout

    def during(self, timeout: float | None = None) -> bool:
        """检查是否在指定时间内

        Args:
            timeout: 超时时间，如果为None则使用初始化时的timeout

        Returns:
            bool: 如果在时间内返回True，否则返回False
        """
        if timeout is None:
            timeout = self.timeout

        if timeout <= 0:
            return True

        return (time.time() - self.start_time) < timeout

    def elapsed(self) -> float:
        """获取已过去的时间（秒）"""
        return time.time() - self.start_time

    def remaining(self) -> float:
        """获取剩余时间（秒）"""
        if self.timeout <= 0:
            return float("inf")
        return max(0, self.timeout - self.elapsed())


def sleep(duration: float) -> None:
    """睡眠指定时间"""
    time.sleep(duration)


def now(format_type: int = 0) -> str:
    """获取当前时间字符串

    Args:
        format_type: 格式类型
            0: 默认格式
            1: 包含毫秒的格式

    Returns:
        str: 格式化的时间字符串
    """
    if format_type == 1:
        return (
            time.strftime("%H:%M:%S", time.localtime())
            + f".{int(time.time() * 1000) % 1000:03d}"
        )
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


# 虚拟键码常量（替代bdtime.vk）
class VirtualKeys:
    """虚拟键码常量"""

    # 鼠标按键
    MOUSE_LEFT = 0x01
    MOUSE_RIGHT = 0x02
    MOUSE_MIDDLE = 0x04

    # 常用按键
    ESC = 0x1B
    ENTER = 0x0D
    SPACE = 0x20
    TAB = 0x09
    BACKSPACE = 0x08
    DELETE = 0x2E

    # 功能键
    F1 = 0x70
    F2 = 0x71
    F3 = 0x72
    F4 = 0x73
    F5 = 0x74
    F6 = 0x75
    F7 = 0x76
    F8 = 0x77
    F9 = 0x78
    F10 = 0x79
    F11 = 0x7A
    F12 = 0x7B

    # 修饰键
    SHIFT = 0x10
    CTRL = 0x11
    ALT = 0x12

    # 数字键
    NUM_0 = 0x30
    NUM_1 = 0x31
    NUM_2 = 0x32
    NUM_3 = 0x33
    NUM_4 = 0x34
    NUM_5 = 0x35
    NUM_6 = 0x36
    NUM_7 = 0x37
    NUM_8 = 0x38
    NUM_9 = 0x39

    # 字母键
    A = 0x41
    B = 0x42
    C = 0x43
    D = 0x44
    E = 0x45
    F = 0x46
    G = 0x47
    H = 0x48
    I = 0x49  # noqa
    J = 0x4A
    K = 0x4B
    L = 0x4C
    M = 0x4D
    N = 0x4E
    O = 0x4F  # noqa
    P = 0x50
    Q = 0x51
    R = 0x52
    S = 0x53
    T = 0x54
    U = 0x55
    V = 0x56
    W = 0x57
    X = 0x58
    Y = 0x59
    Z = 0x5A


# 创建全局实例
tt = TimeTracker()
vk = VirtualKeys()
