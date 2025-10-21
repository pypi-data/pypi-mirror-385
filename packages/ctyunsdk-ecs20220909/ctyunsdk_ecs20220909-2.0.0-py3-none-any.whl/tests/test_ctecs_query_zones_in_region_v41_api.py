import unittest
from unittest.mock import patch
from core.client import CtyunClient
from core.credential import Credential
from apis.apis import Apis
from apis.ctecs_query_zones_in_region_v41_api import CtecsQueryZonesInRegionV41Request


class TestCtecsQueryZonesInRegionV41Api(unittest.TestCase):
    def setUp(self):
        self.client = CtyunClient()
        # Use environment variables or hardcoded credentials
        self.credential = Credential('<YOUR_AK>', '<YOUR_SK>')
        self.endpoint = 'https://<YOUR_ENDPOINT>'
        self.apis = Apis(self.endpoint, self.client)

    def test_successful_request(self):
        """测试成功的API请求"""
        test_region_id = "81f7728662dd11ec810800155d307d5b"
        request = CtecsQueryZonesInRegionV41Request(regionID=test_region_id)

        # Mock成功响应
        mock_response = {
            "statusCode": 800,
            "message": "SUCCESS",
            "description": "成功",
            "errorCode": "",
            "returnObj": {
                "zoneList": [
                    {
                        "name": "az1",
                        "azDisplayName": "西北-内蒙演示1"
                    },
                    {
                        "name": "az2",
                        "azDisplayName": "西北-内蒙演示2"
                    }
                ]
            }
        }

        with patch.object(self.client, 'get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            api = self.apis.ctecsqueryzonesinregionv41api
            response = api.do(self.credential, self.client, self.endpoint, request)

            # 验证基本响应
            self.assertEqual(response.statusCode, 800)
            self.assertEqual(response.errorCode, "")
            self.assertIsNotNone(response.returnObj)

            # 验证返回对象字段
            return_obj = response.returnObj
            self.assertEqual(len(return_obj.zoneList), 2)
            self.assertEqual(return_obj.zoneList[0].name, "az1")
            self.assertEqual(return_obj.zoneList[0].azDisplayName, "西北-内蒙演示1")

    def test_failed_request(self):
        """测试失败的API请求"""
        request = CtecsQueryZonesInRegionV41Request(regionID="invalid_region_id")

        # Mock失败响应
        mock_response = {
            "message": "Not found region by ID, check the ID and contact the admin",
            "description": "没找到该资源池，请检查资源池ID是否正确，如资源池ID无误请联系管理员",
            "error": "Unknown.Region.RegionIDError",
            "errorCode": "Unknown.Region.RegionIDError",
            "returnObj": None,
            "statusCode": 900
        }

        with patch.object(self.client, 'get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            api = self.apis.ctecsqueryzonesinregionv41api
            response = api.do(self.credential, self.client, self.endpoint, request)

            # 验证错误响应
            self.assertEqual(response.statusCode, 900)
            self.assertEqual(response.errorCode, "Unknown.Region.RegionIDError")
            self.assertEqual(response.message, "Not found region by ID, check the ID and contact the admin")
            self.assertEqual(response.description, "没找到该资源池，请检查资源池ID是否正确，如资源池ID无误请联系管理员")
            self.assertIsNone(response.returnObj)

    def test_empty_zone_list(self):
        """测试空可用区列表的情况"""
        request = CtecsQueryZonesInRegionV41Request(regionID="empty_zone_region")

        # Mock空列表响应
        mock_response = {
            "message": "SUCCESS",
            "description": "成功",
            "errorCode": "",
            "returnObj": {
                "zoneList": []
            },
            "statusCode": 800
        }

        with patch.object(self.client, 'get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            api = self.apis.ctecsqueryzonesinregionv41api
            response = api.do(self.credential, self.client, self.endpoint, request)

            self.assertEqual(response.statusCode, 800)
            self.assertEqual(len(response.returnObj.zoneList), 0)

    def test_request_validation(self):
        """测试请求参数验证"""
        with self.assertRaises(TypeError):
            # 缺少必填参数regionID
            CtecsQueryZonesInRegionV41Request()

        # 测试有效的请求参数
        valid_request = CtecsQueryZonesInRegionV41Request(regionID="valid_region_id")
        self.assertEqual(valid_request.regionID, "valid_region_id")

    def test_api_instance(self):
        """验证API实例是否正确初始化"""
        self.assertIsNotNone(self.apis)
        self.assertIsNotNone(self.apis.ctecsqueryzonesinregionv41api)

        # 验证API方法是否可用
        api = self.apis.ctecsqueryzonesinregionv41api
        self.assertTrue(callable(api.do))
        self.assertTrue(hasattr(api, 'set_endpoint'))


if __name__ == '__main__':
    unittest.main()
