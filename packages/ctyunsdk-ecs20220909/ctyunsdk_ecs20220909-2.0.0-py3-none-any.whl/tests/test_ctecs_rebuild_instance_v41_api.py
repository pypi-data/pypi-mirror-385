import unittest
import os
from core.client import CtyunClient
from core.credential import Credential
from core.exception import CtyunRequestException
from apis.apis import Apis
from apis.ctecs_rebuild_instance_v41_api import CtecsRebuildInstanceV41Api, CtecsRebuildInstanceV41Request, CtecsRebuildInstanceV41Response, CtecsRebuildInstanceV41ReturnObjResponse


class TestCtecsRebuildInstanceV41Api(unittest.TestCase):
    def setUp(self):
        self.client = CtyunClient()
        # Use environment variables or hardcoded credentials
        self.credential = Credential('<YOUR_AK>', '<YOUR_SK>')
        self.endpoint = '<YOUR_ENDPOINT>'
        self.apis = Apis(self.endpoint, self.client)
    
    def test_ctecsRebuildInstanceV41Api(self):
        # Construct request
        request = CtecsRebuildInstanceV41Request(        clientToken="rebuild-test-0001", regionID="bb9fdb42056f11eda1610242ac110002", instanceID="adc614e0-e838-d73f-0618-a6d51d09070a", userName="root", password="rebuildTest01", keyPairID="ac6040bd-0afa-55e2-6686-befe1b94dad8", imageID="b1d896e1-c977-4fd4-b6c2-5432549977be", userData="UmVidWlsZFRlc3QyMDIyMTEyNDEzMTE=", instanceName="ecm-3300", monitorService=True, payImage=True)
        
        try:
            api = CtecsRebuildInstanceV41Api()
            api.set_endpoint(self.endpoint)
            response = api.do(self.credential, self.client, self.endpoint, request)
            self.assertIsNotNone(response)  # 验证响应不为空
            print(f'Response: {response}')  # 打印响应内容
        except CtyunRequestException as e:
            pass
    
    def test_api_instance(self):
        # 验证API实例是否正确初始化
        self.assertIsNotNone(self.apis)
        self.assertIsNotNone(self.apis.ctecsrebuildinstancev41api)
    
if __name__ == '__main__':
    unittest.main()
