# !/usr/bin/env python3
"""
==============================================================
Description  : 依赖检查工具模块 - 提供依赖检测、安装建议、兼容性检查等功能
Develop      : VSCode
Author       : sandorn sandorn@live.cn
LastEditTime : 2025-10-18 22:00:00
Github       : https://github.com/sandorn/xtdamo

本模块提供以下核心功能:
- 依赖可用性检测 (check_dependency)
- 批量依赖检查 (check_dependencies)
- 可用依赖列表获取 (get_available_dependencies)
- 缺失依赖检测 (get_missing_dependencies)
- 安装命令生成 (get_installation_commands)

主要特性:
- 使用importlib.util.find_spec进行高效检测
- 支持可选依赖和必需依赖
- 自动生成安装命令
- 预定义常用依赖检查
- 异常处理和错误恢复
==============================================================
"""

from __future__ import annotations

from importlib.util import find_spec


class DependencyChecker:
    """依赖检查工具类"""

    # 项目依赖映射
    DEPENDENCIES = {
        "cryptography": {
            "package": "cryptography",
            "import": "cryptography.fernet",
            "description": "加密功能支持",
            "optional": True,
        },
        "win32cred": {
            "package": "pywin32",
            "import": "win32cred",
            "description": "Windows凭据管理器支持",
            "optional": True,
        },
        "win32con": {
            "package": "pywin32",
            "import": "win32con",
            "description": "Windows常量支持",
            "optional": True,
        },
        "win32gui": {
            "package": "pywin32",
            "import": "win32gui",
            "description": "Windows GUI支持",
            "optional": True,
        },
    }

    @classmethod
    def check_dependency(cls, name: str) -> bool:
        """检查单个依赖是否可用

        Args:
            name: 依赖名称

        Returns:
            bool: 是否可用
        """
        if name not in cls.DEPENDENCIES:
            return False

        import_name = cls.DEPENDENCIES[name]["import"]
        try:
            return find_spec(import_name) is not None
        except Exception:
            return False

    @classmethod
    def check_dependencies(cls, names: list[str]) -> dict[str, bool]:
        """检查多个依赖是否可用

        Args:
            names: 依赖名称列表

        Returns:
            Dict[str, bool]: 依赖可用性字典
        """
        return {name: cls.check_dependency(name) for name in names}

    @classmethod
    def get_available_dependencies(cls) -> list[str]:
        """获取所有可用的依赖

        Returns:
            List[str]: 可用依赖名称列表
        """
        return [name for name in cls.DEPENDENCIES if cls.check_dependency(name)]

    @classmethod
    def get_missing_dependencies(cls) -> list[str]:
        """获取所有缺失的依赖

        Returns:
            List[str]: 缺失依赖名称列表
        """
        return [name for name in cls.DEPENDENCIES if not cls.check_dependency(name)]

    @classmethod
    def get_dependency_info(cls, name: str) -> dict[str, str] | None:
        """获取依赖信息

        Args:
            name: 依赖名称

        Returns:
            Optional[Dict[str, str]]: 依赖信息字典
        """
        if name not in cls.DEPENDENCIES:
            return None

        info = cls.DEPENDENCIES[name].copy()
        info["available"] = str(cls.check_dependency(name))
        return info

    @classmethod
    def get_installation_commands(
        cls, missing_deps: list[str] | None = None
    ) -> list[str]:
        """获取安装命令

        Args:
            missing_deps: 缺失的依赖列表，如果为None则检查所有依赖

        Returns:
            List[str]: 安装命令列表
        """
        if missing_deps is None:
            missing_deps = cls.get_missing_dependencies()

        commands = []
        packages = set()

        for dep_name in missing_deps:
            if dep_name in cls.DEPENDENCIES:
                package = cls.DEPENDENCIES[dep_name]["package"]
                packages.add(package)

        for package in packages:
            commands.append(f"pip install {package}")

        return commands

    @classmethod
    def print_dependency_report(cls) -> None:
        """打印依赖报告"""
        print("=== xtdamo 依赖检查报告 ===")
        print()

        for name, info in cls.DEPENDENCIES.items():
            available = cls.check_dependency(name)
            status = "[OK] 可用" if available else "[X] 缺失"
            optional = " (可选)" if info["optional"] else " (必需)"

            print(f"{name}: {status}{optional}")
            print(f"  包名: {info['package']}")
            print(f"  描述: {info['description']}")
            print()

        missing = cls.get_missing_dependencies()
        if missing:
            print("缺失依赖安装命令:")
            commands = cls.get_installation_commands(missing)
            for cmd in commands:
                print(f"  {cmd}")
        else:
            print("[OK] 所有依赖都已安装")


# 便捷函数
def check_dependency(name: str) -> bool:
    """检查依赖是否可用"""
    return DependencyChecker.check_dependency(name)


def check_dependencies(names: list[str]) -> dict[str, bool]:
    """检查多个依赖是否可用"""
    return DependencyChecker.check_dependencies(names)


def get_available_dependencies() -> list[str]:
    """获取所有可用的依赖"""
    return DependencyChecker.get_available_dependencies()


def get_missing_dependencies() -> list[str]:
    """获取所有缺失的依赖"""
    return DependencyChecker.get_missing_dependencies()


# 预定义的依赖检查结果
CRYPTO_AVAILABLE = check_dependency("cryptography")
WIN32_AVAILABLE = check_dependency("win32cred") and check_dependency("win32con")
WIN32GUI_AVAILABLE = check_dependency("win32gui")


# 使用示例
if __name__ == "__main__":
    DependencyChecker.print_dependency_report()

    print("\n=== 快速检查 ===")
    print(f"加密支持: {'✅' if CRYPTO_AVAILABLE else '❌'}")
    print(f"Windows凭据管理器: {'✅' if WIN32_AVAILABLE else '❌'}")
    print(f"Windows GUI: {'✅' if WIN32GUI_AVAILABLE else '❌'}")
