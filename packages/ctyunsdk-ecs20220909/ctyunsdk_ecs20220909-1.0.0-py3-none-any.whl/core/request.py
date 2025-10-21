import requests
from .signer import CtyunSigner
import uuid
import datetime

class CtyunRequest:
    """天翼云请求类"""
    def __init__(self, url, method, headers=None, params=None, body=None, credential=None):
        self.url = url
        self.method = method
        self.headers = headers or {}
        self.params = params or {}
        self.body = body
        self.credential = credential
        self.content_type = 'application/json;charset=UTF-8'

    def execute(self):
        """执行请求"""
        # 生成请求ID和时间
        request_id = str(uuid.uuid1())
        eop_date = datetime.datetime.now().strftime('%Y%m%dT%H%M%SZ')
        
        # 生成认证签名
        signature = CtyunSigner.sign(
            self.credential,
            self.params,
            self.body,
            self.method,
            self.content_type,
            request_id
        )

        # 添加认证头
        self.headers.update({
            'User-Agent': 'Mozilla/5.0(pysdk)',
            'Content-type': self.content_type,
            'ctyun-eop-request-id': request_id,
            'Eop-Authorization': f'{self.credential.ak} Headers=ctyun-eop-request-id;eop-date Signature={signature}',
            'Eop-date': eop_date
        })

        response = requests.request(
            method=self.method,
            url=self.url,
            headers=self.headers,
            params=self.params,
            json=self.body,
            verify=False
        )
        return response 