import unittest
from unittest.mock import patch
from core.client import CtyunClient
from core.credential import Credential
from core.exception import CtyunRequestException
from apis.ctecs_query_order_uuid_v41_api import CtecsQueryOrderUuidV41Api, CtecsQueryOrderUuidV41Request, \
    CtecsQueryOrderUuidV41Response


class TestCtecsQueryOrderUuidV41Api(unittest.TestCase):
    def setUp(self):
        self.client = CtyunClient()
        self.credential = Credential('<YOUR_AK>', '<YOUR_SK>')
        self.endpoint = 'https://<YOUR_ENDPOINT>'
        self.api = CtecsQueryOrderUuidV41Api()
        self.api.set_endpoint(self.endpoint)

    def test_successful_request(self):
        """测试成功的API请求"""
        test_order_id = "ce57956bf6354827bc91ec7ade20cb11"
        request = CtecsQueryOrderUuidV41Request(masterOrderId=test_order_id)

        # Mock成功响应
        mock_response = {
            "returnObj": {
                "resourceType": "VM",
                "resourceUUID": ["e265ca8e-1ec1-593b-f629-e26af4c90850"],
                "orderStatus": "3"
            },
            "errorCode": "",
            "message": "",
            "description": "",
            "statusCode": 800
        }

        with patch.object(self.client, 'get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            response = self.api.do(self.credential, self.client, self.endpoint, request)

            # 验证基本响应
            self.assertEqual(response.statusCode, 800)
            self.assertIsNotNone(response.returnObj)
            self.assertEqual(response.returnObj.orderStatus, "3")
            self.assertEqual(response.returnObj.resourceType, "VM")
            self.assertEqual(len(response.returnObj.resourceUUID), 1)

    def test_empty_resource_uuid_request(self):
        """测试返回资源UUID为空的情况
        resourceType在 VM、EBS、NETWORK 之外的值不会返回resourceUUID
        """
        test_order_id = "test_nat_order_id"
        request = CtecsQueryOrderUuidV41Request(masterOrderId=test_order_id)

        # Mock成功响应
        mock_response = {
            "returnObj": {
                "resourceType": "GATEWAY",
                "resourceUUID": [],
                "orderStatus": "3"
            },
            "errorCode": "",
            "message": "",
            "description": "",
            "statusCode": 800
        }

        with patch.object(self.client, 'get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            response = self.api.do(self.credential, self.client, self.endpoint, request)

            # 验证基本响应
            self.assertEqual(response.statusCode, 800)
            self.assertEqual(response.returnObj.orderStatus, "3")
            self.assertEqual(response.returnObj.resourceUUID, [])

    def test_failed_request(self):
        """测试失败的API请求"""
        request = CtecsQueryOrderUuidV41Request(masterOrderId="invalid_order_id")

        # Mock失败响应
        mock_response = {
            "description": "没找到对应的订单信息，请检查订单ID是否正确",
            "errorCode": "Order.OrderCheck.NotFound",
            "error": "Order.OrderCheck.NotFound",
            "message": "No corresponding order information found. Please check if the order ID is correct",
            "statusCode": 900
        }

        with patch.object(self.client, 'get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            response = self.api.do(self.credential, self.client, self.endpoint, request)

            # 验证错误响应
            self.assertEqual(response.statusCode, 900)
            self.assertEqual(response.errorCode, "Order.OrderCheck.NotFound")
            self.assertIsNone(response.returnObj)

    def test_request_validation(self):
        """测试请求参数验证"""
        with self.assertRaises(TypeError):
            # 缺少必填参数masterOrderId
            CtecsQueryOrderUuidV41Request()

        # 测试有效的请求参数
        valid_request = CtecsQueryOrderUuidV41Request(
            masterOrderId="valid_order_id"
        )
        self.assertEqual(valid_request.masterOrderId, "valid_order_id")

    def test_empty_response_handling(self):
        """测试空响应处理"""
        with self.assertRaises(ValueError):
            CtecsQueryOrderUuidV41Response.from_json({})

    def test_api_endpoint_setting(self):
        """测试API端点设置"""
        with self.assertRaises(ValueError):
            self.api.set_endpoint("invalid_endpoint")

    def test_api_request_exception(self):
        """测试API请求异常"""
        request = CtecsQueryOrderUuidV41Request(
            masterOrderId="test_order_id"
        )

        with patch.object(self.client, 'get') as mock_get:
            mock_get.side_effect = Exception("Test error")
            with self.assertRaises(CtyunRequestException):
                self.api.do(self.credential, self.client, self.endpoint, request)


if __name__ == '__main__':
    unittest.main()
