"""
文件上传领域服务
"""

import os
import hashlib
import mimetypes
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from ..entities.document import Document
from ..vo.workflow_config import FileUploadConfig


@dataclass
class UploadedFile:
    """上传文件信息"""
    filename: str
    content: bytes
    content_type: str
    size: int


@dataclass
class FileUploadResult:
    """文件上传结果"""
    success: bool
    filename: str
    file_path: Optional[str] = None
    document_id: Optional[str] = None
    error_message: Optional[str] = None
    file_size: Optional[int] = None
    content_hash: Optional[str] = None


class FileUploadService:
    """文件上传领域服务"""
    
    def __init__(self, config: FileUploadConfig):
        self.config = config
        self._ensure_upload_directory()
    
    def _ensure_upload_directory(self) -> None:
        """确保上传目录存在"""
        if not os.path.exists(self.config.upload_directory):
            os.makedirs(self.config.upload_directory, exist_ok=True)
    
    def validate_file(self, file: UploadedFile) -> List[str]:
        """验证文件
        
        Returns:
            错误消息列表，空列表表示验证通过
        """
        errors = []
        
        # 检查文件大小
        if file.size > self.config.max_file_size:
            errors.append(f"文件大小超过限制：{file.size} > {self.config.max_file_size}")
        
        # 检查文件扩展名
        if not self.config.is_allowed_file(file.filename):
            errors.append(f"不支持的文件类型：{file.filename}")
        
        # 检查文件名
        if not file.filename or file.filename.strip() == '':
            errors.append("文件名不能为空")
        
        # 检查文件内容
        if file.size == 0:
            errors.append("文件内容为空")
        
        return errors
    
    def calculate_content_hash(self, content: bytes) -> str:
        """计算文件内容哈希"""
        return hashlib.sha256(content).hexdigest()
    
    async def save_file(
        self, 
        file: UploadedFile, 
        knowledge_base_id: str,
        custom_filename: Optional[str] = None
    ) -> FileUploadResult:
        """保存文件到磁盘
        
        Args:
            file: 上传的文件
            knowledge_base_id: 知识库ID
            custom_filename: 自定义文件名
            
        Returns:
            文件上传结果
        """
        try:
            # 验证文件
            validation_errors = self.validate_file(file)
            if validation_errors:
                return FileUploadResult(
                    success=False,
                    filename=file.filename,
                    error_message="; ".join(validation_errors)
                )
            
            # 生成文件路径
            filename = custom_filename or file.filename
            safe_filename = self._sanitize_filename(filename)
            knowledge_base_dir = os.path.join(self.config.upload_directory, knowledge_base_id)
            
            # 确保知识库目录存在
            os.makedirs(knowledge_base_dir, exist_ok=True)
            
            # 处理文件名冲突
            file_path = os.path.join(knowledge_base_dir, safe_filename)
            file_path = self._handle_filename_conflict(file_path)
            
            # 保存文件
            with open(file_path, 'wb') as f:
                f.write(file.content)
            
            # 计算文件哈希
            content_hash = self.calculate_content_hash(file.content)
            
            # 创建文档实体
            document = Document(
                filename=os.path.basename(file_path),
                content="",  # 内容将在解析时填充
                file_type=self._get_file_type(file.filename),
                file_size=file.size,
                knowledge_base_id=knowledge_base_id,
                original_path=file_path,
                content_hash=content_hash,
                metadata={
                    "original_filename": file.filename,
                    "content_type": file.content_type,
                    "upload_path": file_path
                }
            )
            
            return FileUploadResult(
                success=True,
                filename=file.filename,
                file_path=file_path,
                document_id=document.document_id,
                file_size=file.size,
                content_hash=content_hash
            )
            
        except Exception as e:
            return FileUploadResult(
                success=False,
                filename=file.filename,
                error_message=f"文件保存失败: {str(e)}"
            )
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名，移除危险字符"""
        import re
        # 移除路径分隔符和其他危险字符
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # 确保文件名不为空且不以点开头
        if not safe_name or safe_name.startswith('.'):
            safe_name = 'uploaded_file_' + safe_name
        return safe_name
    
    def _handle_filename_conflict(self, file_path: str) -> str:
        """处理文件名冲突"""
        if not os.path.exists(file_path):
            return file_path
        
        # 文件已存在，生成新的文件名
        base_path, extension = os.path.splitext(file_path)
        counter = 1
        
        while os.path.exists(f"{base_path}_{counter}{extension}"):
            counter += 1
        
        return f"{base_path}_{counter}{extension}"
    
    def _get_file_type(self, filename: str) -> str:
        """获取文件类型"""
        if '.' not in filename:
            return 'unknown'
        
        extension = filename.split('.')[-1].lower()
        return extension
    
    async def delete_file(self, file_path: str) -> bool:
        """删除文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """获取文件信息"""
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            content_type, _ = mimetypes.guess_type(file_path)
            
            return {
                "filename": os.path.basename(file_path),
                "size": stat.st_size,
                "created_at": stat.st_ctime,
                "modified_at": stat.st_mtime,
                "content_type": content_type or "application/octet-stream"
            }
        except Exception:
            return None