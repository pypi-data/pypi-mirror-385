import unittest
import os
from core.client import CtyunClient
from core.credential import Credential
from core.exception import CtyunRequestException
from apis.apis import Apis
from apis.ctecs_update_instance_v41_api import CtecsUpdateInstanceV41Api, CtecsUpdateInstanceV41Request, CtecsUpdateInstanceV41Response, CtecsUpdateInstanceV41ReturnObjResponse


class TestCtecsUpdateInstanceV41Api(unittest.TestCase):
    def setUp(self):
        self.client = CtyunClient()
        # Use environment variables or hardcoded credentials
        ak = os.environ.get('CTYUN_AK', '')
        sk = os.environ.get('CTYUN_SK', '')
        self.credential = Credential(ak, sk)
        self.endpoint = '<YOUR_ENDPOINT>'
        self.apis = Apis(self.endpoint, self.client)
    
    def test_ctecsUpdateInstanceV41Api(self):
        # Construct request
        request = CtecsUpdateInstanceV41Request(
            regionID="bb9fdb42056f11eda1610242ac110002",
            instanceID="755a72c6-ea40-ce04-7ad8-c9f54d38ccfd",
            displayName="ecs-0003",
            instanceName="ecm-3300",
            instanceDescription="ecm-3300",
        )
        
        try:
            api = CtecsUpdateInstanceV41Api()
            api.set_endpoint(self.endpoint)
            response = api.do(self.credential, self.client, self.endpoint, request)
            self.assertIsNotNone(response)  # 验证响应不为空
            print(f'Response: {response}')  # 打印响应内容
        except CtyunRequestException as e:
            pass
    
    def test_api_instance(self):
        # 验证API实例是否正确初始化
        self.assertIsNotNone(self.apis)
        self.assertIsNotNone(self.apis.ctecsupdateinstancev41api)
    
if __name__ == '__main__':
    unittest.main()
