"""
AutoCoder RAG SDK 数据模型

定义SDK中使用的各种数据结构。
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class RAGConfig:
    """
    RAG SDK全局配置

    配置 RAG 客户端的行为和参数。

    最简配置::

        config = RAGConfig(doc_dir="/path/to/docs")

    完整配置::

        config = RAGConfig(
            doc_dir="/path/to/docs",
            model="v3_chat",
            agentic=True,  # 使用 AgenticRAG
            product_mode="pro",  # Pro 模式
            rag_context_window_limit=100000,
            enable_hybrid_index=True,
            timeout=600,  # 10分钟超时
        )
    """

    # 文档目录（必需）
    doc_dir: str

    # 模型配置
    model: str = "v3_chat"

    # 超时配置（秒）
    timeout: int = 300  # 默认5分钟

    # RAG 配置参数
    rag_context_window_limit: int = 56000
    full_text_ratio: float = 0.7
    segment_ratio: float = 0.2
    rag_doc_filter_relevance: int = 5

    # 模式选择
    agentic: bool = False  # 是否使用 AgenticRAG
    product_mode: str = "lite"  # lite 或 pro

    # 索引配置
    enable_hybrid_index: bool = False
    disable_auto_window: bool = False
    disable_segment_reorder: bool = False

    # 可选模型配置
    recall_model: str = ""
    chunk_model: str = ""
    qa_model: str = ""
    emb_model: str = ""
    agentic_model: str = ""
    context_prune_model: str = ""

    # tokenizer 路径
    tokenizer_path: Optional[str] = None

    # 其他参数
    required_exts: str = ""
    ray_address: str = "auto"


@dataclass
class RAGQueryOptions:
    """
    单次查询的配置选项

    用于覆盖全局配置的查询级别选项。

    示例::

        # 使用默认选项
        options = RAGQueryOptions()

        # 自定义选项
        options = RAGQueryOptions(
            output_format="json",
            agentic=True,  # 本次查询使用 AgenticRAG
            model="custom_model",
            timeout=600,  # 本次查询10分钟超时
        )
    """

    # 输出格式: text, json, stream-json
    output_format: str = "text"

    # 是否使用 AgenticRAG (覆盖全局配置)
    agentic: Optional[bool] = None

    # 产品模式 (覆盖全局配置)
    product_mode: Optional[str] = None

    # 模型 (覆盖全局配置)
    model: Optional[str] = None

    # 超时时间（秒，覆盖全局配置）
    timeout: Optional[int] = None


@dataclass
class RAGResponse:
    """
    RAG 查询响应

    包含查询结果、上下文和元数据。

    示例::

        response = client.query_with_contexts("如何使用?")

        if response.success:
            print(f"答案: {response.answer}")
            print(f"参考了 {len(response.contexts)} 个文档")
        else:
            print(f"错误: {response.error}")
    """

    # 查询是否成功
    success: bool

    # 答案内容
    answer: str

    # 使用的上下文
    contexts: List[str] = field(default_factory=list)

    # 错误信息（如果有）
    error: Optional[str] = None

    # 元数据
    metadata: dict = field(default_factory=dict)

    @property
    def has_error(self) -> bool:
        """是否有错误"""
        return not self.success or self.error is not None

    @classmethod
    def success_response(
        cls, answer: str, contexts: Optional[List[str]] = None
    ) -> "RAGResponse":
        """创建成功响应"""
        return cls(success=True, answer=answer, contexts=contexts or [])

    @classmethod
    def error_response(cls, error: str) -> "RAGResponse":
        """创建错误响应"""
        return cls(success=False, answer="", error=error)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "answer": self.answer,
            "contexts": self.contexts,
            "error": self.error,
            "metadata": self.metadata,
        }


class RAGError(Exception):
    """RAG SDK基础异常类"""

    pass


class ValidationError(RAGError):
    """参数验证异常"""

    pass


class ExecutionError(RAGError):
    """执行异常"""

    def __init__(self, message: str, exit_code: int = 1):
        super().__init__(message)
        self.exit_code = exit_code
