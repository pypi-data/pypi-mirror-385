import unittest
from unittest.mock import patch

from core.client import CtyunClient
from core.credential import Credential
from apis.apis import Apis
from apis.ctecs_query_renew_order_price_v41_api import CtecsQueryRenewOrderPriceV41Request


class TestCtecsQueryRenewOrderPriceV41Api(unittest.TestCase):
    def setUp(self):
        self.client = CtyunClient()
        self.credential = Credential('<YOUR_AK>', '<YOUR_SK>')
        self.endpoint = 'https://<YOUR_ENDPOINT>'
        self.apis = Apis(self.endpoint, self.client)

    def test_successful_vm_order_query(self):
        """测试成功的云主机订单询价"""
        request = CtecsQueryRenewOrderPriceV41Request(
            regionID='81f7728662dd11ec810800155d307d5b',
            resourceType='VM',
            resourceUUID='e265ca8e-1ec1-593b-f629-e26af4c90850',
            cycleType='MONTH',
            cycleCount=6,
        )

        # Mock成功响应
        mock_response = {
            "message": "SUCCESS",
            "description": "成功",
            "errorCode": "",
            "returnObj": {
                "isSucceed": True,
                "totalPrice": 90.31,
                "finalPrice": 90.31,
                "discountPrice": 0,
                "subOrderPrices": [
                    {
                        "serviceTag": "OVMS",
                        "totalPrice": 90.31,
                        "finalPrice": 90.31,
                        "cycleCount": 1,
                        "cycleType": None,
                        "orderItemPrices": [
                            {
                                "itemId": "abe40873f20e11ecb13fa4ae12fe8028",
                                "resourceType": "VM",
                                "totalPrice": 78.31,
                                "finalPrice": 78.31,
                                "ctyunName": "弹性云主机ECS",
                                "instanceCnt": "1.0"
                            },
                            {
                                "itemId": "956a23cd50214c4b8ddd507dbc6be5ae",
                                "resourceType": "EBS",
                                "totalPrice": 12,
                                "finalPrice": 12,
                                "ctyunName": "云硬盘",
                                "instanceCnt": "40.0"
                            }
                        ]
                    }
                ]
            },
            "statusCode": 800
        }

        with patch.object(self.client, 'post') as mock_post:
            mock_post.return_value.json.return_value = mock_response
            api = self.apis.ctecsqueryreneworderpricev41api
            response = api.do(self.credential, self.client, self.endpoint, request)

            # 验证基本响应
            self.assertEqual(response.statusCode, 800)
            self.assertIsNotNone(response.returnObj)

            # 验证返回对象字段
            return_obj = response.returnObj
            self.assertEqual(return_obj.totalPrice, 90.31)
            self.assertEqual(return_obj.finalPrice, 90.31)
            self.assertEqual(len(return_obj.subOrderPrices), 1)
            self.assertEqual(return_obj.subOrderPrices[0].serviceTag, 'OVMS')
            self.assertEqual(return_obj.subOrderPrices[0].totalPrice, 90.31)
            self.assertEqual(return_obj.subOrderPrices[0].finalPrice, 90.31)
            self.assertEqual(len(return_obj.subOrderPrices[0].orderItemPrices), 2)
            self.assertEqual(return_obj.subOrderPrices[0].orderItemPrices[0].resourceType, 'VM')
            self.assertEqual(return_obj.subOrderPrices[0].orderItemPrices[0].totalPrice, 78.31)
            self.assertEqual(return_obj.subOrderPrices[0].orderItemPrices[0].finalPrice, 78.31)
            self.assertEqual(return_obj.subOrderPrices[0].orderItemPrices[1].resourceType, 'EBS')
            self.assertEqual(return_obj.subOrderPrices[0].orderItemPrices[1].totalPrice, 12)
            self.assertEqual(return_obj.subOrderPrices[0].orderItemPrices[1].finalPrice, 12)

    def test_failed_request(self):
        """测试失败的API请求"""
        request = CtecsQueryRenewOrderPriceV41Request(
            regionID='invalid_region_id',
            resourceType='VM',
            resourceUUID='',
            cycleType='MONTH',
            cycleCount=6,
        )

        # Mock失败响应
        mock_response = {
            "message":"request param error: resourceUUID is not empty",
            "description":"请求参数错误: 资源uuid resourceUUID不能为空",
            "error":"Unknown.Parameter.Invaliderror",
            "errorCode":"Unknown.Parameter.Invaliderror",
            "returnObj":None,
            "statusCode":900
        }

        with patch.object(self.client, 'post') as mock_post:
            mock_post.return_value.json.return_value = mock_response
            api = self.apis.ctecsqueryneworderpricev42api
            response = api.do(self.credential, self.client, self.endpoint, request)

            # 验证错误响应
            self.assertEqual(response.statusCode, 900)
            self.assertEqual(response.errorCode, 'Unknown.Parameter.Invaliderror')
            self.assertEqual(response.message, 'request param error: resourceUUID is not empty')
            self.assertEqual(response.description, '请求参数错误: 资源uuid resourceUUID不能为空')
            self.assertEqual(response.error, 'Unknown.Parameter.Invaliderror')
            self.assertIsNone(response.returnObj)

    def test_request_validation(self):
        """测试请求参数验证"""
        with self.assertRaises(TypeError):
            # 缺少必填参数
            CtecsQueryRenewOrderPriceV41Request()

    def test_api_instance(self):
        # 验证API实例是否正确初始化
        self.assertIsNotNone(self.apis)
        self.assertIsNotNone(self.apis.ctecsqueryreneworderpricev41api)


if __name__ == '__main__':
    unittest.main()
