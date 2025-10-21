from typing import List, Optional
from dataclasses import dataclass
from ctyunsdk_ecs20220909.core.client import CtyunClient
from ctyunsdk_ecs20220909.core.credential import Credential
from ctyunsdk_ecs20220909.core.exception import CtyunRequestException
import logging

logger = logging.getLogger(__name__)

@dataclass
class CtecsQueryOrderUuidV41Request:
    """查询订单UUID请求参数"""
    masterOrderId: str  # 订单ID(必填)

    def to_dict(self) -> dict:
        """转换为请求参数字典，过滤None值"""
        return {k: v for k, v in vars(self).items() if v is not None}

@dataclass
class OrderUuidResponse:
    """订单UUID响应数据"""
    orderStatus: str  # 订单状态
    resourceType: str  # 资源类型(VM/EBS/NETWORK)
    resourceUUID: List[str]  # 资源UUID列表

    @classmethod
    def from_json(cls, json_data: dict) -> 'OrderUuidResponse':
        """从JSON创建响应对象"""
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        return cls(
            orderStatus=json_data.get('orderStatus', ''),
            resourceType=json_data.get('resourceType', ''),
            resourceUUID=json_data.get('resourceUUID', [])
        )

@dataclass
class CtecsQueryOrderUuidV41Response:
    """API响应"""
    statusCode: int  # 状态码(800成功/900失败)
    errorCode: Optional[str] = None  # 错误码
    message: str = ""  # 错误信息(英文)
    description: str = ""  # 错误描述(中文)
    returnObj: Optional[OrderUuidResponse] = None  # 返回数据
    error: Optional[str] = None  # 错误码(三段式)

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsQueryOrderUuidV41Response':
        """从JSON创建API响应"""
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        return_obj = None
        if 'returnObj' in json_data and json_data['returnObj']:
            return_obj = OrderUuidResponse.from_json(json_data['returnObj'])

        return cls(
            statusCode=json_data.get('statusCode'),
            errorCode=json_data.get('errorCode'),
            message=json_data.get('message', ''),
            description=json_data.get('description', ''),
            returnObj=return_obj,
            error=json_data.get('error')
        )

class CtecsQueryOrderUuidV41Api:
    """查询订单UUID API

    功能：根据订单号查询资源UUID和状态
    接口文档：/v4/order/query-uuid
    """

    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk) if ak and sk else None
        logger.info("CtecsQueryOrderUuidV41Api initialized")

    def set_endpoint(self, endpoint: str) -> None:
        """设置API端点"""
        if not endpoint.startswith(('http://', 'https://')):
            raise ValueError("Endpoint must start with http:// or https://")
        self.endpoint = endpoint.rstrip('/')
        logger.info(f"API endpoint set to: {self.endpoint}")

    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str,
           request: CtecsQueryOrderUuidV41Request) -> CtecsQueryOrderUuidV41Response:
        """执行API请求"""
        try:
            url = f"{endpoint}/v4/order/query-uuid"
            params = request.to_dict()
            logger.debug(f"Making request to {url} with params: {params}")

            response = client.get(
                url=url,
                params=params,
                credential=credential
            )
            return CtecsQueryOrderUuidV41Response.from_json(response.json())
        except Exception as e:
            logger.error(f"API request failed: {str(e)}")
            raise CtyunRequestException(f"查询订单UUID失败: {str(e)}")
