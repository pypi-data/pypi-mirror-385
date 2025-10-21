import unittest
import os
from core.client import CtyunClient
from core.credential import Credential
from core.exception import CtyunRequestException
from apis.apis import Apis
from apis.ctecs_create_instance_v41_api import CtecsCreateInstanceV41Api, CtecsCreateInstanceV41Request, \
    CtecsCreateInstanceV41NetworkCardListRequest, CtecsCreateInstanceV41DataDiskListRequest, \
    CtecsCreateInstanceV41LabelListRequest, CtecsCreateInstanceV41Response, CtecsCreateInstanceV41ReturnObjResponse


class TestCtecsCreateInstanceV41Api(unittest.TestCase):
    def setUp(self):
        self.client = CtyunClient()
        # Use environment variables or hardcoded credentials
        ak = os.environ.get('CTYUN_AK', '')
        sk = os.environ.get('CTYUN_SK', '')
        self.credential = Credential(ak, sk)
        self.endpoint = '<YOUR_ENDPOINT>'
        self.apis = Apis(self.endpoint, self.client)

    def test_ctecsCreateInstanceV41Api(self):
        # Construct request
        request = CtecsCreateInstanceV41Request(
            clientToken="4cf2962d-e92c-4c00-9181-cfbb2218636c",
            regionID="bb9fdb42056f11eda1610242ac110002",
            azName="cn-huadong1-jsnj1A-public-ctcloud",
            instanceName="ecm-3300",
            displayName="ecm-3300",
            flavorName="m8e.large.8",
            flavorID="0824679a-dc86-47dc-a0d3-9c330928f4f6",
            imageType=None,
            imageID="9d9e8998-8ed5-43b2-99cb-322f2b8cf6fa",
            bootDiskType="SATA",
            bootDiskSize=None,
            bootDiskIsEncrypt=True,
            bootDiskCmkID="3f7e2567-4ed3-4f85-9743-c557d9a94667",
            bootDiskProvisionedIops=None,
            vpcID="4797e8a1-722d-4996-9362-458001813e41",
            onDemand=False,
            networkCardList=[
                CtecsCreateInstanceV41NetworkCardListRequest(
                    isMaster=True,
                    subnetID="subnet-12345678",
                    fixedIP="192.168.1.10",
                )
            ],
            extIP="2",
            projectID="6732237e53bc4591b0e67d750030ebe3",
            secGroupList=None,
            dataDiskList=[
                CtecsCreateInstanceV41DataDiskListRequest(
                    diskType="SAS",
                    diskSize=100,
                    isEncrypt=False,
                    cmkID=None,
                    provisionedIops=None,
                    diskName="api-test"
                )
            ],
            ipVersion="ipv4",
            bandwidth=None,
            ipv6AddressID="eip-5sdasd2gfh",
            eipID="eip-9jpeyl0frh",
            affinityGroupID="259b0c37-1044-41d8-989e",
            keyPairID="c57d0626-8a82-407b-a910-b454907778c3",
            userName="root",
            userPassword="1qaz=WSX",
            cycleCount=None,
            cycleType="MONTH",
            autoRenewStatus=None,
            userData="ZWNobyBoZWxsbyBnb3N0YWNrIQ==",
            payVoucherPrice=None,
            labelList=[
                CtecsCreateInstanceV41LabelListRequest(
                    labelKey="test-key",
                    labelValue="test-value"
                )
            ],
            gpuDriverKits="CUDA 11.4.3 Driver 470.82.01 CUDNN 8.8.1.3",
            monitorService=True,
            instanceDescription="云主机描述信息",
            lineType="bgp_standalone",
            demandBillingType="upflowc",
            securityProduct="EnterpriseEdition",
            segmentID="seg-g3glo55ziy",
            threadsPerCore=None
        )

        try:
            api = CtecsCreateInstanceV41Api()
            api.set_endpoint(self.endpoint)
            response = api.do(self.credential, self.client, self.endpoint, request)
            self.assertIsNotNone(response)  # 验证响应不为空
            print(f'Response: {response}')  # 打印响应内容
        except CtyunRequestException as e:
            pass

    def test_api_instance(self):
        # 验证API实例是否正确初始化
        self.assertIsNotNone(self.apis)
        self.assertIsNotNone(self.apis.ctecscreateinstancev41api)


if __name__ == '__main__':
    unittest.main()
