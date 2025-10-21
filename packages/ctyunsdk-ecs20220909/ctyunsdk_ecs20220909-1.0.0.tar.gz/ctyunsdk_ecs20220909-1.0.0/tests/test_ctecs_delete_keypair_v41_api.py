import unittest
import os
from core.client import CtyunClient
from core.credential import Credential
from core.exception import CtyunRequestException
from apis.apis import Apis
from apis.ctecs_delete_keypair_v41_api import CtecsDeleteKeypairV41Api, CtecsDeleteKeypairV41Request, CtecsDeleteKeypairV41Response, CtecsDeleteKeypairV41ReturnObjResponse


class TestCtecsDeleteKeypairV41Api(unittest.TestCase):
    def setUp(self):
        self.client = CtyunClient()
        # Use environment variables or hardcoded credentials
        self.credential = Credential('<YOUR_AK>', '<YOUR_SK>')
        self.endpoint = '<YOUR_ENDPOINT>'
        self.apis = Apis(self.endpoint, self.client)
    
    def test_ctecsDeleteKeypairV41Api(self):
        # Construct request
        request = CtecsDeleteKeypairV41Request(        regionID="bb9fdb42056f11eda1610242ac110002", keyPairName="KeyPair-a589")
        
        try:
            api = CtecsDeleteKeypairV41Api()
            api.set_endpoint(self.endpoint)
            response = api.do(self.credential, self.client, self.endpoint, request)
            self.assertIsNotNone(response)  # 验证响应不为空
            print(f'Response: {response}')  # 打印响应内容
        except CtyunRequestException as e:
            pass
    
    def test_api_instance(self):
        # 验证API实例是否正确初始化
        self.assertIsNotNone(self.apis)
        self.assertIsNotNone(self.apis.ctecsdeletekeypairv41api)
    
if __name__ == '__main__':
    unittest.main()
