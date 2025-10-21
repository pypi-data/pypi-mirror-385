from typing import Optional
from ctyunsdk_ecs20220909.core.client import CtyunClient
from ctyunsdk_ecs20220909.core.credential import Credential
from ctyunsdk_ecs20220909.core.exception import CtyunRequestException
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CtecsQueryJobInfoV41Request:
    """请求参数类"""
    regionID: str  # 资源池ID(必填)
    jobID: str  # 异步任务ID(必填)

    def to_dict(self) -> dict:
        """转换为请求参数字典，过滤None值"""
        return {k: v for k, v in vars(self).items() if v is not None}


@dataclass
class CtecsQueryJobInfoV41ReturnObjFieldsResponse:
    """任务信息"""
    taskName: Optional[str] = None  # 任务名

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsQueryJobInfoV41ReturnObjFieldsResponse':
        """从JSON数据创建返回对象"""
        if not json_data:
            return None
        return cls(
            taskName=json_data.get('taskName')
        )


@dataclass
class CtecsQueryJobInfoV41ReturnObjResponse:
    """返回参数对象"""
    jobID: str  # 异步任务ID
    status: int  # 任务状态 (0:执行中 1:执行成功 2:执行失败)
    jobStatus: str  # job任务状态(executing:执行中, success:执行成功, fail:执行失败)
    resourceId: Optional[str] = None  # 资源ID
    fields: Optional[CtecsQueryJobInfoV41ReturnObjFieldsResponse] = None  # 任务信息

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsQueryJobInfoV41ReturnObjResponse':
        """从JSON数据创建返回对象"""
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        fields = None
        if 'fields' in json_data and json_data['fields'] is not None:
            fields = CtecsQueryJobInfoV41ReturnObjFieldsResponse.from_json(json_data['fields'])

        return cls(
            jobID=json_data.get('jobID', ''),
            status=json_data.get('status', 0),
            jobStatus=json_data.get('jobStatus', 'executing'),
            resourceId=json_data.get('resourceId'),
            fields=fields
        )


@dataclass
class CtecsQueryJobInfoV41Response:
    """API响应"""
    statusCode: int  # 返回状态码(800为成功，900为失败)
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: str = ""  # 失败时的错误描述(英文)
    description: str = ""  # 失败时的错误描述(中文)
    returnObj: Optional[CtecsQueryJobInfoV41ReturnObjResponse] = None  # 返回参数

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsQueryJobInfoV41Response':
        """从JSON数据创建响应对象"""
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        return_obj = None
        if 'returnObj' in json_data and json_data['returnObj'] is not None:
            return_obj = CtecsQueryJobInfoV41ReturnObjResponse.from_json(json_data['returnObj'])

        return cls(
            statusCode=json_data.get('statusCode', 800),
            errorCode=json_data.get('errorCode'),
            message=json_data.get('message', ''),
            description=json_data.get('description', ''),
            returnObj=return_obj,
            error=json_data.get('error')
        )


class CtecsQueryJobInfoV41Api:
    """查询异步任务状态API

    功能：查看异步任务job任务状态等
    接口文档：/v4/job/info
    """

    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk) if ak and sk else None
        logger.info("CtecsQueryJobInfoV41Api initialized")

    def set_endpoint(self, endpoint: str) -> None:
        """设置API端点"""
        if not endpoint.startswith(('http://', 'https://')):
            raise ValueError("Endpoint must start with http:// or https://")
        self.endpoint = endpoint.rstrip('/')
        logger.info(f"API endpoint set to: {self.endpoint}")

    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str,
           request: CtecsQueryJobInfoV41Request) -> CtecsQueryJobInfoV41Response:
        """执行API请求"""
        try:
            url = f"{endpoint}/v4/job/info"
            params = request.to_dict()
            logger.debug(f"Making request to {url} with params: {params}")

            response = client.get(
                url=url,
                params=params,
                credential=credential
            )
            return CtecsQueryJobInfoV41Response.from_json(response.json())
        except Exception as e:
            logger.error(f"API request failed: {str(e)}")
            raise CtyunRequestException(f"API请求失败: {str(e)}")
