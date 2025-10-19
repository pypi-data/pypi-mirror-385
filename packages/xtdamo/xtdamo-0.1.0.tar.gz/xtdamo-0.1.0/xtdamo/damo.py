# !/usr/bin/env python
"""
==============================================================
Description  : 头部注释
Develop      : VSCode
Author       : sandorn sandorn@live.cn
Date         : 2025-05-21 16:26:08
LastEditTime : 2025-06-06 10:18:51
FilePath     : /CODE/xjLib/xt_damo/damo.py
Github       : https://github.com/sandorn/home
==============================================================
"""

from __future__ import annotations

from typing import Any

from .apiproxy import ApiProxy
from .config import Config
from .coreengine import CoreEngine
from .key import Key
from .mouse import Mouse
from .regsvr import DmRegister
from .secure_config import dm_credentials


class DmExcute:
    def __init__(self, dm_dirpath: str | None = None):
        self.RegDM = DmRegister(dm_dirpath)
        self.dm_instance = self.RegDM.dm_instance
        self.Key = Key(self.dm_instance)
        self.Mouse = Mouse(self.dm_instance)
        self.ApiProxy = ApiProxy(self.dm_instance)
        self.CoreEngine = CoreEngine(self.dm_instance)
        # 动态映射组件
        self._components = {
            "Key": self.Key,
            "Mouse": self.Mouse,
            "ApiProxy": self.ApiProxy,
            "CoreEngine": self.CoreEngine,
        }

        # 更严格的检查，确保dm_instance不为None
        if self.dm_instance is None:
            raise RuntimeError("大漠插件实例初始化失败")

        # 确保不为None
        if not all([self.Key, self.Mouse, self.CoreEngine, self.ApiProxy]):
            raise RuntimeError("模块初始化失败")

        # 从统一认证管理器获取认证信息
        reg_code, ver_info = dm_credentials.get_dm_credentials()
        tmp_ret = self.dm_instance.Reg(reg_code, ver_info)

        if tmp_ret != 1:
            error_msg = Config.get_error_message(tmp_ret)
            print(f"授权失败,错误代码：{tmp_ret} | 授权问题： {error_msg}")
            raise RuntimeError(f"授权失败,错误代码：{tmp_ret} | 授权问题： {error_msg}")

    def __repr__(self) -> str:
        """返回对象的字符串表示"""
        try:
            return f"版本：{self.ver()} , ID：{self.GetID()}"
        except Exception as e:
            return f"获取版本和ID时出错: {e}"

    def __getattr__(self, key: str) -> Any:
        for _, component in self._components.items():
            if hasattr(component, key):
                return getattr(component, key)

        # 最后尝试大漠原生方法，确保dm_instance不为None
        if self.dm_instance is not None:
            try:
                return getattr(self.dm_instance, key)
            except AttributeError:
                pass

        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{key}'"
        )


def conv_to_rgb(color: str) -> tuple[int, int, int]:
    """将16进制颜色字符串转换为RGB元组"""
    rgb_str = [color[:2], color[2:4], color[4:6]]
    rgb = [int(i, 16) for i in rgb_str]
    return tuple(rgb)
