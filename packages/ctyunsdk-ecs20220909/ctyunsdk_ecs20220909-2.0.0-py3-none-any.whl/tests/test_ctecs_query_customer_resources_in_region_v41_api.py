import unittest
from unittest.mock import patch

from core.client import CtyunClient
from core.credential import Credential
from core.exception import CtyunRequestException
from apis.ctecs_query_customer_resources_in_region_v41_api import CtecsQueryCustomerResourcesInRegionV41Api, \
    CtecsQueryCustomerResourcesInRegionV41Request, CtecsQueryCustomerResourcesInRegionV41Response


class TestCtecsQueryCustomerResourcesInRegionV41Api(unittest.TestCase):
    def setUp(self):
        self.client = CtyunClient()
        self.credential = Credential('<YOUR_AK>', '<YOUR_SK>')
        self.endpoint = 'https://<YOUR_ENDPOINT>'
        self.api = CtecsQueryCustomerResourcesInRegionV41Api()
        self.api.set_endpoint(self.endpoint)

    def test_successful_request(self):
        test_region_id = "test_region_id"
        request = CtecsQueryCustomerResourcesInRegionV41Request(
            regionID=test_region_id,
        )

        mock_response = {
            "message": "SUCCESS",
            "description": "成功",
            "errorCode": "",
            "returnObj": {
                "resources": {
                    "ACLLIST": {
                        "detail": {
                            "bb9fdb42056f11eda1610242ac110002": 0
                        },
                        "total_count": 0
                    },
                    "BMS": {
                        "bm_running_count": 0,
                        "bm_shutd_count": 0,
                        "cpu_count": 0,
                        "detail_total_count": 0,
                        "expire_count": 0,
                        "expire_running_count": 0,
                        "expire_shutd_count": 0,
                        "memory_count": 0,
                        "total_count": 0
                    },
                    "CBR": {
                        "detail": {
                            "bb9fdb42056f11eda1610242ac110002": 0
                        },
                        "detail_total_count": 0,
                        "total_count": 0,
                        "total_size": 0
                    },
                    "CBR_VBS": {
                        "detail": {
                            "bb9fdb42056f11eda1610242ac110002": 0
                        },
                        "detail_total_count": 0,
                        "total_count": 0
                    },
                    "CERT": {
                        "detail": {
                            "bb9fdb42056f11eda1610242ac110002": 0
                        },
                        "total_count": 0
                    },
                    "Disk_Backup": {
                        "detail": {
                            "bb9fdb42056f11eda1610242ac110002": 0
                        },
                        "detail_total_count": 0,
                        "total_count": 0
                    },
                    "IMAGE": {
                        "detail": {
                            "bb9fdb42056f11eda1610242ac110002": 0
                        },
                        "total_count": 0
                    },
                    "IP_POOL": {
                        "detail": {
                            "bb9fdb42056f11eda1610242ac110002": 0
                        },
                        "outer_pool_count": 0,
                        "total_count": 0
                    },
                    "IPv6_GW": {
                        "total_count": 0
                    },
                    "IPv6_POOL": {
                        "total_count": 0
                    },
                    "LB_LISTENER": {
                        "detail": {
                            "bb9fdb42056f11eda1610242ac110002": 1
                        },
                        "total_count": 1
                    },
                    "LOADBALANCER": {
                        "detail": {
                            "bb9fdb42056f11eda1610242ac110002": 0
                        },
                        "total_count": 0
                    },
                    "NAT": {
                        "detail": {
                            "bb9fdb42056f11eda1610242ac110002": 0
                        },
                        "detail_total_count": 0,
                        "total_count": 0
                    },
                    "OS_Backup": {
                        "detail_total_count": 0,
                        "total_size": 0
                    },
                    "Public_IP": {
                        "detail_total_count": 3,
                        "hold_expense_count": 1,
                        "outer_ip_count": 0,
                        "total_count": 3
                    },
                    "SNAPSHOT": {
                        "detail": {
                            "bb9fdb42056f11eda1610242ac110002": 0
                        },
                        "total_count": 0
                    },
                    "SNAPSHOT_POLICY": {
                        "total_count": 0
                    },
                    "TrafficMirror_Filter": {
                        "detail": {
                            "bb9fdb42056f11eda1610242ac110002": 0
                        },
                        "total_count": 0
                    },
                    "TrafficMirror_Flow": {
                        "detail": {
                            "bb9fdb42056f11eda1610242ac110002": 0
                        },
                        "total_count": 0
                    },
                    "VIRTUALIP": {
                        "total_count": 0
                    },
                    "VM": {
                        "cpu_count": 4,
                        "detail_total_count": 2,
                        "expire_count": 0,
                        "expire_running_count": 0,
                        "expire_shutd_count": 0,
                        "memory_count": 8,
                        "total_count": 2,
                        "vm_running_count": 2,
                        "vm_shutd_count": 0
                    },
                    "VOLUME_SNAPSHOT": {
                        "detail_total_count": 0,
                        "total_count": 0
                    },
                    "VPC": {
                        "detail_total_count": 3,
                        "total_count": 3
                    },
                    "VPC_ACCESSLOG": {
                        "total_count": 0
                    },
                    "Vm_Group": {
                        "detail": {
                            "bb9fdb42056f11eda1610242ac110002": 0
                        },
                        "total_count": 0
                    },
                    "Volume": {
                        "detail_total_count": 4,
                        "total_count": 4,
                        "total_size": 280,
                        "vo_disk_count": 2,
                        "vo_disk_size": 80,
                        "vo_root_count": 2,
                        "vo_root_size": 200
                    },
                    "az_display_name": "",
                    "prefixList": {
                        "detail": {
                            "bb9fdb42056f11eda1610242ac110002": 0
                        },
                        "total_count": 0
                    }
                }
            },
            "statusCode": 800
        }
        with patch.object(self.client, 'get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            response = self.api.do(self.credential, self.client, self.endpoint, request)

            # 验证响应结构
            self.assertEqual(response.statusCode, 800)
            self.assertEqual(response.message, "SUCCESS")
            self.assertEqual(response.description, "成功")
            self.assertEqual(response.errorCode, "")
            self.assertIsNotNone(response.returnObj)

            # 验证资源信息
            resources = response.returnObj.resources
            self.assertIsNotNone(resources)

            # 验证VM资源
            self.assertEqual(resources.VM.total_count, 2)
            self.assertEqual(resources.VM.cpu_count, 4)
            self.assertEqual(resources.VM.memory_count, 8)
            self.assertEqual(resources.VM.vm_running_count, 2)
            self.assertEqual(resources.VM.expire_running_count, 0)

            # 验证Volume资源
            self.assertEqual(resources.Volume.total_count, 4)
            self.assertEqual(resources.Volume.total_size, 280)
            self.assertEqual(resources.Volume.detail_total_count, 4)
            self.assertEqual(resources.Volume.vo_disk_count, 2)
            self.assertEqual(resources.Volume.vo_disk_size, 80)
            self.assertEqual(resources.Volume.vo_root_count, 2)
            self.assertEqual(resources.Volume.vo_root_size, 200)

            # 验证VPC资源
            self.assertEqual(resources.VPC.total_count, 3)
            self.assertEqual(resources.VPC.detail_total_count, 3)

            # 验证Public_IP资源
            self.assertEqual(resources.Public_IP.total_count, 3)
            self.assertEqual(resources.Public_IP.detail_total_count, 3)

            self.assertEqual(resources.VOLUME_SNAPSHOT.total_count, 0)
            self.assertEqual(resources.VOLUME_SNAPSHOT.detail_total_count, 0)

            self.assertEqual(resources.BMS.total_count, 0)
            self.assertEqual(resources.BMS.detail_total_count, 0)
            self.assertEqual(resources.BMS.memory_count, 0)
            self.assertEqual(resources.BMS.cpu_count, 0)

            self.assertEqual(resources.NAT.total_count, 0)
            self.assertEqual(resources.NAT.detail_total_count, 0)
            self.assertEqual(resources.NAT.detail["bb9fdb42056f11eda1610242ac110002"], 0)

            self.assertEqual(resources.Disk_Backup.total_count, 0)
            self.assertEqual(resources.Disk_Backup.detail_total_count, 0)
            self.assertEqual(resources.Disk_Backup.detail["bb9fdb42056f11eda1610242ac110002"], 0)

            self.assertEqual(resources.CBR_VBS.total_count, 0)
            self.assertEqual(resources.CBR_VBS.detail_total_count, 0)
            self.assertEqual(resources.CBR_VBS.detail["bb9fdb42056f11eda1610242ac110002"], 0)

            self.assertEqual(resources.CBR.total_count, 0)
            self.assertEqual(resources.CBR.total_size, 0)
            self.assertEqual(resources.CBR.detail_total_count, 0)
            self.assertEqual(resources.CBR.detail["bb9fdb42056f11eda1610242ac110002"], 0)
            
            self.assertEqual(resources.OS_Backup.total_size, 0)
            self.assertEqual(resources.OS_Backup.detail_total_count, 0)

            self.assertEqual(resources.CERT.total_count, 0)
            self.assertEqual(resources.CERT.detail["bb9fdb42056f11eda1610242ac110002"], 0)

            self.assertEqual(resources.LOADBALANCER.total_count, 0)
            self.assertEqual(resources.LOADBALANCER.detail["bb9fdb42056f11eda1610242ac110002"], 0)

            self.assertEqual(resources.LB_LISTENER.total_count, 1)
            self.assertEqual(resources.LB_LISTENER.detail["bb9fdb42056f11eda1610242ac110002"], 1)

            self.assertEqual(resources.IP_POOL.total_count, 0)
            self.assertEqual(resources.IP_POOL.detail["bb9fdb42056f11eda1610242ac110002"], 0)

            self.assertEqual(resources.IMAGE.total_count, 0)
            self.assertEqual(resources.IMAGE.detail["bb9fdb42056f11eda1610242ac110002"], 0)

            self.assertEqual(resources.ACLLIST.total_count, 0)
            self.assertEqual(resources.ACLLIST.detail["bb9fdb42056f11eda1610242ac110002"], 0)

            self.assertEqual(resources.SNAPSHOT.total_count, 0)
            self.assertEqual(resources.SNAPSHOT.detail["bb9fdb42056f11eda1610242ac110002"], 0)

            self.assertEqual(resources.Vm_Group.total_count, 0)
            self.assertEqual(resources.Vm_Group.detail["bb9fdb42056f11eda1610242ac110002"], 0)

            self.assertEqual(resources.TrafficMirror_Flow.total_count, 0)
            self.assertEqual(resources.TrafficMirror_Flow.detail["bb9fdb42056f11eda1610242ac110002"], 0)

            self.assertEqual(resources.TrafficMirror_Filter.total_count, 0)
            self.assertEqual(resources.TrafficMirror_Filter.detail["bb9fdb42056f11eda1610242ac110002"], 0)

    def test_failed_request(self):
        """测试失败的API请求"""
        request = CtecsQueryCustomerResourcesInRegionV41Request(
            regionID="invalid_region",
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

        with patch.object(self.client, 'get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            response = self.api.do(self.credential, self.client, self.endpoint, request)

            # 验证错误响应
            self.assertEqual(response.statusCode, 900)
            self.assertEqual(response.errorCode, "Unknown.RegionInfo.Empty")
            self.assertEqual(response.message, "region info empty")
            self.assertEqual(response.description, "资源池信息为空")
            self.assertIsNone(response.returnObj)

    def test_ctecsQueryCustomerResourcesInRegionV41Api(self):
        # Construct request
        request = CtecsQueryCustomerResourcesInRegionV41Request(regionID="81f7728662dd11ec810800155d307d5b")

        try:
            api = CtecsQueryCustomerResourcesInRegionV41Api()
            api.set_endpoint(self.endpoint)
            response = api.do(self.credential, self.client, self.endpoint, request)
            self.assertIsNotNone(response)  # 验证响应不为空
            print(f'Response: {response}')  # 打印响应内容
        except CtyunRequestException as e:
            pass

    def test_empty_response_handling(self):
        """测试空响应处理"""
        with self.assertRaises(ValueError):
            CtecsQueryCustomerResourcesInRegionV41Response.from_json({})

    def test_api_endpoint_setting(self):
        """测试API端点设置"""
        with self.assertRaises(ValueError):
            self.api.set_endpoint("invalid_endpoint")

    def test_api_request_exception(self):
        """测试API请求异常"""
        request = CtecsQueryCustomerResourcesInRegionV41Request(
            regionID="test_region",
        )

        with patch.object(self.client, 'get') as mock_get:
            mock_get.side_effect = Exception("Test error")
            with self.assertRaises(CtyunRequestException):
                self.api.do(self.credential, self.client, self.endpoint, request)


if __name__ == '__main__':
    unittest.main()
