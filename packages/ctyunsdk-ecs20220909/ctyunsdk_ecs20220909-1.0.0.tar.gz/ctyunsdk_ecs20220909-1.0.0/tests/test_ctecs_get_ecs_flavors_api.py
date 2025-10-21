import unittest
from unittest.mock import patch

from apis.apis import Apis
from core.client import CtyunClient
from core.credential import Credential
from core.exception import CtyunRequestException
from apis.ctecs_get_ecs_flavors_api import CtecsGetEcsFlavorsRequest, CtecsGetEcsFlavorsResponse


class TestCtecsGetEcsFlavorsApi(unittest.TestCase):
    def setUp(self):
        self.client = CtyunClient()
        self.credential = Credential('<YOUR_AK>', '<YOUR_SK>')
        self.endpoint = 'https://<YOUR_ENDPOINT>'
        self.apis = Apis(self.endpoint, self.client)
        self.api = self.apis.ctecsgetecsflavorsapi

    def test_successful_request(self):
        """测试成功的API请求"""
        test_region_id = "562b89493b1a40e1b97ea05e50dd8170"
        request = CtecsGetEcsFlavorsRequest(
            regionID=test_region_id,
        )

        # Mock成功响应
        mock_response = {
            "statusCode": 800,
            "returnObj": {
                "totalCount": 2,
                "results": [
                    {
                        "flavorName": "通用型",
                        "series": "s",
                        "eipLimit": 2,
                        "pps": 45,
                        "cpuArch": "x86",
                        "multiQueue": 2,
                        "diskBandwidthBase": 1,
                        "azList": [
                            "az3"
                        ],
                        "memSize": 4,
                        "specName": "s8e.large.2",
                        "flavorType": "CPU_s8e",
                        "diskBandwidthBurst": 5,
                        "localDiskType": None,
                        "diskVolumesQuota": None,
                        "isLocalDisk": False,
                        "nicCount": 3,
                        "bandwidthBase": 1,
                        "flavorID": "test_flavor1",
                        "ctLimitCount": 25,
                        "cpuNum": 2,
                        "bandwidthMax": 5.0,
                        "diskIopsBase": 1,
                        "diskIopsBurst": 10,
                        "localDisk": None
                    },
                    {
                        "flavorName": "通用型",
                        "series": "s",
                        "eipLimit": 2,
                        "pps": 45,
                        "cpuArch": "x86",
                        "multiQueue": 2,
                        "diskBandwidthBase": 1,
                        "azList": [
                            "az3"
                        ],
                        "memSize": 8,
                        "specName": "s8e.large.4",
                        "flavorType": "CPU_s8e",
                        "diskBandwidthBurst": 5,
                        "localDiskType": None,
                        "diskVolumesQuota": None,
                        "isLocalDisk": False,
                        "nicCount": 3,
                        "bandwidthBase": 1,
                        "flavorID": "test_flavor2",
                        "ctLimitCount": 25,
                        "cpuNum": 2,
                        "bandwidthMax": 5.0,
                        "diskIopsBase": 1,
                        "diskIopsBurst": 10,
                        "localDisk": None
                    },
                ]
            }
        }

        with patch.object(self.client, 'get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            response = self.api.do(self.credential, self.client, self.endpoint, request)

            # 验证基本响应
            self.assertEqual(response.statusCode, 800)
            self.assertIsNotNone(response.returnObj)
            self.assertEqual(response.returnObj.totalCount, 2)
            self.assertEqual(len(response.returnObj.results), 2)

            # 验证规格详情
            flavor1 = response.returnObj.results[0]
            self.assertEqual(flavor1.flavorID, "test_flavor1")
            self.assertEqual(flavor1.specName, "s8e.large.2")
            self.assertEqual(flavor1.flavorType, "CPU_s8e")
            self.assertEqual(flavor1.flavorName, "通用型")
            self.assertEqual(flavor1.cpuNum, 2)
            self.assertEqual(flavor1.memSize, 4)
            self.assertEqual(flavor1.cpuArch, "x86")
            self.assertEqual(flavor1.azList, ["az3"])

            flavor2 = response.returnObj.results[1]
            self.assertEqual(flavor2.flavorID, "test_flavor2")
            self.assertEqual(flavor2.specName, "s8e.large.4")
            self.assertEqual(flavor2.cpuNum, 2)
            self.assertEqual(flavor2.memSize, 8)

    def test_az_name_successful_request(self):
        """测试传参azName成功的API请求"""
        test_region_id = "562b89493b1a40e1b97ea05e50dd8170"
        test_az_name = "az3"
        request = CtecsGetEcsFlavorsRequest(
            regionID=test_region_id,
            azName=test_az_name,
        )
        mock_response = {
            "statusCode": 800,
            "returnObj": {
                "totalCount": 1,
                "results": [
                    {
                        "flavorName": "通用型",
                        "series": "s",
                        "eipLimit": 2,
                        "pps": 45,
                        "cpuArch": "x86",
                        "multiQueue": 2,
                        "diskBandwidthBase": 1,
                        "memSize": 4,
                        "specName": "s8e.large.2",
                        "flavorType": "CPU_s8e",
                        "diskBandwidthBurst": 5,
                        "localDiskType": None,
                        "diskVolumesQuota": None,
                        "isLocalDisk": False,
                        "nicCount": 3,
                        "bandwidthBase": 1,
                        "flavorID": "test_flavor1",
                        "ctLimitCount": 25,
                        "cpuNum": 2,
                        "bandwidthMax": 5.0,
                        "diskIopsBase": 1,
                        "diskIopsBurst": 10,
                        "localDisk": None
                    }
                ]
            },
            "errorCode": "",
            "message": "",
            "description": "",
        }
        with patch.object(self.client, 'get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            response = self.api.do(self.credential, self.client, self.endpoint, request)

            # 验证基本响应
            self.assertEqual(response.statusCode, 800)
            self.assertIsNotNone(response.returnObj)
            self.assertEqual(response.returnObj.totalCount, 1)
            self.assertEqual(len(response.returnObj.results), 1)

            # 验证规格详情
            flavor1 = response.returnObj.results[0]
            self.assertEqual(flavor1.flavorID, "test_flavor1")
            self.assertEqual(flavor1.specName, "s8e.large.2")
            self.assertEqual(flavor1.flavorType, "CPU_s8e")
            self.assertEqual(flavor1.flavorName, "通用型")
            self.assertEqual(flavor1.cpuNum, 2)
            self.assertEqual(flavor1.memSize, 4)
            self.assertEqual(flavor1.cpuArch, "x86")
            self.assertEqual(flavor1.series, "s")
            self.assertIsNone(flavor1.azList)

    def test_series_successful_request(self):
        """测试传参series成功的API请求"""
        test_region_id = "562b89493b1a40e1b97ea05e50dd8170"
        test_series = "s"
        request = CtecsGetEcsFlavorsRequest(
            regionID=test_region_id,
            series=test_series,
        )
        mock_response = {
            "statusCode": 800,
            "returnObj": {
                "totalCount": 1,
                "results": [
                    {
                        "flavorName": "通用型",
                        "series": "s",
                        "eipLimit": 2,
                        "pps": 45,
                        "cpuArch": "x86",
                        "multiQueue": 2,
                        "diskBandwidthBase": 1,
                        "azList": [
                            "az3"
                        ],
                        "memSize": 4,
                        "specName": "s8e.large.2",
                        "flavorType": "CPU_s8e",
                        "diskBandwidthBurst": 5,
                        "localDiskType": None,
                        "diskVolumesQuota": None,
                        "isLocalDisk": False,
                        "nicCount": 3,
                        "bandwidthBase": 1,
                        "flavorID": "test_flavor1",
                        "ctLimitCount": 25,
                        "cpuNum": 2,
                        "bandwidthMax": 5.0,
                        "diskIopsBase": 1,
                        "diskIopsBurst": 10,
                        "localDisk": None
                    },
                ]
            },
            "errorCode": "",
            "message": "",
            "description": "",
        }
        with patch.object(self.client, 'get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            response = self.api.do(self.credential, self.client, self.endpoint, request)

            # 验证基本响应
            self.assertEqual(response.statusCode, 800)
            self.assertIsNotNone(response.returnObj)
            self.assertEqual(response.returnObj.totalCount, 1)
            self.assertEqual(len(response.returnObj.results), 1)

            # 验证规格详情
            flavor1 = response.returnObj.results[0]
            self.assertEqual(flavor1.flavorID, "test_flavor1")
            self.assertEqual(flavor1.specName, "s8e.large.2")
            self.assertEqual(flavor1.flavorType, "CPU_s8e")
            self.assertEqual(flavor1.flavorName, "通用型")
            self.assertEqual(flavor1.cpuNum, 2)
            self.assertEqual(flavor1.memSize, 4)
            self.assertEqual(flavor1.cpuArch, "x86")
            self.assertEqual(flavor1.series, "s")
            self.assertEqual(flavor1.azList, ["az3"])

    def test_az_name_and_series_successful_request(self):
        """测试传参 azName 和 series 成功的API请求"""
        test_region_id = "562b89493b1a40e1b97ea05e50dd8170"
        test_series = "s"
        test_az_name = "az3"
        request = CtecsGetEcsFlavorsRequest(
            regionID=test_region_id,
            series=test_series,
            azName=test_az_name,
        )
        mock_response = {
            "statusCode": 800,
            "returnObj": {
                "totalCount": 1,
                "results": [
                    {
                        "flavorName": "通用型",
                        "series": "s",
                        "eipLimit": 2,
                        "pps": 45,
                        "cpuArch": "x86",
                        "multiQueue": 2,
                        "diskBandwidthBase": 1,
                        "memSize": 4,
                        "specName": "s8e.large.2",
                        "flavorType": "CPU_s8e",
                        "diskBandwidthBurst": 5,
                        "localDiskType": None,
                        "diskVolumesQuota": None,
                        "isLocalDisk": False,
                        "nicCount": 3,
                        "bandwidthBase": 1,
                        "flavorID": "test_flavor1",
                        "ctLimitCount": 25,
                        "cpuNum": 2,
                        "bandwidthMax": 5.0,
                        "diskIopsBase": 1,
                        "diskIopsBurst": 10,
                        "localDisk": None
                    }
                ]
            },
            "errorCode": "",
            "message": "",
            "description": "",
        }
        with patch.object(self.client, 'get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            response = self.api.do(self.credential, self.client, self.endpoint, request)

            # 验证基本响应
            self.assertEqual(response.statusCode, 800)
            self.assertIsNotNone(response.returnObj)
            self.assertEqual(response.returnObj.totalCount, 1)
            self.assertEqual(len(response.returnObj.results), 1)

            # 验证规格详情
            flavor1 = response.returnObj.results[0]
            self.assertEqual(flavor1.flavorID, "test_flavor1")
            self.assertEqual(flavor1.specName, "s8e.large.2")
            self.assertEqual(flavor1.flavorType, "CPU_s8e")
            self.assertEqual(flavor1.flavorName, "通用型")
            self.assertEqual(flavor1.cpuNum, 2)
            self.assertEqual(flavor1.memSize, 4)
            self.assertEqual(flavor1.cpuArch, "x86")
            self.assertEqual(flavor1.series, "s")
            self.assertIsNone(flavor1.azList)

    def test_failed_request(self):
        """测试失败的API请求"""
        request = CtecsGetEcsFlavorsRequest(
            regionID="invalid_region",
            azName="invalid_az"
        )

        # Mock失败响应
        mock_response = {
            "message": "region info empty",
            "description": "资源池信息为空",
            "error": "Flavor.RegionInfo.Empty",
            "errorCode": "Flavor.RegionInfo.Empty",
            "returnObj": None,
            "statusCode": 900
        }

        with patch.object(self.client, 'get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            response = self.api.do(self.credential, self.client, self.endpoint, request)

            # 验证错误响应
            self.assertEqual(response.statusCode, 900)
            self.assertEqual(response.errorCode, "Flavor.RegionInfo.Empty")
            self.assertEqual(response.message, "region info empty")
            self.assertEqual(response.description, "资源池信息为空")
            self.assertIsNone(response.returnObj)

    def test_request_validation(self):
        """测试请求参数验证"""
        with self.assertRaises(TypeError):
            # 缺少必填参数regionID
            CtecsGetEcsFlavorsRequest()

        # 测试有效的请求参数
        valid_request = CtecsGetEcsFlavorsRequest(
            regionID="valid_region",
            azName="valid_az",
            series="s"
        )
        self.assertEqual(valid_request.regionID, "valid_region")
        self.assertEqual(valid_request.azName, "valid_az")
        self.assertEqual(valid_request.series, "s")

    def test_empty_response_handling(self):
        """测试空响应处理"""
        with self.assertRaises(ValueError):
            CtecsGetEcsFlavorsResponse.from_json({})

    def test_api_endpoint_setting(self):
        """测试API端点设置"""
        with self.assertRaises(ValueError):
            self.api.set_endpoint("invalid_endpoint")

    def test_api_request_exception(self):
        """测试API请求异常"""
        request = CtecsGetEcsFlavorsRequest(
            regionID="test_region",
            azName="test_az"
        )

        with patch.object(self.client, 'get') as mock_get:
            mock_get.side_effect = Exception("Test error")
            with self.assertRaises(CtyunRequestException):
                self.api.do(self.credential, self.client, self.endpoint, request)


if __name__ == '__main__':
    unittest.main()
