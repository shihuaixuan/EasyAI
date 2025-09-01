"""
API Key 加密服务
"""
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
from typing import Optional


class EncryptionService:
    """
    API Key 加密服务
    使用 Fernet 对称加密
    """
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        初始化加密服务
        
        Args:
            secret_key: 可选的密钥，如果不提供则从环境变量获取
        """
        self._secret_key = secret_key or os.getenv('ENCRYPTION_SECRET_KEY', 'default-secret-key-for-development')
        self._fernet = self._get_fernet()
    
    def _get_fernet(self) -> Fernet:
        """
        获取 Fernet 实例
        """
        # 使用 PBKDF2 从密钥生成加密密钥
        password = self._secret_key.encode()
        salt = b'salt_'  # 在生产环境中应该使用随机盐
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return Fernet(key)
    
    def encrypt(self, plaintext: str) -> str:
        """
        加密明文API Key
        
        Args:
            plaintext: 明文API Key
            
        Returns:
            加密后的API Key（base64编码）
        """
        if not plaintext:
            raise ValueError("明文不能为空")
        
        encrypted_bytes = self._fernet.encrypt(plaintext.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')
    
    def decrypt(self, encrypted_text: str) -> str:
        """
        解密API Key
        
        Args:
            encrypted_text: 加密后的API Key
            
        Returns:
            明文API Key
        """
        if not encrypted_text:
            raise ValueError("加密文本不能为空")
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_text.encode('utf-8'))
            decrypted_bytes = self._fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"解密失败: {str(e)}")
    
    def mask_api_key(self, api_key: str, show_length: int = 4) -> str:
        """
        掩码显示API Key，用于前端显示
        
        Args:
            api_key: API Key
            show_length: 显示的后缀长度
            
        Returns:
            掩码后的API Key，如 "sk-***1234"
        """
        if not api_key:
            return "***"
        
        if len(api_key) <= show_length:
            return "*" * len(api_key)
        
        return f"***{api_key[-show_length:]}"


# 全局加密服务实例
encryption_service = EncryptionService()