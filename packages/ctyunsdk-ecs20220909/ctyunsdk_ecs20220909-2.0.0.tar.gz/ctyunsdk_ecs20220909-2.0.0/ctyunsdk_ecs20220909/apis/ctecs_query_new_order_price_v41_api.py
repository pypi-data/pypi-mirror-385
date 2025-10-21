from ctyunsdk_ecs20220909.core.client import CtyunClient
from ctyunsdk_ecs20220909.core.credential import Credential
from ctyunsdk_ecs20220909.core.exception import CtyunRequestException

from dataclasses import dataclass
from typing import Optional, List, Any

class ResourceTypeEnum:
    VM = "VM"
    EBS = "EBS"
    IP = "IP"
    IP_POOL = "IP_POOL"
    NAT = "NAT"
    BMS = "BMS"
    PGELB = "PGELB"
    CBR_VM = "CBR_VM"
    CBR_VBS = "CBR_VBS"


@dataclass
class CtecsQueryNewOrderPriceV41OrderDisksRequest:
    diskType: str  # 磁盘类型(SAS:高IO,SATA:普通IO,SSD:超高IO,FAST-SSD:极速型SSD)
    diskSize: int  # 磁盘大小

    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items()}


@dataclass
class CtecsQueryNewOrderPriceV41DisksRequest:
    diskType: str  # 磁盘类型(SAS:高IO,SATA:普通IO,SSD:超高IO,FAST-SSD:极速型SSD)
    diskSize: int  # 磁盘大小

    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items()}


@dataclass
class CtecsQueryNewOrderPriceV41Request:
    regionID: str  # 资源池ID
    resourceType: str  # 资源类型(VM:云主机,EBS:云硬盘,IP:弹性公网IP,IP_POOL:共享带宽,NAT:NAT网关,BMS:物理机,PGELB:性能保障型负载均衡,CBR_VM:云主机备份存储库,CBR_VBS:云硬盘备份存储库)
    count: Any  # 订购数量
    onDemand: bool  # 是否按需资源，true 按需 / false 包周期
    cycleType: Optional[str] = None  # 订购周期类型，当onDemand为false时为必填，可选值：MONTH 月,YEAR 年
    cycleCount: Optional[int] = None  # 订购周期大小，订购周期类型为MONTH时范围[1,60]，订购周期类型为YEAR时范围[1,5]，当onDemand为false时为必填
    flavorName: Optional[str] = None  # 云主机规格，当resourceType为VM时必填
    imageUUID: Optional[str] = None  # 云主机镜像UUID，当resourceType为VM时必填
    sysDiskType: Optional[str] = None  # 云主机系统盘类型(SAS:高IO,SATA:普通IO,SSD:超高IO,FAST-SSD:极速型SSD)，当resourceType为VM时必填
    sysDiskSize: Optional[int] = None  # 云主机系统盘大小，范围[40,2048]，当resourceType为VM时必填
    disks: Optional[List[Optional[CtecsQueryNewOrderPriceV41DisksRequest]]] = None  # 数据盘信息，当resourceType为VM选填，订购云主机时如果成套订购数据盘时需要该字段
    bandwidth: Optional[int] = None  # 带宽大小，范围[1,2000]，当resourceType为IP时必填；当resourceType为VM时，如果成套订购弹性公网IP时需要该字段
    diskType: Optional[str] = None  # 磁盘类型(SAS:高IO,SATA:普通IO,SSD:超高IO,FAST-SSD:极速型SSD)，当resourceType为EBS时必填
    diskSize: Optional[int] = None  # 磁盘大小，范围[5,2000]，当resourceType为EBS时必填
    diskMode: Optional[str] = None  # 磁盘模式(VBD/ISCSI/FCSAN)，当resourceType为EBS时必填
    natType: Optional[str] = None  # nat规格(small:小型,medium:中型,large:大型,xlarge:超大型)，当resourceType为NAT时必填
    ipPoolBandwidth: Optional[int] = None  # 共享带宽大小，范围[5,2000]，当resourceType为IP_POOL时必填
    deviceType: Optional[str] = None  # 物理机规格，当resourceType为BMS时必填
    azName: Optional[str] = None  # 物理机规格可用区，当resourceType为BMS时必填
    orderDisks: Optional[List[Optional[CtecsQueryNewOrderPriceV41OrderDisksRequest]]] = None  # 物理机云硬盘信息，当resourceType为BMS选填
    elbType: Optional[str] = None  # 性能保障型负载均衡类型(支持standardI/standardII/enhancedI/enhancedII/higherI)，当resourceType为PGELB时必填
    cbrValue: Optional[int] = None  # 存储库大小，100-1024000GB，当resourceType为CBR_VM或CBR_VBS时必填

    def to_dict(self) -> dict:
        if self.onDemand is False and (not self.cycleType or not self.cycleCount):
            raise CtyunRequestException("When onDemand is False, both cycleType and cycleCount are required.")

        if self.resourceType == ResourceTypeEnum.VM and (not self.flavorName or not self.imageUUID or not self.sysDiskType or not self.sysDiskSize):
            raise CtyunRequestException("When resourceType is VM, all of flavorName, imageUUID, sysDiskType and sysDiskSize are required.")

        if self.resourceType == ResourceTypeEnum.EBS and (not self.diskType or not self.diskSize or not self.diskMode):
            raise CtyunRequestException("When resourceType is EBS, all of diskType, diskSize and diskMode are required.")

        if self.resourceType == ResourceTypeEnum.IP and not self.bandwidth:
            raise CtyunRequestException("When resourceType is IP, bandwidth is required.")

        if self.resourceType == ResourceTypeEnum.IP_POOL and not self.ipPoolBandwidth:
            raise CtyunRequestException("When resourceType is IP_POOL, ipPoolBandwidth is required.")

        if self.resourceType == ResourceTypeEnum.NAT and not self.natType:
            raise CtyunRequestException("When resourceType is NAT, natType is required.")

        if self.resourceType == ResourceTypeEnum.BMS and (not self.deviceType or not self.azName):
            raise CtyunRequestException("When resourceType is BMS, deviceType and azName are required.")

        if self.resourceType == ResourceTypeEnum.PGELB and not self.elbType:
            raise CtyunRequestException("When resourceType is PGELB, elbType is required.")

        if self.resourceType == ResourceTypeEnum.CBR_VM and not self.cbrValue:
            raise CtyunRequestException("When resourceType is CBR_VM, cbrValue is required.")

        if self.resourceType == ResourceTypeEnum.CBR_VBS and not self.cbrValue:
            raise CtyunRequestException("When resourceType is CBR_VBS, cbrValue is required.")

        req_dict = {}
        for k, v in vars(self).items():
            if v is None:
                continue
            if isinstance(v, list):
                tmp_list = []
                for item in v:
                    if hasattr(item, 'to_dict'):
                        tmp_list.append(item.to_dict())
                req_dict[k] = tmp_list
            else:
                req_dict[k] = v
        return req_dict


@dataclass
class CtecsQueryNewOrderPriceV41ReturnObjSubOrderPricesOrderItemPricesResponse:
    """子订单项价格信息响应"""
    resourceType: Optional[str] = None  # 资源类型
    totalPrice: Optional[float] = None  # 总价格，单位CNY
    finalPrice: Optional[float] = None  # 最终价格，单位CNY

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryNewOrderPriceV41ReturnObjSubOrderPricesOrderItemPricesResponse']:
        """从JSON数据创建对象"""
        if not json_data:
            return None
        return cls(
            resourceType=json_data.get('resourceType'),
            totalPrice=json_data.get('totalPrice'),
            finalPrice=json_data.get('finalPrice')
        )


@dataclass
class CtecsQueryNewOrderPriceV41ReturnObjSubOrderPricesResponse:
    """子订单价格信息响应"""
    serviceTag: Optional[str] = None  # 服务类型
    totalPrice: Optional[float] = None  # 子订单总价格，单位CNY
    finalPrice: Optional[float] = None  # 子订单最终价格，单位CNY
    orderItemPrices: Optional[List[CtecsQueryNewOrderPriceV41ReturnObjSubOrderPricesOrderItemPricesResponse]] = None  # item价格信息

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryNewOrderPriceV41ReturnObjSubOrderPricesResponse']:
        """从JSON数据创建对象"""
        if not json_data:
            return None

        order_item_price = None
        if 'orderItemPrices' in json_data and json_data.get('orderItemPrices') is not None:
            order_item_price = [
                CtecsQueryNewOrderPriceV41ReturnObjSubOrderPricesOrderItemPricesResponse.from_json(item)
                for item in json_data.get('orderItemPrices')
            ]

        return cls(
            serviceTag=json_data.get('serviceTag'),
            totalPrice=json_data.get('totalPrice'),
            finalPrice=json_data.get('finalPrice'),
            orderItemPrices=order_item_price
        )


@dataclass
class CtecsQueryNewOrderPriceV41ReturnObjResponse:
    """询价返回对象

    包含总价格、折后价格和子订单价格信息
    """
    totalPrice: Optional[float] = None  # 总价格，单位CNY
    discountPrice: Optional[float] = None  # 折后价格，云主机相关产品有，单位CNY
    finalPrice: Optional[float] = None  # 最终价格，单位CNY
    subOrderPrices: Optional[List[CtecsQueryNewOrderPriceV41ReturnObjSubOrderPricesResponse]] = None  # 子订单价格信息

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryNewOrderPriceV41ReturnObjResponse']:
        """从JSON数据创建对象"""
        if not json_data:
            return None

        sub_order_price = None
        if 'subOrderPrices' in json_data and json_data.get('subOrderPrices') is not None:
            sub_order_price = [
                CtecsQueryNewOrderPriceV41ReturnObjSubOrderPricesResponse.from_json(sub_order)
                for sub_order in json_data.get('subOrderPrices')
            ]

        return cls(
            totalPrice=json_data.get('totalPrice'),
            discountPrice=json_data.get('discountPrice'),
            finalPrice=json_data.get('finalPrice'),
            subOrderPrices=sub_order_price
        )


@dataclass
class CtecsQueryNewOrderPriceV41Response:
    """询价API响应
    包含状态码、错误信息和返回对象
    """
    statusCode: int  # 返回状态码(800为成功，900为失败)
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: str = ""  # 失败时的错误描述(英文)
    description: str = ""  # 失败时的错误描述(中文)
    returnObj: Optional[CtecsQueryNewOrderPriceV41ReturnObjResponse] = None  # 返回参数
    error: Optional[str] = None  # 错误码，请求成功时不返回

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsQueryNewOrderPriceV41Response':
        """从JSON数据创建响应对象"""
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        return_obj = None
        if 'returnObj' in json_data and json_data['returnObj'] is not None:
            return_obj = CtecsQueryNewOrderPriceV41ReturnObjResponse.from_json(json_data['returnObj'])

        return cls(
            statusCode=json_data.get('statusCode'),
            errorCode=json_data.get('errorCode'),
            message=json_data.get('message', ''),
            description=json_data.get('description', ''),
            returnObj=return_obj,
            error=json_data.get('error')
        )

# 购买云产品时询价接口，支持云主机、云硬盘、弹性公网IP、NAT网关、共享带宽、物理机、性能保障型负载均衡、云主机备份存储库和云硬盘备份存储库产品的包年/包月或按量订单的询价功能
class CtecsQueryNewOrderPriceV41Api:
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
           request: CtecsQueryNewOrderPriceV41Request) -> CtecsQueryNewOrderPriceV41Response:
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
        url = f"{endpoint.rstrip('/')}/v4/new-order/query-price"
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            response = client.post(
                url=url,
                params={},
                header_params=set(),
                data=request_dict,
                credential=credential
            )
            return CtecsQueryNewOrderPriceV41Response.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(f"API请求失败: {str(e)}")
