import unittest
from unittest.mock import patch

from apis.apis import Apis
from core.client import CtyunClient
from core.credential import Credential
from core.exception import CtyunRequestException
from apis.ctecs_query_new_order_price_v41_api import CtecsQueryNewOrderPriceV41Request, \
    CtecsQueryNewOrderPriceV41DisksRequest


class TestCtecsQueryNewOrderPriceV41Api(unittest.TestCase):
    def setUp(self):
        self.client = CtyunClient()
        self.credential = Credential('<YOUR_AK>', '<YOUR_SK>')
        self.endpoint = 'https://<YOUR_ENDPOINT>'
        self.apis = Apis(self.endpoint, self.client)

    def test_successful_vm_order_query(self):
        """测试成功的云主机订单询价"""
        request = CtecsQueryNewOrderPriceV41Request(
            regionID='81f7728662dd11ec810800155d307d5b',
            azName='az1',
            resourceType='VM',
            count=1,
            onDemand=False,
            cycleType='MONTH',
            cycleCount=6,
            flavorName='s8r.large.2',
            imageUUID='82437c41-9af7-44b9-9cf7-f9df929f8474',
            sysDiskType='SATA',
            sysDiskSize=40,
            disks=[
                CtecsQueryNewOrderPriceV41DisksRequest(
                    diskType='SATA',
                    diskSize=40
                ),
                CtecsQueryNewOrderPriceV41DisksRequest(
                    diskType='SAS',
                    diskSize=40
                ),
            ],
        )

        # Mock成功响应
        mock_response = {
            "message": "SUCCESS",
            "description": "成功",
            "errorCode": "",
            "returnObj": {
                "totalPrice": 1200.06,
                "isSucceed": True,
                "finalPrice": 1200.06,
                "subOrderPrices": [
                    {
                        "serviceTag": "OVMS",
                        "totalPrice": 1200.06,
                        "finalPrice": 1200.06,
                        "cycleCount": 6,
                        "orderItemPrices": [
                            {
                                "resourceType": "VM",
                                "totalPrice": 960.06,
                                "finalPrice": 960.06,
                                "instanceCnt": "1.0",
                                "itemId": "23d8ca0cc7da42639d12cd718e70c9c7",
                                "ctyunName": "弹性云主机ECS"
                            },
                            {
                                "resourceType": "EBS",
                                "totalPrice": 72.0,
                                "finalPrice": 72.0,
                                "instanceCnt": "40.0",
                                "itemId": "956a23cd50214c4b8ddd507dbc6be5ae",
                                "ctyunName": "云硬盘"
                            },
                            {
                                "resourceType": "EBS",
                                "totalPrice": 72.0,
                                "finalPrice": 72.0,
                                "instanceCnt": "40.0",
                                "itemId": "956a23cd50214c4b8ddd507dbc6be5ae",
                                "ctyunName": "云硬盘"
                            },
                            {
                                "resourceType": "EBS",
                                "totalPrice": 96.0,
                                "finalPrice": 96.0,
                                "instanceCnt": "40.0",
                                "itemId": "3adfe1ad25ed45c0ab0ceec31f284ced",
                                "ctyunName": "云硬盘"
                            }
                        ]
                    }
                ]
            },
            "statusCode": 800
        }

        with patch.object(self.client, 'post') as mock_post:
            mock_post.return_value.json.return_value = mock_response
            api = self.apis.ctecsqueryneworderpricev41api
            response = api.do(self.credential, self.client, self.endpoint, request)

            # 验证基本响应
            self.assertEqual(response.statusCode, 800)
            self.assertIsNotNone(response.returnObj)

            # 验证返回对象字段
            return_obj = response.returnObj
            self.assertEqual(return_obj.totalPrice, 1200.06)
            self.assertIsNone(return_obj.discountPrice)
            self.assertEqual(return_obj.finalPrice, 1200.06)
            self.assertEqual(len(return_obj.subOrderPrices), 1)
            self.assertEqual(return_obj.subOrderPrices[0].serviceTag, 'OVMS')
            self.assertEqual(return_obj.subOrderPrices[0].totalPrice, 1200.06)
            self.assertEqual(return_obj.subOrderPrices[0].finalPrice, 1200.06)
            self.assertEqual(len(return_obj.subOrderPrices[0].orderItemPrices), 4)
            self.assertEqual(return_obj.subOrderPrices[0].orderItemPrices[0].resourceType, 'VM')
            self.assertEqual(return_obj.subOrderPrices[0].orderItemPrices[0].totalPrice, 960.06)
            self.assertEqual(return_obj.subOrderPrices[0].orderItemPrices[0].finalPrice, 960.06)
            self.assertEqual(return_obj.subOrderPrices[0].orderItemPrices[1].resourceType, 'EBS')
            self.assertEqual(return_obj.subOrderPrices[0].orderItemPrices[1].totalPrice, 72.0)
            self.assertEqual(return_obj.subOrderPrices[0].orderItemPrices[1].finalPrice, 72.0)

    def test_failed_request(self):
        """测试失败的API请求"""
        request = CtecsQueryNewOrderPriceV41Request(
            regionID='invalid_region_id',
            resourceType='VM',
            count=1,
            onDemand=False,
            cycleType='MONTH',
            cycleCount=6,
            flavorName='s2.small.1',
            imageUUID='7d2922f3-019e-4dbb-ad84-cc8c3497546c',
            sysDiskType='SATA',
            sysDiskSize=50
        )

        # Mock失败响应
        mock_response = {
            "message": "region info empty",
            "description": "资源池信息为空",
            "error": "Unknown.RegionInfo.Empty",
            "errorCode": "Unknown.RegionInfo.Empty",
            "returnObj": None,
            "statusCode": 900
        }

        with patch.object(self.client, 'post') as mock_post:
            mock_post.return_value.json.return_value = mock_response
            api = self.apis.ctecsqueryneworderpricev41api
            response = api.do(self.credential, self.client, self.endpoint, request)

            # 验证错误响应
            self.assertEqual(response.statusCode, 900)
            self.assertEqual(response.errorCode, 'Unknown.RegionInfo.Empty')
            self.assertEqual(response.message, 'region info empty')
            self.assertEqual(response.description, '资源池信息为空')
            self.assertEqual(response.error, 'Unknown.RegionInfo.Empty')
            self.assertIsNone(response.returnObj)

    def test_request_validation(self):
        """测试请求参数验证"""
        with self.assertRaises(TypeError):
            # 缺少必填参数
            CtecsQueryNewOrderPriceV41Request()

        with self.assertRaises(CtyunRequestException):
            # 关联参数校验
            request = CtecsQueryNewOrderPriceV41Request(
                regionID='41f64827f25f468595ffa3a5deb5d15d',
                resourceType='VM',
                count=1,
                onDemand=False
            )
            request.to_dict()

        # 参数转换校验，request -> dict
        request = CtecsQueryNewOrderPriceV41Request(
            regionID='81f7728662dd11ec810800155d307d5b',
            azName='az1',
            resourceType='VM',
            count=1,
            onDemand=False,
            cycleType='MONTH',
            cycleCount=6,
            flavorName='s8r.large.2',
            imageUUID='82437c41-9af7-44b9-9cf7-f9df929f8474',
            sysDiskType='SATA',
            sysDiskSize=40,
            disks=[
                CtecsQueryNewOrderPriceV41DisksRequest(
                    diskType='SATA',
                    diskSize=40
                ),
                CtecsQueryNewOrderPriceV41DisksRequest(
                    diskType='SAS',
                    diskSize=40
                ),
            ],
        )
        request_dict = request.to_dict()
        expected_body = {
            "regionID": "81f7728662dd11ec810800155d307d5b",
            "azName": "az1",
            "resourceType": "VM",
            "count": 1,
            "onDemand": False,
            "cycleType": "MONTH",
            "cycleCount": 6,
            "flavorName": "s8r.large.2",
            "imageUUID": "82437c41-9af7-44b9-9cf7-f9df929f8474",
            "sysDiskType": "SATA",
            "sysDiskSize": 40,
            "disks": [
                {
                    "diskType": "SATA",
                    "diskSize": 40
                },
                {
                    "diskType": "SAS",
                    "diskSize": 40
                }
            ]
        }
        self.assertEqual(request_dict, expected_body)

    def test_successful_ebs_order_query(self):
        """测试云硬盘订单询价"""
        request = CtecsQueryNewOrderPriceV41Request(
            regionID='81f7728662dd11ec810800155d307d5b',
            azName='az1',
            resourceType='EBS',
            count=1,
            onDemand=False,
            cycleType='MONTH',
            cycleCount=6,
            diskType='SATA',
            diskSize=40,
            diskMode='VBD'
        )
        # Mock成功响应
        mock_response = {
            "message": "SUCCESS",
            "description": "成功",
            "errorCode": "",
            "returnObj": {
                "totalPrice": 72.0,
                "isSucceed": True,
                "finalPrice": 72.0,
                "subOrderPrices": [
                    {
                        "serviceTag": "OVMS",
                        "totalPrice": 72.0,
                        "finalPrice": 72.0,
                        "cycleCount": 6,
                        "orderItemPrices": [
                            {
                                "resourceType": "EBS",
                                "totalPrice": 72.0,
                                "finalPrice": 72.0,
                                "instanceCnt": "40.0",
                                "itemId": "956a23cd50214c4b8ddd507dbc6be5ae",
                                "ctyunName": "云硬盘"
                            }
                        ]
                    }
                ]
            },
            "statusCode": 800
        }

        with patch.object(self.client, 'post') as mock_post:
            mock_post.return_value.json.return_value = mock_response
            api = self.apis.ctecsqueryneworderpricev41api
            response = api.do(self.credential, self.client, self.endpoint, request)

            # 验证基本响应
            self.assertEqual(response.statusCode, 800)
            self.assertIsNotNone(response.returnObj)
            self.assertEqual(response.returnObj.totalPrice, 72.0)
            self.assertEqual(response.returnObj.finalPrice, 72.0)
            self.assertEqual(len(response.returnObj.subOrderPrices), 1)
            self.assertEqual(response.returnObj.subOrderPrices[0].serviceTag, 'OVMS')
            self.assertEqual(response.returnObj.subOrderPrices[0].totalPrice, 72.0)
            self.assertEqual(response.returnObj.subOrderPrices[0].finalPrice, 72.0)
            self.assertEqual(len(response.returnObj.subOrderPrices[0].orderItemPrices), 1)
            self.assertEqual(response.returnObj.subOrderPrices[0].orderItemPrices[0].resourceType, 'EBS')
            self.assertEqual(response.returnObj.subOrderPrices[0].orderItemPrices[0].totalPrice, 72.0)
            self.assertEqual(response.returnObj.subOrderPrices[0].orderItemPrices[0].finalPrice, 72.0)


if __name__ == '__main__':
    unittest.main()
