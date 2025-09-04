from enum import IntEnum


class UserStatus(IntEnum):
    """用户状态枚举"""
    INACTIVE = 0  # 未激活
    ACTIVE = 1    # 正常
    DISABLED = 2  # 禁用
    
    @classmethod
    def is_valid_status(cls, status: int) -> bool:
        """验证状态值是否有效"""
        return status in [cls.INACTIVE, cls.ACTIVE, cls.DISABLED]
    
    def can_login(self) -> bool:
        """检查该状态是否允许登录"""
        return self == UserStatus.ACTIVE
    
    def get_description(self) -> str:
        """获取状态描述"""
        descriptions = {
            UserStatus.INACTIVE: "未激活",
            UserStatus.ACTIVE: "正常",
            UserStatus.DISABLED: "禁用"
        }
        return descriptions.get(self, "未知状态")