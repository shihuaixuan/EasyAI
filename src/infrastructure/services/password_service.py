import bcrypt
from typing import Union

from src.domain.user.value_objects.password import Password, HashedPassword


class PasswordService:
    """密码服务 - 负责密码加密和验证"""
    
    def __init__(self, rounds: int = 12):
        """初始化密码服务
        
        Args:
            rounds: bcrypt加密轮数，默认12轮（安全性较高）
        """
        self.rounds = rounds
    
    def hash_password(self, password: Union[str, Password]) -> HashedPassword:
        """加密密码
        
        Args:
            password: 明文密码或密码值对象
            
        Returns:
            加密后的密码值对象
        """
        if isinstance(password, Password):
            plain_password = password.value
        else:
            plain_password = password
        
        # 生成盐值并加密密码
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
        
        return HashedPassword.create(hashed.decode('utf-8'))
    
    def verify_password(self, password: Union[str, Password], hashed_password: HashedPassword) -> bool:
        """验证密码
        
        Args:
            password: 明文密码或密码值对象
            hashed_password: 加密后的密码值对象
            
        Returns:
            密码是否匹配
        """
        if isinstance(password, Password):
            plain_password = password.value
        else:
            plain_password = password
        
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.hash_value.encode('utf-8')
            )
        except (ValueError, TypeError):
            return False
    
    def is_password_strong(self, password: Union[str, Password]) -> bool:
        """检查密码强度
        
        Args:
            password: 明文密码或密码值对象
            
        Returns:
            密码是否足够强
        """
        if isinstance(password, Password):
            return password.is_valid()
        else:
            try:
                Password.create(password)
                return True
            except ValueError:
                return False
    
    def generate_salt(self) -> str:
        """生成盐值
        
        Returns:
            Base64编码的盐值
        """
        salt = bcrypt.gensalt(rounds=self.rounds)
        return salt.decode('utf-8')


# 全局密码服务实例
password_service = PasswordService()