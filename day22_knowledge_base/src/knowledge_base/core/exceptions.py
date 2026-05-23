"""
自定义异常类
定义业务异常，便于统一错误处理
"""


class KnowledgeBaseException(Exception):
    """知识库基础异常"""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class DocumentNotFoundException(KnowledgeBaseException):
    """文档不存在异常"""

    def __init__(self, document_id: str):
        super().__init__(
            message=f"文档不存在: {document_id}",
            status_code=404
        )


class DuplicateDocumentException(KnowledgeBaseException):
    """重复文档异常"""

    def __init__(self, title: str):
        super().__init__(
            message=f"文档已存在: {title}",
            status_code=409
        )


class SearchException(KnowledgeBaseException):
    """搜索异常"""

    def __init__(self, message: str):
        super().__init__(
            message=f"搜索失败: {message}",
            status_code=500
        )


class EmbeddingException(KnowledgeBaseException):
    """向量嵌入异常"""

    def __init__(self, message: str):
        super().__init__(
            message=f"向量计算失败: {message}",
            status_code=500
        )
