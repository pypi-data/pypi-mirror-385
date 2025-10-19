"""配置模块测试"""

from xtdamo.config import Config
from xtdamo.secure_config import DmCredentials


class TestConfig:
    """基础配置类测试"""

    def test_get_error_message(self):
        """测试获取错误信息"""
        assert Config.get_error_message(1) == "成功"
        assert Config.get_error_message(-1) == "无法连接网络"
        assert Config.get_error_message(999) == "未知错误代码: 999"

    def test_get_bind_config(self):
        """测试获取绑定配置"""
        config = Config.get_bind_config()
        assert "display" in config
        assert "mouse" in config
        assert "keypad" in config
        assert "mode" in config

        # 测试自定义配置
        custom_config = Config.get_bind_config(display="dx", mode=103)
        assert custom_config["display"] == "dx"
        assert custom_config["mode"] == 103

    def test_validate_bind_mode(self):
        """测试验证绑定模式"""
        assert Config.validate_bind_mode("display", "gdi")
        assert not Config.validate_bind_mode("display", "invalid")
        assert Config.validate_bind_mode("mode", 101)
        assert not Config.validate_bind_mode("mode", 999)


class TestDmCredentials:
    """认证信息管理类测试"""

    def test_default_credentials(self):
        """测试默认认证信息"""
        assert DmCredentials.DEFAULT_REG_CODE is not None
        assert DmCredentials.DEFAULT_VER_INFO is not None
        assert len(DmCredentials.DEFAULT_REG_CODE) > 0
        assert len(DmCredentials.DEFAULT_VER_INFO) > 0

    def test_get_dm_credentials(self):
        """测试获取认证信息"""
        cred = DmCredentials()
        reg_code, ver_info = cred.get_dm_credentials()
        assert isinstance(reg_code, str)
        assert isinstance(ver_info, str)
        assert len(reg_code) > 0
        assert len(ver_info) > 0

    def test_set_dm_credentials_plain(self):
        """测试设置明文认证信息"""
        cred = DmCredentials()
        success = cred.set_dm_credentials("test_reg", "test_ver", "plain")
        assert success

        # 验证设置结果
        reg_code, ver_info = cred.get_dm_credentials()
        assert reg_code == "test_reg"
        assert ver_info == "test_ver"
