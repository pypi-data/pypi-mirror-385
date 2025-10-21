from typing import List, Optional, Dict, Any
from core.client import CtyunClient
from core.credential import Credential
from core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtecsQueryInstanceStatisticsV41Request:
    regionID: str  # 资源池ID，您可以查看<a href="https://www.ctyun.cn/document/10026730/10028695">地域和可用区</a>来了解资源池 <br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a  href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=5851&data=87">资源池列表查询</a>
    projectID: Optional[str] = None  # 企业项目ID，企业项目管理服务提供统一的云资源按企业项目管理，以及企业项目内的资源管理，成员管理。您可以通过查看<a href="https://www.ctyun.cn/document/10017248/10017961">创建企业项目</a>了解如何创建企业项目

    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if v is not None}


@dataclass
class CtecsQueryInstanceStatisticsV41ReturnObjInstanceStatisticsResponse:
    totalCount: Any = None  # 云主机总数
    runningCount: Any = None  # 运行中的云主机数量
    shutdownCount: Any = None  # 关机数量
    expireCount: Any = None  # 过期数量
    expireRunningCount: Any = None  # 过期运行中数量
    expireShutdownCount: Any = None  # 过期已关机数量
    cpuCount: Any = None  # cpu数量
    memoryCount: Any = None  # 内存总量，单位为GB

    @staticmethod
    def from_json(json_data: dict) -> Optional['CtecsQueryInstanceStatisticsV41ReturnObjInstanceStatisticsResponse']:
        if not json_data:
            return None
        obj = CtecsQueryInstanceStatisticsV41ReturnObjInstanceStatisticsResponse(
            totalCount=json_data.get('totalCount'),
            runningCount=json_data.get('runningCount'),
            shutdownCount=json_data.get('shutdownCount'),
            expireCount=json_data.get('expireCount'),
            expireRunningCount=json_data.get('expireRunningCount'),
            expireShutdownCount=json_data.get('expireShutdownCount'),
            cpuCount=json_data.get('cpuCount'),
            memoryCount=json_data.get('memoryCount'),
        )
        return obj

@dataclass
class CtecsQueryInstanceStatisticsV41ReturnObjResponse:
    instanceStatistics: Optional[CtecsQueryInstanceStatisticsV41ReturnObjInstanceStatisticsResponse] = None  # 分页明细

    @staticmethod
    def from_json(json_data: dict) -> Optional['CtecsQueryInstanceStatisticsV41ReturnObjResponse']:
        if not json_data:
            return None

        instance_statistics = None
        if "instanceStatistics" in json_data:
            instanceStatistics = json_data.get("instanceStatistics")
            if instanceStatistics is not None:
                instance_statistics = CtecsQueryInstanceStatisticsV41ReturnObjResponse.from_json(instanceStatistics)

        obj = CtecsQueryInstanceStatisticsV41ReturnObjResponse(
            instanceStatistics=instance_statistics
        )
        return obj

@dataclass
class CtecsQueryInstanceStatisticsV41Response:
    statusCode: Any = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 英文描述信息
    description: Optional[str] = None  # 中文描述信息
    returnObj: Optional[CtecsQueryInstanceStatisticsV41ReturnObjResponse] = None  # 成功时返回的数据


    @staticmethod
    def from_json(json_data: dict) -> Optional['CtecsQueryInstanceStatisticsV41Response']:
        if not json_data:
            return None

        return_obj = None
        if "returnObj" in json_data:
            returnObj = json_data.get("returnObj")
            if returnObj is not None:
                return_obj = CtecsQueryInstanceStatisticsV41ReturnObjResponse.from_json(returnObj)

        obj = CtecsQueryInstanceStatisticsV41Response(
            statusCode=json_data.get('statusCode'),
            errorCode=json_data.get('errorCode'),
            error=json_data.get('error'),
            message=json_data.get('message'),
            description=json_data.get('description'),
            returnObj=return_obj,
        )

        return obj


# 查询用户云主机统计信息
class CtecsQueryInstanceStatisticsV41Api:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtecsQueryInstanceStatisticsV41Request) -> CtecsQueryInstanceStatisticsV41Response:
        url = endpoint + "/v4/ecs/statistics-instance"
        params = {'regionID':request.regionID, 'projectID':request.projectID}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtecsQueryInstanceStatisticsV41Response.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
