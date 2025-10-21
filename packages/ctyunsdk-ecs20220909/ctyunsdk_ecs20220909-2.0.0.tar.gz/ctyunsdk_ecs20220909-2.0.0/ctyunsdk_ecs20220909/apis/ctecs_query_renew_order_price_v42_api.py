from ctyunsdk_ecs20220909.core.client import CtyunClient
from ctyunsdk_ecs20220909.core.credential import Credential
from ctyunsdk_ecs20220909.core.exception import CtyunRequestException

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class CtecsQueryRenewOrderPriceV42Request:
    regionID: str  # 资源池ID
    resourceType: str  # 资源类型
    resourceID: str  # 资源uuid
    cycleType: str  # 订购周期类型，可选值：MONTH 月，YEAR 年
    cycleCount: int  # 订购周期大小，订购周期类型为MONTH时范围[1,36]，订购周期类型为YEAR时范围[1,3]

    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if v is not None}


@dataclass
class CtecsQueryRenewOrderPriceV42ReturnObjSubOrderPricesOrderItemPricesResponse:
    """子订单项价格信息响应"""
    resourceType: Optional[str] = None  # 资源类型
    totalPrice: Optional[float] = None  # 总价格，单位CNY
    finalPrice: Optional[float] = None  # 最终价格，单位CNY

    @classmethod
    def from_json(cls, json_data: dict) -> Optional[
        'CtecsQueryRenewOrderPriceV42ReturnObjSubOrderPricesOrderItemPricesResponse']:
        """从JSON数据创建对象"""
        if not json_data:
            return None
        return cls(
            resourceType=json_data.get('resourceType'),
            totalPrice=json_data.get('totalPrice'),
            finalPrice=json_data.get('finalPrice')
        )


@dataclass
class CtecsQueryRenewOrderPriceV42ReturnObjSubOrderPricesResponse:
    """子订单价格信息响应"""
    serviceTag: Optional[str] = None  # 服务类型
    totalPrice: Optional[float] = None  # 子订单总价格，单位CNY
    finalPrice: Optional[float] = None  # 子订单最终价格，单位CNY
    orderItemPrices: Optional[
        List[CtecsQueryRenewOrderPriceV42ReturnObjSubOrderPricesOrderItemPricesResponse]] = None  # item价格信息

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryRenewOrderPriceV42ReturnObjSubOrderPricesResponse']:
        """从JSON数据创建对象"""
        if not json_data:
            return None

        order_item_price = None
        if 'orderItemPrices' in json_data and json_data.get('orderItemPrices') is not None:
            order_item_price = [
                CtecsQueryRenewOrderPriceV42ReturnObjSubOrderPricesOrderItemPricesResponse.from_json(item)
                for item in json_data.get('orderItemPrices')
            ]

        return cls(
            serviceTag=json_data.get('serviceTag'),
            totalPrice=json_data.get('totalPrice'),
            finalPrice=json_data.get('finalPrice'),
            orderItemPrices=order_item_price
        )


@dataclass
class CtecsQueryRenewOrderPriceV42ReturnObjResponse:
    """询价返回对象

    包含总价格、最终价格和子订单价格信息
    """
    totalPrice: Optional[float] = None  # 总价格，单位CNY
    finalPrice: Optional[float] = None  # 最终价格，单位CNY
    subOrderPrices: Optional[List[CtecsQueryRenewOrderPriceV42ReturnObjSubOrderPricesResponse]] = None  # 子订单价格信息

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryRenewOrderPriceV42ReturnObjResponse']:
        """从JSON数据创建对象"""
        if not json_data:
            return None

        sub_order_price = None
        if 'subOrderPrices' in json_data and json_data.get('subOrderPrices') is not None:
            sub_order_price = [
                CtecsQueryRenewOrderPriceV42ReturnObjSubOrderPricesResponse.from_json(sub_order)
                for sub_order in json_data.get('subOrderPrices')
            ]

        return cls(
            totalPrice=json_data.get('totalPrice'),
            finalPrice=json_data.get('finalPrice'),
            subOrderPrices=sub_order_price
        )


@dataclass
class CtecsQueryRenewOrderPriceV42Response:
    """询价API响应
    包含状态码、错误信息和返回对象
    """
    statusCode: int  # 返回状态码(800为成功，900为失败)
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: str = ""  # 失败时的错误描述(英文)
    description: str = ""  # 失败时的错误描述(中文)
    returnObj: Optional[CtecsQueryRenewOrderPriceV42ReturnObjResponse] = None  # 返回参数
    error: Optional[str] = None  # 错误码，请求成功时不返回

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsQueryRenewOrderPriceV42Response':
        """从JSON数据创建响应对象"""
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        return_obj = None
        if 'returnObj' in json_data and json_data['returnObj'] is not None:
            return_obj = CtecsQueryRenewOrderPriceV42ReturnObjResponse.from_json(json_data['returnObj'])

        return cls(
            statusCode=json_data.get('statusCode'),
            errorCode=json_data.get('errorCode'),
            message=json_data.get('message', ''),
            description=json_data.get('description', ''),
            returnObj=return_obj,
            error=json_data.get('error')
        )


# 支持云主机、云硬盘、弹性公网IP、NAT网关、共享带宽、物理机、性能保障型负载均衡、云主机备份存储库和云硬盘备份存储库产品的包年/包月订单的续订询价功能
class CtecsQueryRenewOrderPriceV42Api:
    def __init__(self, ak: str = None, sk: str = None):
        """初始化API
        Args:
            ak: 访问密钥AK
            sk: 访问密钥SK
        """
        self.endpoint = None
        self.credential = Credential(ak, sk) if ak and sk else None

    def set_endpoint(self, endpoint: str) -> None:
        """设置API端点
        Args:
            endpoint: API端点URL，必须以http://或https://开头
        """
        if not endpoint.startswith(('http://', 'https://')):
            raise ValueError("Endpoint must start with http:// or https://")
        self.endpoint = endpoint.rstrip('/')

    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str,
           request: CtecsQueryRenewOrderPriceV42Request) -> CtecsQueryRenewOrderPriceV42Response:
        """执行API请求
        Args:
            credential: 认证凭证
            client: CTYun客户端
            endpoint: API端点URL
            request: 请求参数对象
        Returns:
            API响应对象
        Raises:
            CtyunRequestException: 当API请求失败时抛出
        """
        url = f"{endpoint.rstrip('/')}/v4/renew-order/query-price"
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            response = client.post(
                url=url,
                params={},
                header_params=set(),
                data=request_dict,
                credential=credential
            )
            return CtecsQueryRenewOrderPriceV42Response.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(f"API请求失败: {str(e)}")
