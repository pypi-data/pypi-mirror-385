from ctyunsdk_ecs20220909.core.client import CtyunClient
from ctyunsdk_ecs20220909.core.credential import Credential
from ctyunsdk_ecs20220909.core.exception import CtyunRequestException

from dataclasses import dataclass
from typing import Optional, List, Any


def get_response_attributes(json_data, key, response_class):
    result = None
    if key in json_data:
        data = json_data.get(key)
        if data is not None:
            if isinstance(data, list):
                result = [response_class.from_json(item) for item in data]
            else:
                result = response_class.from_json(data)
    return result

@dataclass
class CtecsDescribeInstancesLabelListRequest:
    labelKey: str  # 标签键，长度限制1~32字符
    labelValue: str  # 标签值，长度限制1~32字符

    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if v is not None}


@dataclass
class CtecsDescribeInstancesRequest:
    regionID: str  # 资源池ID
    azName: Optional[str] = None  # 可用区名称，您可以查看<a href="https://www.ctyun.cn/document/10026730/10028695">地域和可用区</a>来了解可用区 <br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a  href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=5855&data=87">资源池可用区查询</a><br />注：查询结果中zoneList内返回存在可用区名称(即多可用区，本字段填写实际可用区名称)，若查询结果中zoneList为空（即为单可用区，本字段填写default）
    projectID: Optional[str] = None  # 企业项目ID，企业项目管理服务提供统一的云资源按企业项目管理，以及企业项目内的资源管理，成员管理。您可以通过查看<a href="https://www.ctyun.cn/document/10017248/10017961">创建企业项目</a>了解如何创建企业项目
    pageNo: Any = None  # 页码，取值范围：正整数（≥1），注：默认值为1
    pageSize: Any = None  # 每页记录数目，取值范围：[1, 50]，注：默认值为10
    state: Optional[str] = None  # 云主机状态，详见枚举值表<br />注：该参数大小写不敏感（如active可填写为ACTIVE）
    keyword: Optional[str] = None  # 关键字，对部分参数进行模糊查询，包含：instanceName、displayName、instanceID、privateIP
    instanceName: Optional[str] = None  # 云主机名称，精准匹配
    instanceIDList: Optional[str] = None  # 云主机ID列表，多台使用英文逗号分割，您可以查看<a href="https://www.ctyun.cn/products/ecs">弹性云主机</a>了解云主机的相关信息<br />获取：<br/><span style="background-color: rgb(97, 175, 254);color: rgb(255,255,255);padding: 2px; margin:2px">创</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=8281&data=87">创建一台按量付费或包年包月的云主机</a><br /><span style="background-color: rgb(97, 175, 254);color: rgb(255,255,255);padding: 2px; margin:2px">创</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=8282&data=87">批量创建按量付费或包年包月云主机</a>
    securityGroupID: Optional[str] = None  # 安全组ID，模糊匹配，您可以查看<a href="https://www.ctyun.cn/document/10026755/10028520">安全组概述</a>了解安全组相关信息 <br />获取： <br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=18&api=4817&data=94">查询用户安全组列表</a><br /><span style="background-color: rgb(97, 175, 254);color: rgb(255,255,255);padding: 2px; margin:2px">创</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=18&api=4821&data=94">创建安全组</a>
    labelList: Optional[List[Optional[CtecsDescribeInstancesLabelListRequest]]] = None  # 标签信息列表

    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if v is not None}


@dataclass
class CtecsDescribeInstancesReturnObjResultsPciInfoNicPciListResponse:
    networkInterfaceID: Optional[str] = None  # 网卡id
    pci: Optional[str] = None  # pci地址

    @staticmethod
    def from_json(json_data: dict) -> Optional['CtecsDescribeInstancesReturnObjResultsPciInfoNicPciListResponse']:
        if not json_data:
            return None
        obj = CtecsDescribeInstancesReturnObjResultsPciInfoNicPciListResponse(
            networkInterfaceID=json_data.get('networkInterfaceID'),
            pci=json_data.get('pci'),
        )
        return obj

@dataclass
class CtecsDescribeInstancesReturnObjResultsNetworkInfoBoundTypeResponse:

    @staticmethod
    def from_json(json_data: dict) -> dict:
        return {}

@dataclass
class CtecsDescribeInstancesReturnObjResultsAddressesAddressListResponse:
    addr: Optional[str] = None  # IP地址
    version: Any = None  # IP版本
    type: Optional[str] = None  # 网络类型，取值范围：<br />fixed（内网），<br />floating（弹性公网）
    isMaster: Optional[bool] = None  # 是否为主网卡
    macAddress: Optional[str] = None  # mac地址

    @staticmethod
    def from_json(json_data: dict) -> Optional['CtecsDescribeInstancesReturnObjResultsAddressesAddressListResponse']:
        if not json_data:
            return None
        obj = CtecsDescribeInstancesReturnObjResultsAddressesAddressListResponse(
            addr=json_data.get('addr'),
            version=json_data.get('version'),
            type=json_data.get('type'),
            isMaster=json_data.get('isMaster'),
            macAddress=json_data.get('macAddress'),
        )
        return obj


@dataclass
class CtecsDescribeInstancesReturnObjResultsPciInfoResponse:
    nicPciList: Optional[List[Optional[CtecsDescribeInstancesReturnObjResultsPciInfoNicPciListResponse]]]  # 网卡pci信息列表

    @staticmethod
    def from_json(json_data: dict) -> Optional['CtecsDescribeInstancesReturnObjResultsPciInfoResponse']:
        if not json_data:
            return None
        obj = CtecsDescribeInstancesReturnObjResultsPciInfoResponse(
            nicPciList=get_response_attributes(json_data, "nicPciList", CtecsDescribeInstancesReturnObjResultsPciInfoNicPciListResponse),
        )
        return obj


@dataclass
class CtecsDescribeInstancesReturnObjResultsNetworkInfoResponse:
    subnetID: Optional[str] = None  # 子网ID
    ipAddress: Optional[str] = None  # IP地址
    boundType: Optional[CtecsDescribeInstancesReturnObjResultsNetworkInfoBoundTypeResponse] = None  # 绑定类型

    @staticmethod
    def from_json(json_data: dict) -> Optional['CtecsDescribeInstancesReturnObjResultsNetworkInfoResponse']:
        if not json_data:
            return None
        obj = CtecsDescribeInstancesReturnObjResultsNetworkInfoResponse(
            subnetID=json_data.get('subnetID'),
            ipAddress=json_data.get('ipAddress'),
            boundType=get_response_attributes(json_data, "boundType", CtecsDescribeInstancesReturnObjResultsNetworkInfoBoundTypeResponse),
        )
        return obj


@dataclass
class CtecsDescribeInstancesReturnObjResultsFlavorResponse:
    flavorID: Optional[str] = None  # 规格ID
    flavorName: Optional[str] = None  # 规格名称
    flavorCPU: Any = None  # VCPU
    flavorRAM: Any = None  # 内存
    gpuType: Optional[str] = None  # GPU类型，取值范围：T4、V100、V100S、A10、A100、atlas 300i pro、mlu370-s4，支持类型会随着功能升级增加
    gpuCount: Any = None  # GPU数目
    gpuVendor: Optional[str] = None  # GPU名称
    videoMemSize: Any = None  # 显存大小

    @staticmethod
    def from_json(json_data: dict) -> Optional['CtecsDescribeInstancesReturnObjResultsFlavorResponse']:
        if not json_data:
            return None
        obj = CtecsDescribeInstancesReturnObjResultsFlavorResponse(
            flavorID=json_data.get('flavorID'),
            flavorName=json_data.get('flavorName'),
            flavorCPU=json_data.get('flavorCPU'),
            flavorRAM=json_data.get('flavorRAM'),
            gpuType=json_data.get('gpuType'),
            gpuCount=json_data.get('gpuCount'),
            gpuVendor=json_data.get('gpuVendor'),
            videoMemSize=json_data.get('videoMemSize'),
        )
        return obj


@dataclass
class CtecsDescribeInstancesReturnObjResultsImageResponse:
    imageID: Optional[str] = None  # 镜像ID
    imageName: Optional[str] = None  # 镜像名称

    @staticmethod
    def from_json(json_data: dict) -> Optional['CtecsDescribeInstancesReturnObjResultsImageResponse']:
        if not json_data:
            return None
        obj = CtecsDescribeInstancesReturnObjResultsImageResponse(
            imageID=json_data.get('imageID'),
            imageName=json_data.get('imageName'),
        )
        return obj


@dataclass
class CtecsDescribeInstancesReturnObjResultsAffinityGroupResponse:
    policy: Optional[str] = None  # 云主机组策略
    affinityGroupName: Optional[str] = None  # 云主机组名称
    affinityGroupID: Optional[str] = None  # 云主机组ID

    @staticmethod
    def from_json(json_data: dict) -> Optional['CtecsDescribeInstancesReturnObjResultsAffinityGroupResponse']:
        if not json_data:
            return None
        obj = CtecsDescribeInstancesReturnObjResultsAffinityGroupResponse(
            policy=json_data.get('policy'),
            affinityGroupName=json_data.get('affinityGroupName'),
            affinityGroupID=json_data.get('affinityGroupID'),
        )
        return obj


@dataclass
class CtecsDescribeInstancesReturnObjResultsVipInfoListResponse:
    vipID: Optional[str] = None  # 虚拟IP的ID
    vipAddress: Optional[str] = None  # 虚拟IP地址
    vipBindNicIP: Optional[str] = None  # 虚拟IP绑定的网卡对应IPv4地址
    vipBindNicIPv6: Optional[str] = None  # 虚拟IP绑定的网卡对应IPv6地址
    nicID: Optional[str] = None  # 网卡ID

    @staticmethod
    def from_json(json_data: dict) -> Optional['CtecsDescribeInstancesReturnObjResultsVipInfoListResponse']:
        if not json_data:
            return None
        obj = CtecsDescribeInstancesReturnObjResultsVipInfoListResponse(
            vipID=json_data.get('vipID'),
            vipAddress=json_data.get('vipAddress'),
            vipBindNicIP=json_data.get('vipBindNicIP'),
            vipBindNicIPv6=json_data.get('vipBindNicIPv6'),
            nicID=json_data.get('nicID'),
        )
        return obj


@dataclass
class CtecsDescribeInstancesReturnObjResultsSecGroupListResponse:
    securityGroupID: Optional[str] = None  # 安全组ID
    securityGroupName: Optional[str] = None  # 安全组名称

    @staticmethod
    def from_json(json_data: dict) -> Optional['CtecsDescribeInstancesReturnObjResultsSecGroupListResponse']:
        if not json_data:
            return None
        obj = CtecsDescribeInstancesReturnObjResultsSecGroupListResponse(
            securityGroupID=json_data.get('securityGroupID'),
            securityGroupName=json_data.get('securityGroupName'),
        )
        return obj


@dataclass
class CtecsDescribeInstancesReturnObjResultsAddressesResponse:
    vpcName: Optional[str] = None  # vpc名称
    addressList: Optional[List[Optional[CtecsDescribeInstancesReturnObjResultsAddressesAddressListResponse]]] = None  # 网络地址列表

    @staticmethod
    def from_json(json_data: dict) -> Optional['CtecsDescribeInstancesReturnObjResultsAddressesResponse']:
        if not json_data:
            return None
        obj = CtecsDescribeInstancesReturnObjResultsAddressesResponse(
            vpcName=json_data.get('vpcName'),
            addressList=get_response_attributes(json_data, "addressList", CtecsDescribeInstancesReturnObjResultsAddressesAddressListResponse),
        )
        return obj


@dataclass
class CtecsDescribeInstancesReturnObjResultsResponse:
    projectID: Optional[str] = None  # 企业项目ID
    azName: Optional[str] = None  # 可用区名称
    azDisplayName: Optional[str] = None  # 可用区展示名称
    attachedVolume: Optional[List[Optional[str]]] = None  # 云硬盘ID列表
    addresses: Optional[List[Optional[CtecsDescribeInstancesReturnObjResultsAddressesResponse]]] = None  # 网络地址信息
    instanceID: Optional[str] = None  # 云主机ID
    displayName: Optional[str] = None  # 云主机显示名称
    instanceName: Optional[str] = None  # 云主机名称
    osType: Any = None  # 操作系统类型，详见枚举值表
    instanceStatus: Optional[str] = None  # 云主机状态，取值范围：<br />backuping: 备份中，<br />creating: 创建中，<br />expired: 已到期，<br />freezing: 已冻结，<br />rebuild: 重装，<br />restarting: 重启中，<br />running: 运行中，<br />starting: 开机中，<br />stopped: 已关机，<br />stopping: 关机中，<br />error: 错误，<br />snapshotting: 快照创建中，<br />unsubscribed: 包周期已退订，<br />unsubscribing: 包周期退订中。
    expiredTime: Optional[str] = None  # 到期时间
    createdTime: Optional[str] = None  # 创建时间
    secGroupList: Optional[List[Optional[CtecsDescribeInstancesReturnObjResultsSecGroupListResponse]]] = None  # 安全组信息列表
    vipInfoList: Optional[List[Optional[CtecsDescribeInstancesReturnObjResultsVipInfoListResponse]]] = None  # 虚拟IP信息列表
    affinityGroup: Optional[CtecsDescribeInstancesReturnObjResultsAffinityGroupResponse]  = None # 云主机组信息
    image: Optional[CtecsDescribeInstancesReturnObjResultsImageResponse] = None  # 镜像信息
    flavor: Optional[CtecsDescribeInstancesReturnObjResultsFlavorResponse] = None  # 云主机规格信息
    onDemand: Optional[bool] = None  # 付费方式，取值范围：<br />true（按量付费），<br />false（包周期）
    keypairName: Optional[str] = None  # 密钥对名称
    networkInfo: Optional[List[Optional[CtecsDescribeInstancesReturnObjResultsNetworkInfoResponse]]] = None  # 网络信息
    delegateName: Optional[str] = None  # 委托名称，注：委托绑定目前仅支持多可用区类型资源池，非可用区资源池为空字符串
    deletionProtection: Optional[bool] = None  # 是否开启实例删除保护
    instanceDescription: Optional[str] = None  # 云主机描述信息
    pciInfo: Optional[CtecsDescribeInstancesReturnObjResultsPciInfoResponse] = None  # pci地址信息，注：仅多可用区类型资源池返回；该字段内测中

    @staticmethod
    def from_json(json_data: dict) -> Optional['CtecsDescribeInstancesReturnObjResultsResponse']:
        if not json_data:
            return None

        obj = CtecsDescribeInstancesReturnObjResultsResponse(
            projectID=json_data.get('projectID'),
            azName=json_data.get('azName'),
            azDisplayName=json_data.get('azDisplayName'),
            attachedVolume=json_data.get('attachedVolume'),
            addresses=get_response_attributes(json_data, "addresses", CtecsDescribeInstancesReturnObjResultsAddressesResponse),
            instanceID=json_data.get('instanceID'),
            displayName=json_data.get('displayName'),
            instanceName=json_data.get('instanceName'),
            osType=json_data.get('osType'),
            instanceStatus=json_data.get('instanceStatus'),
            expiredTime=json_data.get('expiredTime'),
            createdTime=json_data.get('createdTime'),
            secGroupList=get_response_attributes(json_data, "secGroupList", CtecsDescribeInstancesReturnObjResultsSecGroupListResponse),
            vipInfoList=get_response_attributes(json_data, "vipInfoList", CtecsDescribeInstancesReturnObjResultsVipInfoListResponse),
            affinityGroup=get_response_attributes(json_data, "affinityGroup", CtecsDescribeInstancesReturnObjResultsAffinityGroupResponse),
            image=get_response_attributes(json_data, "image", CtecsDescribeInstancesReturnObjResultsImageResponse),
            flavor=get_response_attributes(json_data, "flavor", CtecsDescribeInstancesReturnObjResultsFlavorResponse),
            onDemand=json_data.get('onDemand'),
            keypairName=json_data.get('keypairName'),
            networkInfo=get_response_attributes(json_data, "networkInfo", CtecsDescribeInstancesReturnObjResultsNetworkInfoResponse),
            delegateName=json_data.get('delegateName'),
            deletionProtection=json_data.get('deletionProtection'),
            instanceDescription=json_data.get('instanceDescription'),
            pciInfo=get_response_attributes(json_data, "pciInfo", CtecsDescribeInstancesReturnObjResultsPciInfoResponse),
        )
        return obj

@dataclass
class CtecsDescribeInstancesReturnObjResponse:
    currentCount: Any = None  # 当前页记录数目
    totalCount: Any = None  # 总记录数
    totalPage: Any = None  # 总页数
    results: Optional[List[Optional[CtecsDescribeInstancesReturnObjResultsResponse]]] = None  # 分页明细

    @staticmethod
    def from_json(json_data: dict) -> Optional['CtecsDescribeInstancesReturnObjResponse']:
        if not json_data:
            return None

        obj = CtecsDescribeInstancesReturnObjResponse(
            currentCount=json_data.get('currentCount'),
            totalCount=json_data.get('totalCount'),
            totalPage=json_data.get('totalPage'),
            results=get_response_attributes(json_data, "results", CtecsDescribeInstancesReturnObjResultsResponse),
        )
        return obj


@dataclass
class CtecsDescribeInstancesResponse:
    statusCode: Any = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 英文描述信息
    description: Optional[str] = None  # 中文描述信息
    returnObj: Optional[CtecsDescribeInstancesReturnObjResponse] = None  # 成功时返回的数据

    @staticmethod
    def from_json(json_data: dict) -> Optional['CtecsDescribeInstancesResponse']:
        if not json_data:
            return None

        obj = CtecsDescribeInstancesResponse(
            statusCode=json_data.get('statusCode'),
            errorCode=json_data.get('errorCode'),
            error=json_data.get('error'),
            message=json_data.get('message'),
            description=json_data.get('description'),
            returnObj=get_response_attributes(json_data, "returnObj", CtecsDescribeInstancesReturnObjResponse),
        )
        return obj


# 该接口提供用户多台云主机信息查询功能，用户可以根据此接口的返回值得到多台云主机信息。该接口相较于/v4/ecs/list-instances提供更精简的云主机信息，拥有更高的查找效率<br /><b>准备工作：</b><br />&emsp;&emsp;构造请求：在调用前需要了解如何构造请求，详情查看<a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=%u6784%u9020%u8BF7%u6C42&data=87&vid=81">构造请求</a><br />&emsp;&emsp;认证鉴权：openapi请求需要进行加密调用，详细查看<a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=%u8BA4%u8BC1%u9274%u6743&data=87&vid=81">认证鉴权</a><br /><b>注意事项：</b><br />&emsp;&emsp;分页查询：当前查询结果以分页形式进行展示，单次查询最多显示50条数据<br />&emsp;&emsp;匹配查找：可以通过部分字段进行匹配筛选数据，无符合条件的为空，在指定多台云主机ID的情况下，只返回匹配到的云主机信息。推荐每次使用单个条件查找
class CtecsDescribeInstancesApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtecsDescribeInstancesRequest) -> CtecsDescribeInstancesResponse:
        url = endpoint + "/v4/ecs/describe-instances"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtecsDescribeInstancesResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
