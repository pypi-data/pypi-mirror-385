from .http_methods import HttpMethods

class CtyunRequestBuilder:
    """天翼云请求构建器"""
    def __init__(self, template):
        self.template = template
        self.headers = {}
        self.params = {}
        self.body = None

    def with_credential(self, credential):
        """设置凭证"""
        self.credential = credential
        return self

    def replace_url(self, key, value):
        """替换URL参数"""
        self.template.url_path = self.template.url_path.replace(key, value)
        return self

    def build(self):
        """构建请求"""
        from .request import CtyunRequest
        return CtyunRequest(
            url=self.template.endpoint + self.template.url_path,
            method=self.template.method,
            headers=self.headers,
            params=self.params,
            body=self.body,
            credential=self.credential
        ) 