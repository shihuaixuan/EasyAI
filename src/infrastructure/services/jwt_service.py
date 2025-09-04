import jwt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from src.domain.user.entities.user import User


class JWTService:
    """JWT服务 - 负责JWT令牌的生成和验证"""
    
    def __init__(
        self,
        secret_key: Optional[str] = None,
        algorithm: str = 'HS256',
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7
    ):
        """初始化JWT服务
        
        Args:
            secret_key: JWT签名密钥
            algorithm: 签名算法
            access_token_expire_minutes: 访问令牌过期时间（分钟）
            refresh_token_expire_days: 刷新令牌过期时间（天）
        """
        self.secret_key = secret_key or os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
    
    def create_access_token(self, user: User, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌
        
        Args:
            user: 用户实体
            expires_delta: 自定义过期时间
            
        Returns:
            JWT访问令牌
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            'sub': user.id,  # subject - 用户ID
            'username': user.username.value,
            'email': user.email.value,
            'status': int(user.status),
            'exp': expire,  # expiration time
            'iat': datetime.utcnow(),  # issued at
            'type': 'access'
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user: User, expires_delta: Optional[timedelta] = None) -> str:
        """创建刷新令牌
        
        Args:
            user: 用户实体
            expires_delta: 自定义过期时间
            
        Returns:
            JWT刷新令牌
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            'sub': user.id,
            'exp': expire,
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证令牌
        
        Args:
            token: JWT令牌
            
        Returns:
            解码后的载荷，验证失败返回None
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None  # 令牌已过期
        except jwt.InvalidTokenError:
            return None  # 令牌无效
    
    def get_user_id_from_token(self, token: str) -> Optional[str]:
        """从令牌中获取用户ID
        
        Args:
            token: JWT令牌
            
        Returns:
            用户ID，验证失败返回None
        """
        payload = self.verify_token(token)
        if payload:
            return payload.get('sub')
        return None
    
    def is_token_expired(self, token: str) -> bool:
        """检查令牌是否过期
        
        Args:
            token: JWT令牌
            
        Returns:
            是否过期
        """
        try:
            jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return False
        except jwt.ExpiredSignatureError:
            return True
        except jwt.InvalidTokenError:
            return True
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """使用刷新令牌生成新的访问令牌
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            新的访问令牌，验证失败返回None
        """
        payload = self.verify_token(refresh_token)
        if not payload or payload.get('type') != 'refresh':
            return None
        
        user_id = payload.get('sub')
        if not user_id:
            return None
        
        # 这里需要从数据库重新获取用户信息
        # 在实际使用中，应该注入用户仓储来获取用户
        # 暂时返回一个简化的令牌
        new_payload = {
            'sub': user_id,
            'exp': datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes),
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        
        return jwt.encode(new_payload, self.secret_key, algorithm=self.algorithm)


# 全局JWT服务实例
jwt_service = JWTService()