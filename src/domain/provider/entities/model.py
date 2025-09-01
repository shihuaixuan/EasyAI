"""
Model实体
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class Model:
    """
    模型实体
    """
    provider_id: int
    model_name: str
    type: str  # 模型类型，如 'llm', 'embedding', 'rerank'
    subtype: Optional[str] = None  # 子类型，如 'chat', 'completion'
    metadata: Optional[Dict[str, Any]] = None
    id: Optional[int] = None
    is_delete: int = 0  # 软删除标记，0-未删除，1-已删除
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        # 验证必填字段
        if not self.provider_id or self.provider_id <= 0:
            raise ValueError("提供商ID必须为正整数")
        
        if not self.model_name or not self.model_name.strip():
            raise ValueError("模型名称不能为空")
        
        if not self.type or not self.type.strip():
            raise ValueError("模型类型不能为空")
        
        # 标准化字段
        self.model_name = self.model_name.strip()
        self.type = self.type.strip().lower()
        if self.subtype:
            self.subtype = self.subtype.strip().lower()
        
        # 验证支持的模型类型
        supported_types = {'llm', 'embedding', 'rerank'}
        if self.type not in supported_types:
            raise ValueError(f"不支持的模型类型: {self.type}，支持的类型: {supported_types}")
        
        # 初始化metadata
        if self.metadata is None:
            self.metadata = {}
    
    @classmethod
    def create(
        cls,
        provider_id: int,
        model_name: str,
        model_type: str,
        subtype: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "Model":
        """
        创建新的Model实体
        """
        return cls(
            provider_id=provider_id,
            model_name=model_name,
            type=model_type,
            subtype=subtype,
            metadata=metadata or {}
        )
    
    def update_metadata(self, metadata: Dict[str, Any]) -> None:
        """更新模型元数据"""
        if self.metadata is None:
            self.metadata = {}
        self.metadata.update(metadata)
        self.updated_at = datetime.now()
    
    def mark_as_deleted(self) -> None:
        """标记为已删除（软删除）"""
        self.is_delete = 1
        self.updated_at = datetime.now()
    
    def restore(self) -> None:
        """恢复已删除的记录"""
        self.is_delete = 0
        self.updated_at = datetime.now()
    
    def is_deleted(self) -> bool:
        """检查是否已被删除"""
        return self.is_delete == 1
    
    def get_unique_key(self) -> str:
        """获取唯一标识键（提供商ID + 模型名称）"""
        return f"{self.provider_id}:{self.model_name}"
    
    def get_metadata_json(self) -> str:
        """获取JSON格式的元数据"""
        return json.dumps(self.metadata, ensure_ascii=False) if self.metadata else "{}"
    
    def set_metadata_from_json(self, json_str: str) -> None:
        """从JSON字符串设置元数据"""
        try:
            self.metadata = json.loads(json_str) if json_str else {}
        except json.JSONDecodeError as e:
            raise ValueError(f"无效的JSON格式: {e}")
    
    def __str__(self) -> str:
        return f"Model(id={self.id}, provider_id={self.provider_id}, name={self.model_name}, type={self.type})"