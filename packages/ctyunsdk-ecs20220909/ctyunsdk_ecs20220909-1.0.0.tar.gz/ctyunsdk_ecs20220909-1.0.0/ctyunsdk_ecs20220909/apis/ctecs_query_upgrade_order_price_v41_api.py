from enum import Enum

from ctyunsdk_ecs20220909.core.client import CtyunClient
from ctyunsdk_ecs20220909.core.credential import Credential
from ctyunsdk_ecs20220909.core.exception import CtyunRequestException

from dataclasses import dataclass
from typing import Optional, List


class ResourceTypeEnum(Enum):
    VM = "VM"
    EBS = "EBS"
    IP = "IP"
    IP_POOL = "IP_POOL"
    NAT = "NAT"
    PGELB = "PGELB"
    CBR_VM = "CBR_VM"
    CBR_VBS = "CBR_VBS"

    @classmethod
    def get_all_values(cls) -> list:
        return [item.value for item in cls]


@dataclass
class CtecsQueryUpgradeOrderPriceV41Request:
    regionID: str  # 资源池ID
    resourceUUID: str  # 资源uuid
    resourceType: str  # 资源类型
    flavorName: Optional[str] = None  # 云主机规格，当resourceType为VM时必填
    bandwidth: Optional[int] = None  # 带宽大小，范围[1,2000]，需大于当前带宽，当resourceType为IP时必填
    diskSize: Optional[int] = None  # 磁盘大小，范围[10,2000]，需大于当前大小，当resourceType为EBS时必填
    natType: Optional[str] = None  # nat规格，当resourceType为NAT时必填
    ipPoolBandwidth: Optional[int] = None  # 共享带宽大小，范围[5,2000]，需大于当前带宽，当resourceType为IP_POOL时必填
    elbType: Optional[str] = None  # 性能保障型负载均衡类型(支持standardI/standardII/enhancedI/enhancedII/higherI)，当resourceType为PGELB时必填
    cbrValue: Optional[int] = None  # 存储库大小，100-1024000GB，当resourceType为CBR_VM或CBR_VBS时必填

    def to_dict(self) -> dict:
        if self.resourceType not in ResourceTypeEnum.get_all_values():
            raise ValueError(f"Invalid value for resourceType: {self.resourceType}. Valid values are: {ResourceTypeEnum.get_all_values()}")
        if self.resourceType == ResourceTypeEnum.VM and self.flavorName is None:
            raise ValueError("When resourceType is VM, flavorName is required.")
        if self.resourceType == ResourceTypeEnum.IP and self.bandwidth is None:
            raise ValueError("When resourceType is IP, bandwidth is required.")
        if self.resourceType == ResourceTypeEnum.EBS and self.diskSize is None:
            raise ValueError("When resourceType is EBS, diskSize is required.")
        if self.resourceType == ResourceTypeEnum.NAT and self.natType is None:
            raise ValueError("When resourceType is NAT, natType is required.")
        if self.resourceType == ResourceTypeEnum.IP_POOL and self.ipPoolBandwidth is None:
            raise ValueError("When resourceType is IP_POOL, ipPoolBandwidth is required.")
        if self.resourceType == ResourceTypeEnum.PGELB and self.elbType is None:
            raise ValueError("When resourceType is PGELB, elbType is required.")
        if self.resourceType == ResourceTypeEnum.CBR_VM and self.cbrValue is None:
            raise ValueError("When resourceType is CBR_VM, cbrValue is required.")
        if self.resourceType == ResourceTypeEnum.CBR_VBS and self.cbrValue is None:
            raise ValueError("When resourceType is CBR_VBS, cbrValue is required.")

        return {k: v for k, v in vars(self).items() if v is not None }


@dataclass
class CtecsQueryUpgradeOrderPriceV41ReturnObjSubOrderPricesOrderItemPricesResponse:
    resourceType: Optional[str] = None  # 资源类型
    totalPrice: Optional[float] = None  # 总价格，单位CNY
    finalPrice: Optional[float] = None  # 最终价格，单位CNY

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryUpgradeOrderPriceV41ReturnObjSubOrderPricesOrderItemPricesResponse']:
        if not json_data:
            return None
        return cls(
            resourceType=json_data.get('resourceType'),
            totalPrice=json_data.get('totalPrice'),
            finalPrice=json_data.get('finalPrice')
        )

@dataclass
class CtecsQueryUpgradeOrderPriceV41ReturnObjSubOrderPricesResponse:
    serviceTag: Optional[str] = None  # 服务类型
    totalPrice: Optional[int] = None  # 总价格，单位CNY
    finalPrice: Optional[int] = None  # 最终价格，单位CNY
    orderItemPrices: Optional[List[Optional[CtecsQueryUpgradeOrderPriceV41ReturnObjSubOrderPricesOrderItemPricesResponse]]] = None  # 资源价格信息

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryUpgradeOrderPriceV41ReturnObjSubOrderPricesResponse']:
        if not json_data:
            return None

        order_item_price = None
        if 'orderItemPrices' in json_data and json_data.get('orderItemPrices') is not None:
            order_item_price = [
                CtecsQueryUpgradeOrderPriceV41ReturnObjSubOrderPricesOrderItemPricesResponse.from_json(item)
                for item in json_data.get('orderItemPrices')
            ]

        return cls(
            serviceTag=json_data.get('serviceTag'),
            totalPrice=json_data.get('totalPrice'),
            finalPrice=json_data.get('finalPrice'),
            orderItemPrices=order_item_price
        )

@dataclass
class CtecsQueryUpgradeOrderPriceV41ReturnObjResponse:
    """成功时返回的数据，参见returnObj对象结构"""
    totalPrice: Optional[float] = None  # 总价格，单位CNY
    discountPrice: Optional[float] = None  # 折后价格，单位CNY
    finalPrice: Optional[float] = None  # 最终价格，单位CNY
    subOrderPrices: Optional[List[Optional[CtecsQueryUpgradeOrderPriceV41ReturnObjSubOrderPricesResponse]]] = None  # 子订单价格信息

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryUpgradeOrderPriceV41ReturnObjResponse']:
        if not json_data:
            return None

        sub_order_price = None
        if 'subOrderPrices' in json_data and json_data.get('subOrderPrices') is not None:
            sub_order_price = [
                CtecsQueryUpgradeOrderPriceV41ReturnObjSubOrderPricesResponse.from_json(sub_order)
                for sub_order in json_data.get('subOrderPrices')
            ]

        return cls(
            totalPrice=json_data.get('totalPrice'),
            discountPrice=json_data.get('discountPrice'),
            finalPrice=json_data.get('finalPrice'),
            subOrderPrices=sub_order_price
        )

@dataclass
class CtecsQueryUpgradeOrderPriceV41Response:
    """询价API响应
    包含状态码、错误信息和返回对象
    """
    statusCode: int  # 返回状态码(800为成功，900为失败)
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: str = ""  # 失败时的错误描述(英文)
    description: str = ""  # 失败时的错误描述(中文)
    returnObj: Optional[CtecsQueryUpgradeOrderPriceV41ReturnObjResponse] = None  # 返回参数
    error: Optional[str] = None  # 错误码，请求成功时不返回

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsQueryUpgradeOrderPriceV41Response':
        """从JSON数据创建响应对象"""
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        return_obj = None
        if 'returnObj' in json_data and json_data['returnObj'] is not None:
            return_obj = CtecsQueryUpgradeOrderPriceV41ReturnObjResponse.from_json(json_data['returnObj'])

        return cls(
            statusCode=json_data.get('statusCode'),
            errorCode=json_data.get('errorCode'),
            message=json_data.get('message', ''),
            description=json_data.get('description', ''),
            returnObj=return_obj,
            error=json_data.get('error')
        )

# 支持云主机、云硬盘、弹性公网IP、NAT网关、共享带宽、性能保障型负载均衡、云主机备份存储库和云硬盘备份存储库产品的包年/包月或按量订单变配时的询价功能
class CtecsQueryUpgradeOrderPriceV41Api:
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
           request: CtecsQueryUpgradeOrderPriceV41Request) -> CtecsQueryUpgradeOrderPriceV41Response:
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
        url = f"{endpoint.rstrip('/')}/v4/order/upgrade-query-price"
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            response = client.post(
                url=url,
                params={},
                header_params=set(),
                data=request_dict,
                credential=credential
            )
            return CtecsQueryUpgradeOrderPriceV41Response.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(f"API请求失败: {str(e)}")
