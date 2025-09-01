"""
领域异常定义
"""


class DomainError(Exception):
    """领域层基础异常"""
    pass


class ProviderDomainError(DomainError):
    """Provider领域异常"""
    pass


class ProviderAlreadyExistsError(ProviderDomainError):
    """Provider已存在异常"""
    def __init__(self, user_id: int, provider_name: str):
        self.user_id = user_id
        self.provider_name = provider_name
        super().__init__(f"用户 {user_id} 的提供商 {provider_name} 已存在")


class ProviderNotFoundError(ProviderDomainError):
    """Provider未找到异常"""
    def __init__(self, identifier: str):
        self.identifier = identifier
        super().__init__(f"Provider未找到: {identifier}")


class ModelDomainError(DomainError):
    """Model领域异常"""
    pass


class ModelAlreadyExistsError(ModelDomainError):
    """Model已存在异常"""
    def __init__(self, provider_id: int, model_name: str):
        self.provider_id = provider_id
        self.model_name = model_name
        super().__init__(f"提供商 {provider_id} 的模型 {model_name} 已存在")


class ModelNotFoundError(ModelDomainError):
    """Model未找到异常"""
    def __init__(self, identifier: str):
        self.identifier = identifier
        super().__init__(f"Model未找到: {identifier}")


class RepositoryError(DomainError):
    """仓储操作异常"""
    pass