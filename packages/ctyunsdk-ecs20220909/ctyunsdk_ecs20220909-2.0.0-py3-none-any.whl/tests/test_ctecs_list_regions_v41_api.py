import unittest
from unittest.mock import patch, MagicMock
from core.client import CtyunClient
from core.credential import Credential
from apis.apis import Apis
from apis.ctecs_list_regions_v41_api import CtecsListRegionsV41Request


class TestCtecsListRegionsV41Api(unittest.TestCase):
    def setUp(self):
        self.client = CtyunClient()
        self.credential = Credential('<YOUR_AK>', '<YOUR_SK>')
        self.endpoint = 'https://<YOUR_ENDPOINT>'
        self.apis = Apis(self.endpoint, self.client)

    def test_ctecsListRegionsV41Api(self):
        # Construct request
        request = CtecsListRegionsV41Request(regionName='内蒙')

        # Mock response data
        mock_response = {
            'returnObj': {
                'regionList': [
                    {
                        'isMultiZones': False,
                        'regionCode': 'cn-neimeng-1',
                        'zoneList': [],
                        'openapiAvailable': True,
                        'regionParent': '内蒙',
                        'regionID': '41f64827f25f468595ffa3a5deb5d15d',
                        'regionType': 'openstack',
                        'regionName': '内蒙1'
                    },
                    {
                        'isMultiZones': True,
                        'regionCode': 'cn-neimeng-8',
                        'zoneList': ['az1', 'az2', 'az3'],
                        'openapiAvailable': True,
                        'regionParent': '内蒙',
                        'regionID': '81f7728662dd11ec810800155d307d5b',
                        'regionType': 'openstack',
                        'regionName': '内蒙8'
                    }
                ]
            },
            'errorCode': '',
            'message': '',
            'description': '',
            'statusCode': 800
        }

        with patch('core.client.CtyunClient.get') as mock_get:
            # Configure the mock to return a response with status code 200 and mock data
            mock_get.return_value = MagicMock(
                status_code=200,
                json=MagicMock(return_value=mock_response)
            )
            api = self.apis.ctecslistregionsv41api
            response = api.do(self.credential, self.client, self.endpoint, request)
            self.assertEqual(response.statusCode, 800)
            self.assertEqual(len(response.returnObj.regionList), 2)
            self.assertEqual(response.returnObj.regionList[0].regionName, '内蒙1')

    def test_empty_region_list(self):
        """测试资源池为空的情况"""
        request = CtecsListRegionsV41Request(regionName='test_empty')
        mock_response = {
            'message': 'SUCCESS',
            'description': '成功',
            'errorCode': '',
            'returnObj': {
                'regionList': []
            },
            'statusCode': 800
        }
        with patch('core.client.CtyunClient.get') as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=MagicMock(return_value=mock_response)
            )
            api = self.apis.ctecslistregionsv41api
            response = api.do(self.credential, self.client, self.endpoint, request)
            self.assertEqual(response.statusCode, 800)
            self.assertEqual(len(response.returnObj.regionList), 0)

    def test_api_instance(self):
        self.assertIsNotNone(self.apis)
        self.assertIsNotNone(self.apis.ctecslistregionsv41api)


if __name__ == '__main__':
    unittest.main()
