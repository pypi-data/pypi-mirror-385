"""依赖检查模块测试"""

from xtdamo.dependencies import (
    DependencyChecker,
    check_dependency,
    get_available_dependencies,
    get_missing_dependencies,
)


class TestDependencyChecker:
    """依赖检查器测试"""

    def test_check_dependency(self):
        """测试单个依赖检查"""
        # 测试预定义依赖
        assert check_dependency("cryptography") in [True, False]  # 可能安装也可能没安装

        # 测试不存在的依赖
        assert not check_dependency("nonexistent_module_12345")

    def test_check_dependencies(self):
        """测试多个依赖检查"""
        deps = ["cryptography", "win32cred", "nonexistent_module_12345"]
        results = DependencyChecker.check_dependencies(deps)

        # 预定义依赖可能安装也可能没安装
        assert results["cryptography"] in [True, False]
        assert results["win32cred"] in [True, False]
        assert not results["nonexistent_module_12345"]

    def test_get_available_dependencies(self):
        """测试获取可用依赖"""
        available = get_available_dependencies()
        assert isinstance(available, list)

        # 检查是否包含已知的依赖
        for dep in available:
            assert dep in DependencyChecker.DEPENDENCIES

    def test_get_missing_dependencies(self):
        """测试获取缺失依赖"""
        missing = get_missing_dependencies()
        assert isinstance(missing, list)

        # 检查缺失的依赖确实不可用
        for dep in missing:
            assert not check_dependency(dep)

    def test_get_dependency_info(self):
        """测试获取依赖信息"""
        # 测试存在的依赖
        info = DependencyChecker.get_dependency_info("cryptography")
        if info:
            assert "package" in info
            assert "import" in info
            assert "description" in info
            assert "optional" in info
            assert "available" in info

        # 测试不存在的依赖
        info = DependencyChecker.get_dependency_info("nonexistent_dep")
        assert info is None

    def test_get_installation_commands(self):
        """测试获取安装命令"""
        # 测试获取所有缺失依赖的安装命令
        commands = DependencyChecker.get_installation_commands()
        assert isinstance(commands, list)

        # 检查命令格式
        for cmd in commands:
            assert cmd.startswith("pip install ")

    def test_dependency_consistency(self):
        """测试依赖一致性"""
        available = get_available_dependencies()
        missing = get_missing_dependencies()

        # 可用和缺失的依赖应该不重复
        assert not set(available) & set(missing)

        # 所有依赖都应该在可用或缺失列表中
        all_deps = set(DependencyChecker.DEPENDENCIES.keys())
        assert set(available) | set(missing) == all_deps

    def test_predefined_constants(self):
        """测试预定义常量"""
        from xtdamo.dependencies import (
            CRYPTO_AVAILABLE,
            WIN32_AVAILABLE,
            WIN32GUI_AVAILABLE,
        )

        assert isinstance(CRYPTO_AVAILABLE, bool)
        assert isinstance(WIN32_AVAILABLE, bool)
        assert isinstance(WIN32GUI_AVAILABLE, bool)

        # 验证预定义常量与检查结果一致
        assert CRYPTO_AVAILABLE == check_dependency("cryptography")
        assert WIN32_AVAILABLE == (
            check_dependency("win32cred") and check_dependency("win32con")
        )
        assert WIN32GUI_AVAILABLE == check_dependency("win32gui")
