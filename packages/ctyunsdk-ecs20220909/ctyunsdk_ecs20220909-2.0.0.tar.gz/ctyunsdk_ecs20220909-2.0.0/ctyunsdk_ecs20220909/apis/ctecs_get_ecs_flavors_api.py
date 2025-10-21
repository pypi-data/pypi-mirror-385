from typing import List, Optional
from dataclasses import dataclass
from ctyunsdk_ecs20220909.core.client import CtyunClient
from ctyunsdk_ecs20220909.core.credential import Credential
from ctyunsdk_ecs20220909.core.exception import CtyunRequestException
import logging

logger = logging.getLogger(__name__)


@dataclass
class CtecsGetEcsFlavorsRequest:
    """请求参数类"""
    regionID: str  # 资源池ID(必填)
    azName: Optional[str] = None  # 多az可用区名称（4.0场景）
    series: Optional[str] = None  # 系列

    def to_dict(self) -> dict:
        """转换为请求参数字典，过滤None值"""
        return {k: v for k, v in vars(self).items() if v is not None}


@dataclass
class FlavorSpecification:
    """虚机规格详情"""
    flavorID: str  # 规格ID
    specName: str  # 规格名称
    flavorType: str  # 规格类型
    flavorName: str  # 规格类型名称
    cpuNum: int  # CPU核数
    memSize: int  # 内存大小(GB)
    multiQueue: int  # 网卡多队列数
    pps: int  # 网络最大收发包能力(万PPS)
    bandwidthBase: float  # 基准带宽(Gbps)
    bandwidthMax: float  # 最大带宽(Gbps)
    cpuArch: str  # CPU架构(x86/arm)
    series: str  # 系列
    azList: Optional[List[str]] = None  # 支持的AZ列表
    nicCount: Optional[int] = None  # 最大可挂载网卡数
    ctLimitCount: Optional[int] = None  # 最大连接数

    @classmethod
    def from_json(cls, json_data: dict) -> 'FlavorSpecification':
        """从JSON数据创建规格对象"""
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        return cls(
            flavorID=json_data.get('flavorID', ''),
            specName=json_data.get('specName', ''),
            flavorType=json_data.get('flavorType', ''),
            flavorName=json_data.get('flavorName', ''),
            cpuNum=json_data.get('cpuNum', 0),
            memSize=json_data.get('memSize', 0),
            multiQueue=json_data.get('multiQueue', 0),
            pps=json_data.get('pps', 0),
            bandwidthBase=float(json_data.get('bandwidthBase', 0)),
            bandwidthMax=float(json_data.get('bandwidthMax', 0)),
            cpuArch=json_data.get('cpuArch', ''),
            series=json_data.get('series', ''),
            azList=json_data.get('azList'),
            nicCount=json_data.get('nicCount'),
            ctLimitCount=json_data.get('ctLimitCount')
        )


@dataclass
class FlavorListResponse:
    """规格列表响应"""
    totalCount: int  # 总条数
    results: List[FlavorSpecification]  # 规格列表

    @classmethod
    def from_json(cls, json_data: dict) -> 'FlavorListResponse':
        """从JSON数据创建规格列表响应"""
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        results = []
        if 'results' in json_data and json_data['results']:
            results = [FlavorSpecification.from_json(item) for item in json_data['results']]

        return cls(
            totalCount=json_data.get('totalCount', 0),
            results=results
        )


@dataclass
class CtecsGetEcsFlavorsResponse:
    """API响应"""
    statusCode: int  # 返回状态码(800为成功，900为失败)
    errorCode: Optional[str] = None  # # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # # 错误码，为product.module.code三段式码
    message: str = ""  # 错误信息(英文)
    description: str = ""  # 错误描述(中文)
    returnObj: Optional[FlavorListResponse] = None  # 返回数据

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsGetEcsFlavorsResponse':
        """从JSON数据创建API响应"""
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        return_obj = None
        if 'returnObj' in json_data and json_data['returnObj']:
            return_obj = FlavorListResponse.from_json(json_data['returnObj'])

        return cls(
            statusCode=json_data.get('statusCode'),
            errorCode=json_data.get('errorCode'),
            message=json_data.get('message', ''),
            description=json_data.get('description', ''),
            returnObj=return_obj,
            error=json_data.get('error')
        )


class CtecsGetEcsFlavorsApi:
    """查询虚机规格API

    功能：查询资源池虚机规格信息
    接口文档：/v4/common/get-ecs-flavors
    """

    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk) if ak and sk else None
        logger.info("CtecsGetEcsFlavorsApi initialized")

    def set_endpoint(self, endpoint: str) -> None:
        """设置API端点"""
        if not endpoint.startswith(('http://', 'https://')):
            raise ValueError("Endpoint must start with http:// or https://")
        self.endpoint = endpoint.rstrip('/')
        logger.info(f"API endpoint set to: {self.endpoint}")

    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str,
           request: CtecsGetEcsFlavorsRequest) -> CtecsGetEcsFlavorsResponse:
        """执行API请求"""
        try:
            url = f"{endpoint}/v4/common/get-ecs-flavors"
            params = request.to_dict()
            logger.debug(f"Making request to {url} with params: {params}")

            response = client.get(
                url=url,
                params=params,
                credential=credential
            )
            return CtecsGetEcsFlavorsResponse.from_json(response.json())
        except Exception as e:
            logger.error(f"API request failed: {str(e)}")
            raise CtyunRequestException(f"API请求失败: {str(e)}")
