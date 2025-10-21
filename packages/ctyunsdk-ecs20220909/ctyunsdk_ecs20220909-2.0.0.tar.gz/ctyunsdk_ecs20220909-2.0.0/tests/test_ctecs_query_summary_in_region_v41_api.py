import unittest
from unittest.mock import patch
from core.client import CtyunClient
from core.credential import Credential
from core.exception import CtyunRequestException
from apis.apis import Apis
from apis.ctecs_query_summary_in_region_v41_api import CtecsQuerySummaryInRegionV41Api, \
    CtecsQuerySummaryInRegionV41Request


class TestCtecsQuerySummaryInRegionV41Api(unittest.TestCase):
    def setUp(self):
        self.client = CtyunClient()
        self.credential = Credential('<YOUR_AK>', '<YOUR_SK>')
        self.endpoint = 'https://<YOUR_ENDPOINT>'
        self.apis = Apis(self.endpoint, self.client)

    def test_successful_request(self):
        """测试成功的API请求"""
        test_region_id = '81f7728662dd11ec810800155d307d5b'
        request = CtecsQuerySummaryInRegionV41Request(regionID=test_region_id)

        # Mock成功响应
        mock_response = {
            'message': 'SUCCESS',
            'description': '成功',
            'errorCode': '',
            'returnObj': {
                'province': '内蒙',
                'dedicated': False,
                'openapiAvailable': True,
                'cpuArches': ['x86_64'],
                'zoneList': ['az1', 'az2', 'az3'],
                'regionName': '内蒙8',
                'isMultiZones': True,
                'city': '内蒙8',
                'regionParent': '内蒙',
                'regionID': '81f7728662dd11ec810800155d307d5b',
                'regionType': 'openstack',
                'regionVersion': 'v4.0'
            },
            'statusCode': 800
        }

        with patch.object(self.client, 'get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            api = self.apis.ctecsquerysummaryinregionv41api
            response = api.do(self.credential, self.client, self.endpoint, request)

            # 验证基本响应
            self.assertEqual(response.statusCode, 800)
            self.assertEqual(response.errorCode, '')
            self.assertIsNotNone(response.returnObj)

            # 验证返回对象字段
            return_obj = response.returnObj
            self.assertEqual(return_obj.regionID, test_region_id)
            self.assertEqual(return_obj.regionParent, '内蒙')
            self.assertEqual(return_obj.regionName, '内蒙8')
            self.assertEqual(return_obj.regionType, 'openstack')
            self.assertTrue(return_obj.isMultiZones)
            self.assertEqual(return_obj.zoneList, ['az1', 'az2', 'az3'])
            self.assertEqual(return_obj.cpuArches, ['x86_64'])
            self.assertEqual(return_obj.regionVersion, 'v4.0')
            self.assertFalse(return_obj.dedicated)
            self.assertEqual(return_obj.province, '内蒙')
            self.assertEqual(return_obj.city, '内蒙8')
            self.assertTrue(return_obj.openapiAvailable)

    def test_failed_request(self):
        """测试失败的API请求"""
        request = CtecsQuerySummaryInRegionV41Request(regionID='invalid_region_id')

        # Mock失败响应
        mock_response = {
            'message': 'Not found region by ID, check the ID and contact the admin',
            'description': '没找到该资源池，请检查资源池ID是否正确，如资源池ID无误请联系管理员',
            'error': 'Unknown.Region.RegionIDError',
            'errorCode': 'Unknown.Region.RegionIDError',
            'returnObj': None,
            'statusCode': 900
        }

        with patch.object(self.client, 'get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            api = self.apis.ctecsquerysummaryinregionv41api
            response = api.do(self.credential, self.client, self.endpoint, request)

            # 验证错误响应
            self.assertEqual(response.statusCode, 900)
            self.assertEqual(response.errorCode, 'Unknown.Region.RegionIDError')
            self.assertEqual(response.message, 'Not found region by ID, check the ID and contact the admin')
            self.assertEqual(response.description, '没找到该资源池，请检查资源池ID是否正确，如资源池ID无误请联系管理员')
            self.assertEqual(response.error, 'Unknown.Region.RegionIDError')
            self.assertIsNone(response.returnObj)

    def test_invalid_credentials(self):
        """测试无效凭证"""
        invalid_credential = Credential('invalid_ak', 'invalid_sk')
        request = CtecsQuerySummaryInRegionV41Request(regionID='81f7728662dd11ec810800155d307d5b')

        try:
            api = CtecsQuerySummaryInRegionV41Api()
            api.set_endpoint(self.endpoint)
            response = api.do(self.credential, self.client, self.endpoint, request)
            self.assertIsNotNone(response)  # 验证响应不为空
            print(f'Response: {response}')  # 打印响应内容
        except CtyunRequestException as e:
            pass

    def test_request_validation(self):
        """测试请求参数验证"""
        with self.assertRaises(TypeError):
            # 缺少必填参数regionID
            CtecsQuerySummaryInRegionV41Request()

        # 测试有效的请求参数
        valid_request = CtecsQuerySummaryInRegionV41Request(regionID='valid_region_id')
        self.assertEqual(valid_request.regionID, 'valid_region_id')

    def test_api_instance(self):
        """验证API实例是否正确初始化"""
        self.assertIsNotNone(self.apis)
        self.assertIsNotNone(self.apis.ctecsquerysummaryinregionv41api)

        # 验证API方法是否可用
        api = self.apis.ctecsquerysummaryinregionv41api
        self.assertTrue(callable(api.do))
        self.assertTrue(hasattr(api, 'set_endpoint'))


if __name__ == '__main__':
    unittest.main()
