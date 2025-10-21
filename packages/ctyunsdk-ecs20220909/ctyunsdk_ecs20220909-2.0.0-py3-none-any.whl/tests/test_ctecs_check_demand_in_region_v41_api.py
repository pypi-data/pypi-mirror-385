import unittest
from unittest.mock import patch
from core.client import CtyunClient
from core.credential import Credential
from apis.apis import Apis
from apis.ctecs_check_demand_in_region_v41_api import CtecsCheckDemandInRegionV41Api, \
    CtecsCheckDemandInRegionV41Request, CtecsCheckDemandInRegionV41Response


class TestCtecsCheckDemandInRegionV41Api(unittest.TestCase):
    def setUp(self):
        self.client = CtyunClient()
        self.credential = Credential('<YOUR_AK>', '<YOUR_SK>')
        self.endpoint = 'https://<YOUR_ENDPOINT>'
        self.apis = Apis(self.endpoint, self.client)

    def test_ecs_successful_request(self):
        """测试云主机可售查询成功"""
        request = CtecsCheckDemandInRegionV41Request(
            regionID='81f7728662dd11ec810800155d307d5b',
            productType='ecs',
            specName='s7.8xlarge.4',
            ecsAmount=2
        )

        # Mock成功响应
        mock_response = {
            "message": "SUCCESS",
            "description": "成功",
            "errorCode": "",
            "returnObj": {
                "hasQuota": True,
                "quotaInfo": {
                    "cpuVcoreQuota": 1000,
                    "cpuVcoreQutoa": 1000,
                    "ecsCountQuota": 1000,
                    "memQuota": 409600
                },
                "satisfied": True,
                "sellout": False,
                "usedInfo": {
                    "cpuVcoreCount": 156,
                    "ecsCount": 68,
                    "memUsed": 441
                }
            },
            "statusCode": 800
        }

        with patch.object(self.client, 'get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            api = self.apis.ctecscheckdemandinregionv41api
            response = api.do(self.credential, self.client, self.endpoint, request)

            # 验证基本响应
            self.assertEqual(response.statusCode, 800)
            self.assertEqual(response.errorCode, '')
            self.assertIsNotNone(response.returnObj)

            # 验证返回对象字段
            return_obj = response.returnObj
            self.assertTrue(return_obj.satisfied)
            self.assertFalse(return_obj.sellout)
            self.assertTrue(return_obj.hasQuota)

            # 验证配额信息
            self.assertEqual(return_obj.quotaInfo.ecsCountQuota, 1000)
            self.assertEqual(return_obj.quotaInfo.cpuVcoreQuota, 1000)
            self.assertEqual(return_obj.quotaInfo.memQuota, 409600)

            # 验证已用信息
            self.assertEqual(return_obj.usedInfo.ecsCount, 68)
            self.assertEqual(return_obj.usedInfo.cpuVcoreCount, 156)
            self.assertEqual(return_obj.usedInfo.memUsed, 441)

    def test_ebs_successful_request(self):
        """测试云硬盘可售查询成功"""
        request = CtecsCheckDemandInRegionV41Request(
            regionID='81f7728662dd11ec810800155d307d5b',
            productType='ebs',
            ebsType='SSD',
            ebsSize=500
        )

        # Mock成功响应
        mock_response = {
            "message": "SUCCESS",
            "description": "成功",
            "errorCode": "",
            "returnObj": {
                "hasQuota": True,
                "quotaInfo": {
                    "ebsCountQuota": 1000,
                    "ebsSizeQuota": 3276870
                },
                "satisfied": True,
                "sellout": False,
                "usedInfo": {
                    "ebsCount": 32,
                    "ebsSize": 1120
                }
            },
            "statusCode": 800
        }

        with patch.object(self.client, 'get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            response = CtecsCheckDemandInRegionV41Api.do(
                self.credential, self.client, self.endpoint, request
            )

            self.assertEqual(response.statusCode, 800)
            return_obj = response.returnObj
            self.assertTrue(return_obj.satisfied)
            self.assertEqual(return_obj.quotaInfo.ebsSizeQuota, 3276870)
            self.assertEqual(return_obj.quotaInfo.ebsCountQuota, 1000)
            self.assertEqual(return_obj.usedInfo.ebsSize, 1120)
            self.assertEqual(return_obj.usedInfo.ebsCount, 32)

    def test_eip_successful_request(self):
        """测试弹性IP可售查询成功"""
        request = CtecsCheckDemandInRegionV41Request(
            regionID='81f7728662dd11ec810800155d307d5b',
            productType='eip',
            eipAmount=5
        )

        # Mock成功响应
        mock_response = {
            "message": "SUCCESS",
            "description": "成功",
            "errorCode": "",
            "returnObj": {
                "hasQuota": True,
                "quotaInfo": {
                    "ipCountQuota": 51
                },
                "satisfied": True,
                "sellout": False,
                "usedInfo": {
                    "ipCount": 9
                }
            },
            "statusCode": 800
        }
        with patch.object(self.client, 'get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            response = CtecsCheckDemandInRegionV41Api.do(
                self.credential, self.client, self.endpoint, request
            )

            self.assertEqual(response.statusCode, 800)
            self.assertTrue(response.returnObj.satisfied)
            self.assertEqual(response.returnObj.quotaInfo.ipCountQuota, 51)
            self.assertEqual(response.returnObj.usedInfo.ipCount, 9)

    def test_quota_not_met(self):
        """测试配额不足情况"""
        request = CtecsCheckDemandInRegionV41Request(
            regionID='81f7728662dd11ec810800155d307d5b',
            azName='az1',
            productType='ebs',
            ebsType='SATA',
            ebsSize=3276870
        )

        # Mock配额不足响应
        mock_response = {
            "message": "User quota not met",
            "description": "用户配额不满足: 磁盘大小用户配额3276870，已使用3573，此次需求3276870",
            "error": "Region.DemandCheck.UserQuotaLimited",
            "errorCode": "Region.DemandCheck.UserQuotaLimited",
            "returnObj": {
                "hasQuota": False,
                "quotaInfo": {
                    "ebsCountQuota": 1000,
                    "ebsSizeQuota": 3276870
                },
                "usedInfo": {
                    "ebsCount": 97,
                    "ebsSize": 3573
                }
            },
            "statusCode": 900
        }

        with patch.object(self.client, 'get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            response = CtecsCheckDemandInRegionV41Response.from_json(mock_response)

            self.assertEqual(response.statusCode, 900)
            self.assertEqual(response.errorCode, 'Region.DemandCheck.UserQuotaLimited')
            self.assertFalse(response.returnObj.hasQuota)

    def test_sale_out(self):
        """测试产品售罄情况"""
        request = CtecsCheckDemandInRegionV41Request(
            regionID='81f7728662dd11ec810800155d307d5b',
            productType='ecs',
            flavorID='d7d12e87-35e3-6d65-9a4d-c3efddf73d83'
        )

        # Mock售罄响应
        mock_response = {
            "message": "flavor sale out",
            "description": "规格已售罄",
            "error": "Region.FlavorSaleCheck.SaleOut",
            "errorCode": "Region.FlavorSaleCheck.SaleOut",
            "returnObj": {
                "hasQuota": True,
                "quotaInfo": {
                    "cpuVcoreQuota": 1000,
                    "cpuVcoreQutoa": 1000,
                    "ecsCountQuota": 1000,
                    "memQuota": 409600
                },
                "satisfied": False,
                "sellout": True,
                "usedInfo": {
                    "cpuVcoreCount": 156,
                    "ecsCount": 68,
                    "memUsed": 441
                }
            },
            "statusCode": 900
        }

        with patch.object(self.client, 'get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            response = CtecsCheckDemandInRegionV41Api.do(
                self.credential, self.client, self.endpoint, request
            )

            self.assertEqual(response.statusCode, 900)
            self.assertTrue(response.returnObj.sellout)
            self.assertFalse(response.returnObj.satisfied)
            self.assertEqual(response.returnObj.hasQuota, True)

            # 验证配额信息
            self.assertEqual(response.returnObj.quotaInfo.cpuVcoreQuota, 1000)
            self.assertEqual(response.returnObj.quotaInfo.ecsCountQuota, 1000)
            self.assertEqual(response.returnObj.quotaInfo.memQuota, 409600)

            # 验证已用信息
            self.assertEqual(response.returnObj.usedInfo.cpuVcoreCount, 156)
            self.assertEqual(response.returnObj.usedInfo.ecsCount, 68)
            self.assertEqual(response.returnObj.usedInfo.memUsed, 441)

    def test_failed_request(self):
        """测试失败请求"""
        request = CtecsCheckDemandInRegionV41Request(
            regionID='invalid-region-id',
            productType='ecs',
            flavorID='invalid-flavor-id'
        )

        # Mock失败响应
        mock_response = {
            "message": "region info empty",
            "description": "资源池信息为空",
            "error": "Region.RegionInfo.Empty",
            "errorCode": "Region.RegionInfo.Empty",
            "returnObj": None,
            "statusCode": 900
        }

        with patch.object(self.client, 'get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            response = CtecsCheckDemandInRegionV41Api.do(
                self.credential, self.client, self.endpoint, request
            )

            self.assertEqual(response.statusCode, 900)
            self.assertIsNone(response.returnObj)

    def test_request_validation(self):
        """测试请求参数验证"""
        # 缺少必填参数
        with self.assertRaises(TypeError):
            CtecsCheckDemandInRegionV41Request()

        # 缺少productType
        with self.assertRaises(TypeError):
            CtecsCheckDemandInRegionV41Request(regionID='test')

        # 有效的ecs请求
        ecs_request = CtecsCheckDemandInRegionV41Request(
            regionID='test',
            productType='ecs',
            specName='test'
        )
        self.assertEqual(ecs_request.productType, 'ecs')

        # 有效的ebs请求
        ebs_request = CtecsCheckDemandInRegionV41Request(
            regionID='test',
            productType='ebs',
            ebsType='SSD'
        )
        self.assertEqual(ebs_request.productType, 'ebs')

    def test_api_instance(self):
        """验证API实例和方法"""
        api = CtecsCheckDemandInRegionV41Api()
        api.set_endpoint(self.endpoint)
        self.assertTrue(callable(api.do))
        self.assertTrue(hasattr(api, 'set_endpoint'))

        # 验证Apis集成
        self.assertIsNotNone(self.apis.ctecscheckdemandinregionv41api)


if __name__ == '__main__':
    unittest.main()
