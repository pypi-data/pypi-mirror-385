from typing import List, Optional
from ctyunsdk_ecs20220909.core.client import CtyunClient
from ctyunsdk_ecs20220909.core.credential import Credential
from ctyunsdk_ecs20220909.core.exception import CtyunRequestException
from dataclasses import dataclass


@dataclass
class CtecsQuerySummaryInRegionV41Request:
    """请求参数类"""
    regionID: str  # 资源池ID(必填)

    def to_dict(self) -> dict:
        """转换为请求参数字典，过滤None值"""
        return {k: v for k, v in vars(self).items() if v is not None}


@dataclass
class CtecsQuerySummaryInRegionV41ReturnObjResponse:
    """返回参数对象"""
    regionID: str  # 资源池ID
    regionParent: str  # 资源池所属省份
    regionName: str  # 资源池名称
    regionType: str  # 资源池类型
    isMultiZones: bool  # 是否多可用区
    zoneList: List[str]  # 可用区列表
    cpuArches: List[str]  # 资源池cpu架构信息
    regionVersion: str  # 资源池版本
    dedicated: bool  # 是否是专属资源池
    province: str  # 省份
    city: str  # 城市
    openapiAvailable: bool  # 是否支持OpenAPI访问

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsQuerySummaryInRegionV41ReturnObjResponse':
        """从JSON数据创建返回对象"""
        if not json_data:
            raise ValueError("JSON data cannot be empty")
        return cls(
            regionID=json_data.get('regionID', ''),
            regionParent=json_data.get('regionParent', ''),
            regionName=json_data.get('regionName', ''),
            regionType=json_data.get('regionType', ''),
            isMultiZones=json_data.get('isMultiZones'),
            zoneList=json_data.get('zoneList', []),
            cpuArches=json_data.get('cpuArches', []),
            regionVersion=json_data.get('regionVersion', ''),
            dedicated=json_data.get('dedicated'),
            province=json_data.get('province', ''),
            city=json_data.get('city', ''),
            openapiAvailable=json_data.get('openapiAvailable')
        )


@dataclass
class CtecsQuerySummaryInRegionV41Response:
    """API响应"""
    statusCode: int  # 返回状态码(800为成功，900为失败)
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: str = ""  # 失败时的错误描述(英文)
    description: str = ""  # 失败时的错误描述(中文)
    returnObj: Optional[CtecsQuerySummaryInRegionV41ReturnObjResponse] = None  # 返回参数
    error: Optional[str] = None  # 错误码，请求成功时不返回

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsQuerySummaryInRegionV41Response':
        """从JSON数据创建响应对象"""
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        return_obj = None
        if 'returnObj' in json_data and json_data['returnObj'] is not None:
            return_obj = CtecsQuerySummaryInRegionV41ReturnObjResponse.from_json(json_data['returnObj'])

        return cls(
            statusCode=json_data.get('statusCode'),
            errorCode=json_data.get('errorCode'),
            message=json_data.get('message', ''),
            description=json_data.get('description', ''),
            returnObj=return_obj,
            error=json_data.get('error')
        )


class CtecsQuerySummaryInRegionV41Api:
    """查询资源池概况API

    功能：查询资源池概况，包括地域、多AZ信息、支持的CPU架构、资源池占用类型、资源池版本信息等
    接口文档：/v4/region/get-summary
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
           request: CtecsQuerySummaryInRegionV41Request) -> CtecsQuerySummaryInRegionV41Response:
        """执行API请求"""
        try:
            url = f"{endpoint}/v4/region/get-summary"
            params = request.to_dict()
            response = client.get(
                url=url,
                params=params,
                credential=credential
            )
            return CtecsQuerySummaryInRegionV41Response.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(f"API请求失败: {str(e)}")
