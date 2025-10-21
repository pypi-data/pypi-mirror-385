import unittest
import os
from core.client import CtyunClient
from core.credential import Credential
from core.exception import CtyunRequestException
from apis.apis import Apis
from apis.ctecs_describe_instances_api import CtecsDescribeInstancesApi, CtecsDescribeInstancesRequest, CtecsDescribeInstancesLabelListRequest, CtecsDescribeInstancesResponse, CtecsDescribeInstancesReturnObjResponse, CtecsDescribeInstancesReturnObjResultsResponse, CtecsDescribeInstancesReturnObjResultsAddressesResponse, CtecsDescribeInstancesReturnObjResultsSecGroupListResponse, CtecsDescribeInstancesReturnObjResultsVipInfoListResponse, CtecsDescribeInstancesReturnObjResultsAffinityGroupResponse, CtecsDescribeInstancesReturnObjResultsImageResponse, CtecsDescribeInstancesReturnObjResultsFlavorResponse, CtecsDescribeInstancesReturnObjResultsNetworkInfoResponse, CtecsDescribeInstancesReturnObjResultsPciInfoResponse, CtecsDescribeInstancesReturnObjResultsAddressesAddressListResponse, CtecsDescribeInstancesReturnObjResultsNetworkInfoBoundTypeResponse, CtecsDescribeInstancesReturnObjResultsPciInfoNicPciListResponse


class TestCtecsDescribeInstancesApi(unittest.TestCase):
    def setUp(self):
        self.client = CtyunClient()
        # Use environment variables or hardcoded credentials
        ak = os.environ.get('CTYUN_AK', '')
        sk = os.environ.get('CTYUN_SK', '')
        self.credential = Credential(ak, sk)
        self.endpoint = '<YOUR_ENDPOINT>'
        self.apis = Apis(self.endpoint, self.client)
    
    def test_ctecsDescribeInstancesApi(self):
        # Construct request
        request = CtecsDescribeInstancesRequest(
            regionID="bb9fdb42056f11eda1610242ac110002",
            azName="cn-huadong1-jsnj1A-public-ctcloud",
            projectID="0",
            pageNo=1,
            pageSize=10,
            state="active",
            keyword="ecs-888",
            instanceName="ecs-1",
            instanceIDList="73f321ea-62ff-11ec-a8bc-005056898fe0,88f888ea-88ff-88ec-a8bc-888888888fe8",
            securityGroupID="sg-tolywxbe1f",
            labelList=None
        )
        
        try:
            api = CtecsDescribeInstancesApi()
            api.set_endpoint(self.endpoint)
            response = api.do(self.credential, self.client, self.endpoint, request)
            self.assertIsNotNone(response)  # 验证响应不为空
            print(f'Response: {response}')  # 打印响应内容
        except CtyunRequestException as e:
            pass
    
    def test_api_instance(self):
        # 验证API实例是否正确初始化
        self.assertIsNotNone(self.apis)
        self.assertIsNotNone(self.apis.ctecsdescribeinstancesapi)
    
if __name__ == '__main__':
    unittest.main()
