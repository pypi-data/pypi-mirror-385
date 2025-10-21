class CtyunRequestTemplate:
    """天翼云请求模板"""
    def __init__(self):
        self.endpoint = None
        self.method = None
        self.url_path = None
        self.content_type = 'application/json;charset=UTF-8'

    @staticmethod
    def new_builder():
        """创建新的请求构建器"""
        from .request_builder import CtyunRequestBuilder
        return CtyunRequestBuilder() 