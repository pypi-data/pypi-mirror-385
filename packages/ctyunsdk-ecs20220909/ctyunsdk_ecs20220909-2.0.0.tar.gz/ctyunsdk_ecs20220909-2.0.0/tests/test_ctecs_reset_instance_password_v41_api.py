import unittest
import os
from core.client import CtyunClient
from core.credential import Credential
from core.exception import CtyunRequestException
from apis.apis import Apis
from apis.ctecs_reset_instance_password_v41_api import CtecsResetInstancePasswordV41Api, CtecsResetInstancePasswordV41Request, CtecsResetInstancePasswordV41Response, CtecsResetInstancePasswordV41ReturnObjResponse


class TestCtecsResetInstancePasswordV41Api(unittest.TestCase):
    def setUp(self):
        self.client = CtyunClient()
        # Use environment variables or hardcoded credentials
        self.credential = Credential('<YOUR_AK>', '<YOUR_SK>')
        self.endpoint = '<YOUR_ENDPOINT>'
        self.apis = Apis(self.endpoint, self.client)
    
    def test_ctecsResetInstancePasswordV41Api(self):
        # Construct request
        request = CtecsResetInstancePasswordV41Request(        regionID="88f8888888dd88ec888888888d888d8b", instanceID="8d8e8888-8ed8-88b8-88cb-888f8b8cf8fa", userName="root", newPassword="1qaz=WSX")
        
        try:
            api = CtecsResetInstancePasswordV41Api()
            api.set_endpoint(self.endpoint)
            response = api.do(self.credential, self.client, self.endpoint, request)
            self.assertIsNotNone(response)  # 验证响应不为空
            print(f'Response: {response}')  # 打印响应内容
        except CtyunRequestException as e:
            pass
    
    def test_api_instance(self):
        # 验证API实例是否正确初始化
        self.assertIsNotNone(self.apis)
        self.assertIsNotNone(self.apis.ctecsresetinstancepasswordv41api)
    
if __name__ == '__main__':
    unittest.main()
