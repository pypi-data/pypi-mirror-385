import unittest
import os
from core.client import CtyunClient
from core.credential import Credential
from core.exception import CtyunRequestException
from apis.apis import Apis
from apis.ctecs_update_keypair_v41_api import CtecsUpdateKeypairV41Api, CtecsUpdateKeypairV41Request, CtecsUpdateKeypairV41Response, CtecsUpdateKeypairV41ReturnObjResponse


class TestCtecsUpdateKeypairV41Api(unittest.TestCase):
    def setUp(self):
        self.client = CtyunClient()
        # Use environment variables or hardcoded credentials
        self.credential = Credential('<YOUR_AK>', '<YOUR_SK>')
        self.endpoint = '<YOUR_ENDPOINT>'
        self.apis = Apis(self.endpoint, self.client)
    
    def test_ctecsUpdateKeypairV41Api(self):
        # Construct request
        request = CtecsUpdateKeypairV41Request(        regionID="bb9fdb42056f11eda1610242ac110002", keyPairID="", keyPairDescription="")
        
        try:
            api = CtecsUpdateKeypairV41Api()
            api.set_endpoint(self.endpoint)
            response = api.do(self.credential, self.client, self.endpoint, request)
            self.assertIsNotNone(response)  # 验证响应不为空
            print(f'Response: {response}')  # 打印响应内容
        except CtyunRequestException as e:
            pass
    
    def test_api_instance(self):
        # 验证API实例是否正确初始化
        self.assertIsNotNone(self.apis)
        self.assertIsNotNone(self.apis.ctecsupdatekeypairv41api)
    
if __name__ == '__main__':
    unittest.main()
