from typing import List, Optional
from core.client import CtyunClient
from core.credential import Credential
from core.exception import CtyunRequestException
from dataclasses import dataclass

@dataclass
class CtecsListRegionsV41Request:
    """请求参数类，保持原类名不变"""
    regionName: Optional[str] = None  # 资源池名称(非必填)

    def to_dict(self) -> dict:
        """转换为请求参数字典，过滤None值"""
        return {k: v for k, v in vars(self).items() if v is not None}

@dataclass
class CtecsListRegionsV41ReturnObjRegionListResponse:
    """资源池详细信息，保持原类名不变"""
    regionID: str  # 资源池ID
    regionParent: str  # 资源池所属省份
    regionName: str  # 资源池名称
    regionType: str  # 资源池类型
    isMultiZones: bool  # 是否多可用区
    zoneList: List[str]  # 可用区列表
    regionCode: str  # 地域编号
    openapiAvailable: bool  # 是否支持OpenAPI访问
    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsListRegionsV41ReturnObjRegionListResponse':
        """确保返回对象格式"""
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        return cls(
            regionID=json_data['regionID'],
            regionParent=json_data['regionParent'],
            regionName=json_data['regionName'],
            regionType=json_data.get('regionType', 'public'),
            isMultiZones=json_data.get('isMultiZones', False),
            zoneList=json_data.get('zoneList', []),
            regionCode=json_data['regionCode'],
            openapiAvailable=json_data.get('openapiAvailable', True)
        )

@dataclass
class CtecsListRegionsV41ReturnObjResponse:
    """返回参数，保持原类名不变"""
    regionList: List[CtecsListRegionsV41ReturnObjRegionListResponse] = None

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsListRegionsV41ReturnObjResponse':
        """确保返回对象格式"""
        if not json_data:
            return cls()
        region_list = [CtecsListRegionsV41ReturnObjRegionListResponse.from_json(region)
                      for region in json_data.get('regionList', [])]
        return cls(regionList=region_list)

@dataclass
class CtecsListRegionsV41Response:
    """API响应，保持原类名不变"""
    statusCode: int # 返回状态码('800为成功，900为失败)
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码。
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: str = ""  # 失败时的错误描述，一般为英文描述
    description: str = ""  # 失败时的错误描述，一般为中文描述
    returnObj: CtecsListRegionsV41ReturnObjResponse = None  # 返回参数

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsListRegionsV41Response':
        """确保返回对象格式"""
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        return_obj = None
        if 'returnObj' in json_data and json_data['returnObj'] is not None:
            return_obj = CtecsListRegionsV41ReturnObjResponse.from_json(json_data['returnObj'])

        return cls(
            statusCode=json_data.get('statusCode'),
            errorCode=json_data.get('errorCode'),
            message=json_data.get('message', ""),
            description=json_data.get('description', ""),
            returnObj=return_obj,
            error=json_data.get('error')
        )

class CtecsListRegionsV41Api:
    """API类，保持原类名和方法名不变"""
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk) if ak and sk else None

    def set_endpoint(self, endpoint: str) -> None:
        """设置API端点，保持原方法名不变"""
        if not endpoint.startswith(('http://', 'https://')):
            raise ValueError("Endpoint must start with http:// or https://")
        self.endpoint = endpoint.rstrip('/')

    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str,
           request: CtecsListRegionsV41Request) -> CtecsListRegionsV41Response:
        """执行API请求，保持原方法名不变"""
        try:
            url = f"{endpoint}/v4/region/list-regions"
            params = request.to_dict()
            response = client.get(
                url=url,
                params=params,
                credential=credential
            )
            return CtecsListRegionsV41Response.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(f"API请求失败: {str(e)}")