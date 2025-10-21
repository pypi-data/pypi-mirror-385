import unittest
from unittest.mock import patch
from core.client import CtyunClient
from core.credential import Credential
from core.exception import CtyunRequestException
from apis.ctecs_query_job_info_v41_api import CtecsQueryJobInfoV41Api, CtecsQueryJobInfoV41Request, \
    CtecsQueryJobInfoV41Response


class TestCtecsQueryJobInfoV41Api(unittest.TestCase):
    def setUp(self):
        self.client = CtyunClient()
        self.credential = Credential('<YOUR_AK>', '<YOUR_SK>')
        self.endpoint = 'https://<YOUR_ENDPOINT>'
        self.api = CtecsQueryJobInfoV41Api()
        self.api.set_endpoint(self.endpoint)

    def test_successful_request(self):
        """测试成功的API请求"""
        test_region_id = "81f7728662dd11ec810800155d307d5b"
        test_job_id = "success_job_id"
        request = CtecsQueryJobInfoV41Request(
            regionID=test_region_id,
            jobID=test_job_id
        )

        # Mock成功响应
        mock_response = {
            "returnObj": {
                "status": 1,
                "resourceId": "test_resource_id",
                "jobStatus": "success",
                "jobID": "success_job_id",
                "fields": {
                    "jaegerHeaders": None,
                    "traceid": "test_trace_id",
                    "isMaz": "1",
                    "azId": None,
                    "resourceId": "",
                    "azName": "az1",
                    "taskName": "ecs_task.tasks.volume_task.os_volume_snapshot_rollback_task",
                    "projectIdEcs": None,
                }
            },
            "errorCode": "",
            "message": "SUCCESS",
            "description": "成功",
            "statusCode": 800
        }

        with patch.object(self.client, 'get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            response = self.api.do(self.credential, self.client, self.endpoint, request)

            # 验证基本响应
            self.assertEqual(response.statusCode, 800)
            self.assertEqual(response.errorCode, "")
            self.assertIsNotNone(response.returnObj)

            # 验证返回对象字段
            return_obj = response.returnObj
            self.assertEqual(return_obj.jobID, test_job_id)
            self.assertEqual(return_obj.status, 1)
            self.assertEqual(return_obj.jobStatus, "success")
            self.assertEqual(return_obj.resourceId, "test_resource_id")
            self.assertEqual(return_obj.fields.taskName, "ecs_task.tasks.volume_task.os_volume_snapshot_rollback_task")

    def test_failed_request(self):
        """测试失败的API请求"""
        request = CtecsQueryJobInfoV41Request(
            regionID="invalid_region_id",
            jobID="invalid_job_id"
        )

        # Mock失败响应
        mock_response = {
            "statusCode": 900,
            "errorCode": "Unknown.Job.JobIDError",
            "message": "Job not found",
            "description": "任务不存在",
            "returnObj": None,
            "error": "Unknown.Job.JobIDError"
        }

        with patch.object(self.client, 'get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            response = self.api.do(self.credential, self.client, self.endpoint, request)

            # 验证错误响应
            self.assertEqual(response.statusCode, 900)
            self.assertEqual(response.errorCode, "Unknown.Job.JobIDError")
            self.assertEqual(response.message, "Job not found")
            self.assertEqual(response.description, "任务不存在")
            self.assertEqual(response.error, "Unknown.Job.JobIDError")
            self.assertIsNone(response.returnObj)

    def test_request_validation(self):
        """测试请求参数验证"""
        with self.assertRaises(TypeError):
            # 缺少必填参数regionID和jobID
            CtecsQueryJobInfoV41Request()

        # 测试有效的请求参数
        valid_request = CtecsQueryJobInfoV41Request(
            regionID="valid_region_id",
            jobID="valid_job_id"
        )
        self.assertEqual(valid_request.regionID, "valid_region_id")
        self.assertEqual(valid_request.jobID, "valid_job_id")

    def test_response_parsing(self):
        """测试响应解析"""
        test_data = {
            "statusCode": 800,
            "returnObj": {
                "jobID": "test_job_id",
                "status": 0,
                "jobStatus": "executing",
                "resourceId": None,
                "fields": None
            }
        }

        response = CtecsQueryJobInfoV41Response.from_json(test_data)
        self.assertEqual(response.statusCode, 800)
        self.assertEqual(response.returnObj.jobID, "test_job_id")
        self.assertEqual(response.returnObj.status, 0)
        self.assertEqual(response.returnObj.jobStatus, "executing")
        self.assertIsNone(response.returnObj.resourceId)
        self.assertIsNone(response.returnObj.fields)

    def test_empty_response_handling(self):
        """测试空响应处理"""
        with self.assertRaises(ValueError):
            CtecsQueryJobInfoV41Response.from_json({})

    def test_api_endpoint_setting(self):
        """测试API端点设置"""
        with self.assertRaises(ValueError):
            self.api.set_endpoint("invalid_endpoint")

    def test_api_request_exception(self):
        """测试API请求异常"""
        request = CtecsQueryJobInfoV41Request(
            regionID="test_region_id",
            jobID="test_job_id"
        )

        with patch.object(self.client, 'get') as mock_get:
            mock_get.side_effect = Exception("Test error")
            with self.assertRaises(CtyunRequestException):
                self.api.do(self.credential, self.client, self.endpoint, request)


if __name__ == '__main__':
    unittest.main()
