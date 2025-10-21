from typing import List, Optional
from core.client import CtyunClient
from core.credential import Credential
from core.exception import CtyunRequestException
from dataclasses import dataclass


@dataclass
class CtecsCheckDemandInRegionV41Request:
    """请求参数类"""
    regionID: str  # 资源池ID(必填)
    productType: str  # 产品类型 可选值：ecs:云主机,eip:IP,ebs:磁盘(必填)
    azName: Optional[str] = None  # 可用区名称(云主机和云硬盘规格资源池4.0区分az)
    flavorID: Optional[str] = None  # productType为ecs时传，云主机规格ID
    specName: Optional[str] = None  # productType为ecs时传，主机规格名称
    ecsAmount: Optional[int] = 1  # productType为ecs时传，云主机需求量(默认1)
    ebsType: Optional[str] = None  # productType为ebs时传，磁盘类型
    ebsSize: Optional[int] = None  # productType为ebs时传，磁盘大小
    eipAmount: Optional[int] = 1  # productType为eip时传，IP需求量(默认1)

    def to_dict(self) -> dict:
        """转换为请求参数字典，过滤None值"""
        return {k: v for k, v in vars(self).items() if v is not None}


@dataclass
class CtecsCheckDemandInRegionV41ReturnObjUsedInfoResponse:
    """用户已用量信息(paas带channel的调用不会返回)"""
    ecsCount: Optional[int] = None  # 云主机数量
    cpuVcoreCount: Optional[int] = None  # CPU核数(云主机)
    memUsed: Optional[int] = None  # 内存使用量MB(云主机)
    ebsSize: Optional[int] = None  # 磁盘总容量GB
    ebsCount: Optional[int] = None  # 磁盘数量
    ipCount: Optional[int] = None  # IP数量

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsCheckDemandInRegionV41ReturnObjUsedInfoResponse':
        """从JSON数据创建返回对象"""
        if not json_data:
            return None
        return cls(
            ecsCount=json_data.get('ecsCount'),
            cpuVcoreCount=json_data.get('cpuVcoreCount'),
            memUsed=json_data.get('memUsed'),
            ebsSize=json_data.get('ebsSize'),
            ebsCount=json_data.get('ebsCount'),
            ipCount=json_data.get('ipCount')
        )


@dataclass
class CtecsCheckDemandInRegionV41ReturnObjQuotaInfoResponse:
    """产品用户配额信息(paas带channel的调用不会返回)"""
    ecsCountQuota: Optional[int] = None  # 云主机数量配额
    # cpuVcoreQutoa: Optional[int] = None  # CPU核数配额(云主机)
    cpuVcoreQuota: Optional[int] = None  # CPU核数配额(云主机)
    memQuota: Optional[int] = None  # 内存配额MB(云主机)
    ebsSizeQuota: Optional[int] = None  # 磁盘总容量配额GB
    ebsCountQuota: Optional[int] = None  # 磁盘数量配额
    ipCountQuota: Optional[int] = None  # IP数量配额

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsCheckDemandInRegionV41ReturnObjQuotaInfoResponse':
        """从JSON数据创建返回对象"""
        if not json_data:
            return None
        return cls(
            ecsCountQuota=json_data.get('ecsCountQuota'),
            cpuVcoreQuota=json_data.get('cpuVcoreQuota'),
            memQuota=json_data.get('memQuota'),
            ebsSizeQuota=json_data.get('ebsSizeQuota'),
            ebsCountQuota=json_data.get('ebsCountQuota'),
            ipCountQuota=json_data.get('ipCountQuota')
        )

@dataclass
class CtecsCheckDemandInRegionV41ReturnObjResponse:
    """返回参数对象"""
    satisfied: Optional[bool] = None  # 是否可售
    sellout: Optional[bool] = None  # 是否售罄
    hasQuota: Optional[bool] = None  # 用户配额余量是否满足
    quotaInfo: Optional[CtecsCheckDemandInRegionV41ReturnObjQuotaInfoResponse] = None  # 产品用户配额信息
    usedInfo: Optional[CtecsCheckDemandInRegionV41ReturnObjUsedInfoResponse] = None  # 用户已用量信息

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsCheckDemandInRegionV41ReturnObjResponse':
        """从JSON数据创建返回对象"""
        if not json_data:
            return cls()

        quota_info = None
        if 'quotaInfo' in json_data and json_data['quotaInfo'] is not None:
            quota_info = CtecsCheckDemandInRegionV41ReturnObjQuotaInfoResponse.from_json(json_data['quotaInfo'])

        used_info = None
        if 'usedInfo' in json_data and json_data['usedInfo'] is not None:
            used_info = CtecsCheckDemandInRegionV41ReturnObjUsedInfoResponse.from_json(json_data['usedInfo'])

        return cls(
            satisfied=json_data.get('satisfied'),
            sellout=json_data.get('sellout'),
            hasQuota=json_data.get('hasQuota'),
            quotaInfo=quota_info,
            usedInfo=used_info
        )

@dataclass
class CtecsCheckDemandInRegionV41Response:
    """API响应"""
    statusCode: int  # 返回状态码(800为成功，900为失败)
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: str = ""  # 失败时的错误描述(英文)
    description: str = ""  # 失败时的错误描述(中文)
    returnObj: Optional[CtecsCheckDemandInRegionV41ReturnObjResponse] = None  # 返回参数
    error: Optional[str] = None  # 错误码，请求成功时不返回

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsCheckDemandInRegionV41Response':
        """从JSON数据创建响应对象"""
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        return_obj = None
        if 'returnObj' in json_data and json_data['returnObj'] is not None:
            return_obj = CtecsCheckDemandInRegionV41ReturnObjResponse.from_json(json_data['returnObj'])

        return cls(
            statusCode=json_data.get('statusCode', 900),
            errorCode=json_data.get('errorCode'),
            message=json_data.get('message', ''),
            description=json_data.get('description', ''),
            returnObj=return_obj,
            error=json_data.get('error')
        )


class CtecsCheckDemandInRegionV41Api:
    """查询资源池产品可售状态API

    功能：查询用户可用的产品是否可售，支持云主机、云硬盘、弹性公网IP产品的可售查询
    接口文档：/v4/region/check-demand
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
           request: CtecsCheckDemandInRegionV41Request) -> CtecsCheckDemandInRegionV41Response:
        """执行API请求"""
        try:
            url = f"{endpoint}/v4/region/check-demand"
            params = request.to_dict()
            response = client.get(
                url=url,
                params=params,
                credential=credential
            )
            return CtecsCheckDemandInRegionV41Response.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(f"API请求失败: {str(e)}")
