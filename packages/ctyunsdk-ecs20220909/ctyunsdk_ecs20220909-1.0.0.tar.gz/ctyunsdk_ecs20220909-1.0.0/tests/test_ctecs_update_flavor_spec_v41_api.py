import unittest
import os
from core.client import CtyunClient
from core.credential import Credential
from core.exception import CtyunRequestException
from apis.apis import Apis
from apis.ctecs_update_flavor_spec_v41_api import CtecsUpdateFlavorSpecV41Api, CtecsUpdateFlavorSpecV41Request, CtecsUpdateFlavorSpecV41Response, CtecsUpdateFlavorSpecV41ReturnObjResponse


class TestCtecsUpdateFlavorSpecV41Api(unittest.TestCase):
    def setUp(self):
        self.client = CtyunClient()
        # Use environment variables or hardcoded credentials
        self.credential = Credential('<YOUR_AK>', '<YOUR_SK>')
        self.endpoint = '<YOUR_ENDPOINT>'
        self.apis = Apis(self.endpoint, self.client)
    
    def test_ctecsUpdateFlavorSpecV41Api(self):
        # Construct request
        request = CtecsUpdateFlavorSpecV41Request(        regionID="41f64827f25f468595ffa3a5deb5d15d", instanceID="285010af-16f1-137e-06c0-920d4bdd0026", flavorID="7fde1913-a1ac-1b4a-6d14-12783656f814", clientToken="resize3003", payVoucherPrice=None)
        
        try:
            api = CtecsUpdateFlavorSpecV41Api()
            api.set_endpoint(self.endpoint)
            response = api.do(self.credential, self.client, self.endpoint, request)
            self.assertIsNotNone(response)  # 验证响应不为空
            print(f'Response: {response}')  # 打印响应内容
        except CtyunRequestException as e:
            pass
    
    def test_api_instance(self):
        # 验证API实例是否正确初始化
        self.assertIsNotNone(self.apis)
        self.assertIsNotNone(self.apis.ctecsupdateflavorspecv41api)
    
if __name__ == '__main__':
    unittest.main()
