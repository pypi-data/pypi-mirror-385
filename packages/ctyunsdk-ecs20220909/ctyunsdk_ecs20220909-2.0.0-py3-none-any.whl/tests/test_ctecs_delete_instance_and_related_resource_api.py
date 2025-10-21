import unittest
import os
from core.client import CtyunClient
from core.credential import Credential
from core.exception import CtyunRequestException
from apis.apis import Apis
from apis.ctecs_delete_instance_and_related_resource_api import CtecsDeleteInstanceAndRelatedResourceApi, CtecsDeleteInstanceAndRelatedResourceRequest, CtecsDeleteInstanceAndRelatedResourceResponse, CtecsDeleteInstanceAndRelatedResourceReturnObjResponse


class TestCtecsDeleteInstanceAndRelatedResourceApi(unittest.TestCase):
    def setUp(self):
        self.client = CtyunClient()
        # Use environment variables or hardcoded credentials
        ak = os.environ.get('CTYUN_AK', '')
        sk = os.environ.get('CTYUN_SK', '')
        self.credential = Credential(ak, sk)
        self.endpoint = '<YOUR_ENDPOINT>'
        self.apis = Apis(self.endpoint, self.client)
    
    def test_ctecsDeleteInstanceAndRelatedResourceApi(self):
        # Construct request
        request = CtecsDeleteInstanceAndRelatedResourceRequest(
            regionID="bb9fdb42056f11eda1610242ac110002",
            clientToken="delete-test-001",
            instanceID="755a72c6-ea40-ce04-7ad8-c9f54d38ccfd",
            deleteVolume=True,
            deleteEip=True,
        )
        
        try:
            api = CtecsDeleteInstanceAndRelatedResourceApi()
            api.set_endpoint(self.endpoint)
            response = api.do(self.credential, self.client, self.endpoint, request)
            self.assertIsNotNone(response)  # 验证响应不为空
            print(f'Response: {response}')  # 打印响应内容
        except CtyunRequestException as e:
            pass
    
    def test_api_instance(self):
        # 验证API实例是否正确初始化
        self.assertIsNotNone(self.apis)
        self.assertIsNotNone(self.apis.ctecsdeleteinstanceandrelatedresourceapi)
    
if __name__ == '__main__':
    unittest.main()
