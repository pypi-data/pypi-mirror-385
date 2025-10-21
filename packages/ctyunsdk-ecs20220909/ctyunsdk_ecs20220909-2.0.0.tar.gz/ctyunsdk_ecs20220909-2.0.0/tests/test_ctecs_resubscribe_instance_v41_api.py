import unittest
import os
from core.client import CtyunClient
from core.credential import Credential
from core.exception import CtyunRequestException
from apis.apis import Apis
from apis.ctecs_resubscribe_instance_v41_api import CtecsResubscribeInstanceV41Api, CtecsResubscribeInstanceV41Request, CtecsResubscribeInstanceV41Response, CtecsResubscribeInstanceV41ReturnObjResponse


class TestCtecsResubscribeInstanceV41Api(unittest.TestCase):
    def setUp(self):
        self.client = CtyunClient()
        # Use environment variables or hardcoded credentials
        self.credential = Credential('<YOUR_AK>', '<YOUR_SK>')
        self.endpoint = '<YOUR_ENDPOINT>'
        self.apis = Apis(self.endpoint, self.client)
    
    def test_ctecsResubscribeInstanceV41Api(self):
        # Construct request
        request = CtecsResubscribeInstanceV41Request(        regionID="bb9fdb42056f11eda1610242ac110002", instanceID="8d8e8888-8ed8-88b8-88cb-888f8b8cf8fa", cycleCount=None, cycleType="MONTH", clientToken="4cf2962d-e92c-4c00-9181-cfbb2218636c", payVoucherPrice=None)
        
        try:
            api = CtecsResubscribeInstanceV41Api()
            api.set_endpoint(self.endpoint)
            response = api.do(self.credential, self.client, self.endpoint, request)
            self.assertIsNotNone(response)  # 验证响应不为空
            print(f'Response: {response}')  # 打印响应内容
        except CtyunRequestException as e:
            pass
    
    def test_api_instance(self):
        # 验证API实例是否正确初始化
        self.assertIsNotNone(self.apis)
        self.assertIsNotNone(self.apis.ctecsresubscribeinstancev41api)
    
if __name__ == '__main__':
    unittest.main()
