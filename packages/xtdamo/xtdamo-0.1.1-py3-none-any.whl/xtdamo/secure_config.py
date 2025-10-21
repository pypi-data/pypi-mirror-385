# !/usr/bin/env python3
"""
==============================================================
Description  : 安全认证信息管理模块 - 统一管理大漠插件认证信息
Develop      : VSCode
Author       : sandorn sandorn@live.cn
LastEditTime : 2025-10-18 22:00:00
Github       : https://github.com/sandorn/xtdamo

本模块提供以下核心功能:
- 认证信息存储管理 (环境变量、配置文件、加密存储)
- 多种存储方式支持 (明文、加密、Windows凭据管理器)
- 认证信息优先级获取 (环境变量 > 凭据管理器 > 加密文件 > 明文文件 > 默认值)
- 安全加密存储 (Fernet加密)
- 认证信息验证与设置

主要特性:
- 多层级存储优先级
- 安全的加密存储机制
- Windows凭据管理器集成
- 灵活的配置管理
- 异常处理和错误恢复
==============================================================
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .dependencies import CRYPTO_AVAILABLE, WIN32_AVAILABLE

# 如果可用，则导入
if CRYPTO_AVAILABLE:
    from cryptography.fernet import Fernet

if WIN32_AVAILABLE:
    import win32cred


class DmCredentials:
    """大漠插件认证信息管理类 - 统一管理所有认证相关配置"""

    # 默认认证信息（正确的认证信息）
    DEFAULT_REG_CODE = "jv965720b239b8396b1b7df8b768c919e86e10f"
    DEFAULT_VER_INFO = "ddsyyc365"

    def __init__(self, config_dir: str | None = None):
        """初始化认证信息管理器

        Args:
            config_dir: 配置文件目录，默认为用户目录下的.xtdamo文件夹
        """
        if config_dir is None:
            config_dir = Path.home() / ".xtdamo"

        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)

        self.config_file = self.config_dir / "dm_conf.json"
        self.encrypted_file = self.config_dir / "dm_conf.enc"
        self.key_file = self.config_dir / "dm_conf.key"

        # 初始化加密器
        self.cipher = None
        if CRYPTO_AVAILABLE:
            self._init_cipher()

    def _init_cipher(self):
        """初始化加密器"""
        try:
            if self.key_file.exists():
                with open(self.key_file, "rb") as f:
                    key = f.read()
            else:
                key = Fernet.generate_key()
                with open(self.key_file, "wb") as f:
                    f.write(key)
            self.cipher = Fernet(key)
        except Exception as e:
            print(f"加密器初始化失败: {e}")
            self.cipher = None

    def store_plain_config(self, config: dict[str, Any]) -> bool:
        """存储明文配置到JSON文件

        Args:
            config: 配置字典

        Returns:
            bool: 是否成功
        """
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"存储明文配置失败: {e}")
            return False

    def load_plain_config(self) -> dict[str, Any]:
        """从JSON文件加载明文配置

        Returns:
            Dict[str, Any]: 配置字典
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载明文配置失败: {e}")
        return {}

    def store_encrypted_config(self, config: dict[str, Any]) -> bool:
        """存储加密配置

        Args:
            config: 配置字典

        Returns:
            bool: 是否成功
        """
        if not self.cipher:
            print("加密器未初始化，无法存储加密配置")
            return False

        try:
            config_str = json.dumps(config, ensure_ascii=False)
            encrypted_data = self.cipher.encrypt(config_str.encode())
            with open(self.encrypted_file, "wb") as f:
                f.write(encrypted_data)
            return True
        except Exception as e:
            print(f"存储加密配置失败: {e}")
            return False

    def load_encrypted_config(self) -> dict[str, Any]:
        """加载加密配置

        Returns:
            Dict[str, Any]: 配置字典
        """
        if not self.cipher:
            print("加密器未初始化，无法加载加密配置")
            return {}

        try:
            if self.encrypted_file.exists():
                with open(self.encrypted_file, "rb") as f:
                    encrypted_data = f.read()
                decrypted_data = self.cipher.decrypt(encrypted_data)
                return json.loads(decrypted_data.decode())
        except Exception as e:
            print(f"加载加密配置失败: {e}")
        return {}

    def store_windows_credential(
        self, target_name: str, username: str, password: str
    ) -> bool:
        """存储到Windows凭据管理器

        Args:
            target_name: 目标名称
            username: 用户名
            password: 密码

        Returns:
            bool: 是否成功
        """
        if not WIN32_AVAILABLE:
            print("Windows凭据管理器不可用")
            return False

        try:
            win32cred.CredWrite(
                {
                    "Type": win32cred.CRED_TYPE_GENERIC,
                    "TargetName": target_name,
                    "UserName": username,
                    "CredentialBlob": password,
                    "Comment": "xtdamo configuration",
                    "Persist": win32cred.CRED_PERSIST_LOCAL_MACHINE,
                }
            )
            return True
        except Exception as e:
            print(f"存储Windows凭据失败: {e}")
            return False

    def load_windows_credential(self, target_name: str) -> str | None:
        """从Windows凭据管理器加载

        Args:
            target_name: 目标名称

        Returns:
            Optional[str]: 凭据内容
        """
        if not WIN32_AVAILABLE:
            return None

        try:
            cred = win32cred.CredRead(target_name, win32cred.CRED_TYPE_GENERIC)
            return cred["CredentialBlob"].decode("utf-16le")
        except Exception:
            return None

    def get_dm_credentials(self) -> tuple[str, str]:
        """获取大漠插件认证信息，按优先级尝试不同方式

        Returns:
            tuple[str, str]: (注册码, 版本信息)
        """
        # 1. 尝试环境变量
        reg_code = os.getenv("DM_REG_CODE")
        ver_info = os.getenv("DM_VER_INFO")

        if reg_code and ver_info:
            return reg_code, ver_info

        # 2. 尝试Windows凭据管理器
        reg_code = self.load_windows_credential("xtdamo_dm_reg_code")
        ver_info = self.load_windows_credential("xtdamo_dm_ver_info")

        if reg_code and ver_info:
            return reg_code, ver_info

        # 3. 尝试加密配置文件
        config = self.load_encrypted_config()
        if config.get("dm_reg_code") and config.get("dm_ver_info"):
            return config["dm_reg_code"], config["dm_ver_info"]

        # 4. 尝试明文配置文件
        config = self.load_plain_config()
        if config.get("dm_reg_code") and config.get("dm_ver_info"):
            return config["dm_reg_code"], config["dm_ver_info"]

        # 5. 使用默认值
        return (self.DEFAULT_REG_CODE, self.DEFAULT_VER_INFO)

    def set_dm_credentials(
        self, reg_code: str, ver_info: str, storage_method: str = "plain"
    ) -> bool:
        """设置大漠插件认证信息

        Args:
            reg_code: 注册码
            ver_info: 版本信息
            storage_method: 存储方式 ("env", "windows", "encrypted", "plain")

        Returns:
            bool: 是否成功
        """
        if storage_method == "env":
            os.environ["DM_REG_CODE"] = reg_code
            os.environ["DM_VER_INFO"] = ver_info
            return True

        if storage_method == "windows":
            success1 = self.store_windows_credential(
                "xtdamo_dm_reg_code", "user", reg_code
            )
            success2 = self.store_windows_credential(
                "xtdamo_dm_ver_info", "user", ver_info
            )
            return success1 and success2

        if storage_method == "encrypted":
            config = {"dm_reg_code": reg_code, "dm_ver_info": ver_info}
            return self.store_encrypted_config(config)

        if storage_method == "plain":
            config = {"dm_reg_code": reg_code, "dm_ver_info": ver_info}
            return self.store_plain_config(config)

        print(f"不支持的存储方式: {storage_method}")
        return False


# 创建全局实例
dm_credentials = DmCredentials()


# 使用示例
if __name__ == "__main__":
    # 设置认证信息（加密存储）
    dm_credentials.set_dm_credentials(
        dm_credentials.DEFAULT_REG_CODE, dm_credentials.DEFAULT_VER_INFO, "plain"
    )

    # 获取认证信息
    reg_code, ver_info = dm_credentials.get_dm_credentials()
    print(f"注册码: {reg_code}")
    print(f"版本信息: {ver_info}")
