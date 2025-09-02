/**
 * 知识库API服务
 */

// API接口定义
export interface KnowledgeBase {
  knowledge_base_id: string;
  name: string;
  description: string;
  owner_id: string;
  config: Record<string, any>;
  is_active: boolean;
  document_count: number;
  chunk_count: number;
  created_at: string;
  updated_at: string;
}

export interface CreateKnowledgeBaseRequest {
  name: string;
  description: string;
  config?: Record<string, any>;
}

export interface FileUploadResponse {
  success: boolean;
  filename: string;
  file_path?: string;
  document_id?: string;
  file_size?: number;
  content_hash?: string;
  error_message?: string;
  created_at?: string;
}

export interface FileUploadBatchResponse {
  total_files: number;
  successful_uploads: FileUploadResponse[];
  failed_uploads: FileUploadResponse[];
  success_count: number;
  error_count: number;
}

export interface WorkflowConfig {
  chunking: {
    strategy: 'parent_child' | 'general';
    separator: string;
    max_length: number;
    overlap_length: number;
    remove_extra_whitespace: boolean;
    remove_urls: boolean;
    remove_emails: boolean;  // 新增字段
    parent_separator?: string;
    parent_max_length?: number;
    child_separator?: string;
    child_max_length?: number;
  };
  embedding: {
    strategy: 'high_quality' | 'economic';
    model_name?: string;
  };
  retrieval: {
    strategy: 'vector_search' | 'fulltext_search' | 'hybrid_search';
    top_k: number;
    score_threshold: number;
    enable_rerank: boolean;
    rerank_model?: string;
  };
}

const API_BASE = 'http://localhost:8000/api/knowledge';

class KnowledgeService {
  /**
   * 创建知识库
   */
  async createKnowledgeBase(request: CreateKnowledgeBaseRequest): Promise<KnowledgeBase> {
    try {
      const response = await fetch(`${API_BASE}/knowledge-bases`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '创建知识库失败');
      }

      return await response.json();
    } catch (error) {
      console.error('创建知识库失败:', error);
      throw error;
    }
  }

  /**
   * 获取知识库列表
   */
  async getKnowledgeBases(): Promise<{ knowledge_bases: KnowledgeBase[]; total: number }> {
    try {
      const response = await fetch(`${API_BASE}/knowledge-bases`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '获取知识库列表失败');
      }

      return await response.json();
    } catch (error) {
      console.error('获取知识库列表失败:', error);
      throw error;
    }
  }

  /**
   * 获取知识库详情
   */
  async getKnowledgeBase(knowledgeBaseId: string): Promise<KnowledgeBase> {
    try {
      const response = await fetch(`${API_BASE}/knowledge-bases/${knowledgeBaseId}`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '获取知识库详情失败');
      }

      return await response.json();
    } catch (error) {
      console.error('获取知识库详情失败:', error);
      throw error;
    }
  }

  /**
   * 更新工作流配置
   */
  async updateWorkflowConfig(knowledgeBaseId: string, config: WorkflowConfig): Promise<any> {
    try {
      const response = await fetch(`${API_BASE}/knowledge-bases/${knowledgeBaseId}/config`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '更新配置失败');
      }

      return await response.json();
    } catch (error) {
      console.error('更新配置失败:', error);
      throw error;
    }
  }

  /**
   * 上传单个文件
   */
  async uploadFile(knowledgeBaseId: string, file: File): Promise<FileUploadResponse> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE}/knowledge-bases/${knowledgeBaseId}/files`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '文件上传失败');
      }

      return await response.json();
    } catch (error) {
      console.error('文件上传失败:', error);
      throw error;
    }
  }

  /**
   * 批量上传文件
   */
  async uploadFiles(knowledgeBaseId: string, files: File[]): Promise<FileUploadBatchResponse> {
    try {
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });

      const response = await fetch(`${API_BASE}/knowledge-bases/${knowledgeBaseId}/files/batch`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '批量文件上传失败');
      }

      return await response.json();
    } catch (error) {
      console.error('批量文件上传失败:', error);
      throw error;
    }
  }

  /**
   * 获取文件列表
   */
  async getFiles(knowledgeBaseId: string): Promise<any> {
    try {
      const response = await fetch(`${API_BASE}/knowledge-bases/${knowledgeBaseId}/files`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '获取文件列表失败');
      }

      return await response.json();
    } catch (error) {
      console.error('获取文件列表失败:', error);
      throw error;
    }
  }

  /**
   * 获取支持的文件类型
   */
  async getSupportedFileTypes(): Promise<any> {
    try {
      const response = await fetch(`${API_BASE}/supported-file-types`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '获取支持的文件类型失败');
      }

      return await response.json();
    } catch (error) {
      console.error('获取支持的文件类型失败:', error);
      throw error;
    }
  }

  /**
   * 删除知识库
   */
  async deleteKnowledgeBase(knowledgeBaseId: string): Promise<void> {
    try {
      const response = await fetch(`${API_BASE}/knowledge-bases/${knowledgeBaseId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '删除知识库失败');
      }
    } catch (error) {
      console.error('删除知识库失败:', error);
      throw error;
    }
  }
}

export const knowledgeService = new KnowledgeService();