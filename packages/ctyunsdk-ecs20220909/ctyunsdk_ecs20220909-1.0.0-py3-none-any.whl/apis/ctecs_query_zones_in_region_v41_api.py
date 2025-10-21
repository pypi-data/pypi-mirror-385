from typing import List, Optional
from core.client import CtyunClient
from core.credential import Credential
from core.exception import CtyunRequestException
from dataclasses import dataclass

@dataclass
class CtecsQueryZonesInRegionV41Request:
    """请求参数类"""
    regionID: str  # 资源池ID(必填)

    def to_dict(self) -> dict:
        """转换为请求参数字典，过滤None值"""
        return {k: v for k, v in vars(self).items() if v is not None}

@dataclass
class CtecsQueryZonesInRegionV41ReturnObjZoneListResponse:
    """可用区信息"""
    name: str  # 可用区名称
    azDisplayName: str  # 可用区展示名

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsQueryZonesInRegionV41ReturnObjZoneListResponse':
        """从JSON数据创建返回对象"""
        if not json_data:
            raise ValueError("JSON data cannot be empty")
        return cls(
            name=json_data.get('name', ''),
            azDisplayName=json_data.get('azDisplayName', '')
        )

@dataclass
class CtecsQueryZonesInRegionV41ReturnObjResponse:
    """返回参数对象"""
    zoneList: List[CtecsQueryZonesInRegionV41ReturnObjZoneListResponse]  # 可用区列表

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsQueryZonesInRegionV41ReturnObjResponse':
        """从JSON数据创建返回对象"""
        if not json_data:
            return cls(zoneList=[])

        zone_list = []
        if 'zoneList' in json_data and json_data['zoneList'] is not None:
            zone_list = [CtecsQueryZonesInRegionV41ReturnObjZoneListResponse.from_json(zone)
                        for zone in json_data['zoneList']]

        return cls(zoneList=zone_list)

@dataclass
class CtecsQueryZonesInRegionV41Response:
    """API响应"""
    statusCode: int  # 返回状态码(800为成功，900为失败)
    errorCode: Optional[str] = None  # 错误码
    message: str = ""  # 错误描述(英文)
    description: str = ""  # 错误描述(中文)
    returnObj: Optional[CtecsQueryZonesInRegionV41ReturnObjResponse] = None  # 返回参数
    error: Optional[str] = None  # 错误码(请求成功时不返回)

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsQueryZonesInRegionV41Response':
        """从JSON数据创建响应对象"""
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        return_obj = None
        if 'returnObj' in json_data and json_data['returnObj'] is not None:
            return_obj = CtecsQueryZonesInRegionV41ReturnObjResponse.from_json(json_data['returnObj'])

        return cls(
            statusCode=json_data.get('statusCode', 800),
            errorCode=json_data.get('errorCode'),
            message=json_data.get('message', ""),
            description=json_data.get('description', ""),
            returnObj=return_obj,
            error=json_data.get('error')
        )

class CtecsQueryZonesInRegionV41Api:
    """查询资源池可用区API

    功能：查询单个资源池的可用区信息
    接口文档：/v4/region/get-zones
    """

    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk) if ak and sk else None

    def set_endpoint(self, endpoint: str) -> None:
        """设置API端点"""
        if not endpoint.startswith(('http://', 'https://')):
            raise ValueError("Endpoint must start with http:// or https://")
        self.endpoint = endpoint.rstrip('/')

    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str,
           request: CtecsQueryZonesInRegionV41Request) -> CtecsQueryZonesInRegionV41Response:
        """执行API请求"""
        try:
            url = f"{endpoint}/v4/region/get-zones"
            params = request.to_dict()
            response = client.get(
                url=url,
                params=params,
                credential=credential
            )
            return CtecsQueryZonesInRegionV41Response.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(f"API请求失败: {str(e)}")
