from typing import Optional, Any
from ctyunsdk_ecs20220909.core.client import CtyunClient
from ctyunsdk_ecs20220909.core.credential import Credential
from ctyunsdk_ecs20220909.core.exception import CtyunRequestException
from dataclasses import dataclass, fields


@dataclass
class CtecsQueryCustomerResourcesInRegionV41Request:
    """请求参数类"""
    regionID: str  # 资源池ID(必填)

    def to_dict(self) -> dict:
        """转换为请求参数字典，过滤None值"""
        return {k: v for k, v in vars(self).items() if v is not None}


@dataclass
class CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesCBR_VBSResponse:
    """磁盘存储备份"""
    total_count: int  # 磁盘存储备份总数
    detail_total_count: int  # 磁盘存储备份总数
    detail: Optional[dict[str, int]]  # 对应资源池id下的数量

    @classmethod
    def from_json(cls, json_data: dict):
        if not json_data:
            raise ValueError("JSON data cannot be empty")
        valid_fields = {f.name for f in fields(cls)}
        # 过滤掉无效字段
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}
        return cls(**filtered_data)


@dataclass
class CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesCERTResponse:
    """负载均衡证书"""
    total_count: int  # 负载均衡证书总数
    detail: Optional[dict[str, int]]  # 对应资源池id下的数量

    @classmethod
    def from_json(cls, json_data: dict):
        if not json_data:
            raise ValueError("JSON data cannot be empty")
        valid_fields = {f.name for f in fields(cls)}
        # 过滤掉无效字段
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}
        return cls(**filtered_data)


@dataclass
class CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesCBRResponse:
    """云主机备份"""
    total_count: int  # 云主机备份总数
    detail_total_count: int  # 云主机备份总数
    total_size: int  # 云主机备份总大小
    detail: Optional[dict[str, int]]  # 对应资源池id下的数量

    @classmethod
    def from_json(cls, json_data: dict):
        if not json_data:
            raise ValueError("JSON data cannot be empty")
        valid_fields = {f.name for f in fields(cls)}
        # 过滤掉无效字段
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}
        return cls(**filtered_data)


@dataclass
class CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesOS_BackupResponse:
    """操作系统备份"""
    total_size: int  # 固定为0
    detail_total_count: int  # 固定为0

    @classmethod
    def from_json(cls, json_data: dict):
        if not json_data:
            raise ValueError("JSON data cannot be empty")
        valid_fields = {f.name for f in fields(cls)}
        # 过滤掉无效字段
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}
        return cls(**filtered_data)


@dataclass
class CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesLOADBALANCERResponse:
    """负载均衡"""
    total_count: int  # 负载均衡总数
    detail: Optional[dict[str, int]]  # 对应资源池id下的数量

    @classmethod
    def from_json(cls, json_data: dict):
        if not json_data:
            raise ValueError("JSON data cannot be empty")
        valid_fields = {f.name for f in fields(cls)}
        # 过滤掉无效字段
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}
        return cls(**filtered_data)


@dataclass
class CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesLB_LISTENERResponse:
    """负载均衡监听器"""
    total_count: int  # 负载均衡监听器总数
    detail: Optional[dict[str, int]]  # 对应资源池id下的数量

    @classmethod
    def from_json(cls, json_data: dict):
        if not json_data:
            raise ValueError("JSON data cannot be empty")
        valid_fields = {f.name for f in fields(cls)}
        # 过滤掉无效字段
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}
        return cls(**filtered_data)


@dataclass
class CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesIMAGEResponse:
    """私有镜像"""
    total_count: int  # 私有镜像总数
    detail: Optional[dict[str, int]]  # 对应资源池id下的数量

    @classmethod
    def from_json(cls, json_data: dict):
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        valid_fields = {f.name for f in fields(cls)}
        # 过滤掉无效字段
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}
        return cls(**filtered_data)


@dataclass
class CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesIP_POOLResponse:
    """共享带宽"""
    total_count: int  # 共享带宽总数
    detail: Optional[dict[str, int]]  # 对应资源池id下的数量

    @classmethod
    def from_json(cls, json_data: dict):
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        valid_fields = {f.name for f in fields(cls)}
        # 过滤掉无效字段
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}
        return cls(**filtered_data)


@dataclass
class CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesACLLISTResponse:
    """ACL"""
    total_count: int  # ACL总数
    detail: Optional[dict[str, int]]  # 对应资源池id下的数量

    @classmethod
    def from_json(cls, json_data: dict):
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        valid_fields = {f.name for f in fields(cls)}
        # 过滤掉无效字段
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}
        return cls(**filtered_data)


@dataclass
class CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesSNAPSHOTResponse:
    """云主机快照"""
    total_count: int  # 云主机快照总数
    detail: Optional[dict[str, int]]  # 对应资源池id下的数量

    @classmethod
    def from_json(cls, json_data: dict):
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        valid_fields = {f.name for f in fields(cls)}
        # 过滤掉无效字段
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}
        return cls(**filtered_data)


@dataclass
class CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesVm_GroupResponse:
    """云主机组"""
    total_count: int  # 云主机组总数
    detail: Optional[dict[str, int]]  # 对应资源池id下的数量

    @classmethod
    def from_json(cls, json_data: dict):
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        valid_fields = {f.name for f in fields(cls)}
        # 过滤掉无效字段
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}
        return cls(**filtered_data)


@dataclass
class CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesDisk_BackupResponse:
    """磁盘备份"""
    total_count: int  # 磁盘备份总数
    detail_total_count: int  # 磁盘备份总数
    detail: Optional[dict[str, int]]  # 对应资源池id下的数量

    @classmethod
    def from_json(cls, json_data: dict):
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        valid_fields = {f.name for f in fields(cls)}
        # 过滤掉无效字段
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}
        return cls(**filtered_data)


@dataclass
class CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesNATResponse:
    """NAT"""
    total_count: int  # nat总数
    detail_total_count: int  # nat总数
    detail: Optional[dict[str, int]]  # 对应资源池id下的数量

    @classmethod
    def from_json(cls, json_data: dict):
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        valid_fields = {f.name for f in fields(cls)}
        # 过滤掉无效字段
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}
        return cls(**filtered_data)


@dataclass
class CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesBMSResponse:
    """物理机"""
    total_count: int  # 物理机总数
    detail_total_count: int  # 物理机总数
    memory_count: int  # 固定为0
    cpu_count: int  # 固定为0
    bm_shutd_count: int  # 固定为0
    expire_running_count: int  # 固定为0
    bm_running_count: int  # 固定为0
    expire_count: int  # 固定为0
    expire_shutd_count: int  # 固定为0

    @classmethod
    def from_json(cls, json_data: dict):
        if not json_data:
            raise ValueError("JSON data cannot be empty")
        valid_fields = {f.name for f in fields(cls)}
        # 过滤掉无效字段
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}
        return cls(**filtered_data)


@dataclass
class CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesPublic_IPResponse:
    """公网IP"""
    total_count: int  # 公网IP总数
    detail_total_count: int  # 公网IP总数

    @classmethod
    def from_json(cls, json_data: dict):
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        valid_fields = {f.name for f in fields(cls)}
        # 过滤掉无效字段
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}
        return cls(**filtered_data)


@dataclass
class CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesVPCResponse:
    """VPC"""
    total_count: int  # VPC总数
    detail_total_count: int  # VPC总数

    @classmethod
    def from_json(cls, json_data: dict):
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        valid_fields = {f.name for f in fields(cls)}
        # 过滤掉无效字段
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}
        return cls(**filtered_data)


@dataclass
class CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesVOLUME_SNAPSHOTResponse:
    """磁盘快照"""
    total_count: int  # 磁盘快照总数
    detail_total_count: int  # 磁盘快照总数

    @classmethod
    def from_json(cls, json_data: dict):
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        valid_fields = {f.name for f in fields(cls)}
        # 过滤掉无效字段
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}
        return cls(**filtered_data)


@dataclass
class CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesVolumeResponse:
    """磁盘"""
    vo_root_count: int  # 系统盘数量
    vo_disk_count: int  # 数据盘数量
    total_count: int  # 磁盘总数
    detail_total_count: int  # 磁盘总数
    total_size: int  # 磁盘总大小
    vo_disk_size: int  # 数据盘大小
    vo_root_size: int  # 系统盘大小

    @classmethod
    def from_json(cls, json_data: dict):
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        valid_fields = {f.name for f in fields(cls)}
        # 过滤掉无效字段
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}
        return cls(**filtered_data)


@dataclass
class CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesVMResponse:
    """云主机"""
    vm_shutd_count: int  # 已关机云主机数量
    expire_count: int  # 过期云主机数量
    expire_running_count: int  # 已过期的运行中云主机数量
    expire_shutd_count: int  # 已过期的关机云主机数量
    vm_running_count: int  # 运行中云主机数量
    total_count: int  # 云主机总数
    cpu_count: int  # CPU总数
    memory_count: int  # 总内存大小
    detail_total_count: int  # 云主机总数

    @classmethod
    def from_json(cls, json_data: dict):
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        valid_fields = {f.name for f in fields(cls)}
        # 过滤掉无效字段
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}
        return cls(**filtered_data)


@dataclass
class CtecsTrafficMirrorFlowResponse:
    """流量镜像"""
    total_count: int  # 流量镜像总数
    detail: Optional[dict[str, int]]  # 流量镜像总数

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsTrafficMirrorFlowResponse':

        valid_fields = {f.name for f in fields(cls)}
        # 过滤掉无效字段
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}
        return cls(**filtered_data)


@dataclass
class TrafficMirrorFilterResponse:
    """流量镜像过滤规则"""
    total_count: int  # 流量镜像过滤规则总数
    detail: Optional[dict[str, int]]  # 流量镜像过滤规则总数

    @classmethod
    def from_json(cls, json_data: dict) -> 'TrafficMirrorFilterResponse':

        valid_fields = {f.name for f in fields(cls)}
        # 过滤掉无效字段
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}
        return cls(**filtered_data)


@dataclass
class CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesResponse:
    """资源信息"""
    VM: Optional['CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesVMResponse'] = None  # 云主机
    Volume: Optional['CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesVolumeResponse'] = None  # 磁盘
    VOLUME_SNAPSHOT: Optional['CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesVOLUME_SNAPSHOTResponse'] = None  # 磁盘快照
    VPC: Optional['CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesVPCResponse'] = None  # VPC
    Public_IP: Optional['CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesPublic_IPResponse'] = None  # 公网IP
    BMS: Optional['CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesBMSResponse'] = None  # 物理机
    NAT: Optional['CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesNATResponse'] = None  # NAT
    Disk_Backup: Optional['CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesDisk_BackupResponse'] = None  # 磁盘备份
    Vm_Group: Optional['CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesVm_GroupResponse'] = None  # 云主机组
    SNAPSHOT: Optional['CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesSNAPSHOTResponse'] = None  # 云主机快照
    ACLLIST: Optional['CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesACLLISTResponse'] = None  # ACL
    IP_POOL: Optional['CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesIP_POOLResponse'] = None  # 共享带宽
    IMAGE: Optional['CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesIMAGEResponse'] = None  # 私有镜像
    LB_LISTENER: Optional['CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesLB_LISTENERResponse'] = None  # 负载均衡监听器
    LOADBALANCER: Optional['CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesLOADBALANCERResponse'] = None  # 负载均衡
    OS_Backup: Optional['CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesOS_BackupResponse'] = None  # 操作系统备份
    TrafficMirror_Flow: Optional['CtecsTrafficMirrorFlowResponse'] = None  # 流量镜像适配器
    TrafficMirror_Filter: Optional['TrafficMirrorFilterResponse'] = None  # 流量镜像过滤器
    CBR: Optional['CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesCBRResponse'] = None  # 云主机备份
    CERT: Optional['CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesCERTResponse'] = None  # 负载均衡证书
    CBR_VBS: Optional['CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesCBR_VBSResponse'] = None  # 磁盘存储备份

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesResponse':
        """从JSON数据创建返回对象"""
        if not json_data:
            return cls()

        def safe_parse(field: str, target_cls: type) -> Optional[Any]:
            return target_cls.from_json(json_data.get(field, {})) if json_data.get(field) else None

        return cls(
            VM=safe_parse('VM', CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesVMResponse),
            Volume=safe_parse('Volume', CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesVolumeResponse),
            VOLUME_SNAPSHOT=safe_parse('VOLUME_SNAPSHOT', CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesVOLUME_SNAPSHOTResponse),
            VPC=safe_parse('VPC', CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesVPCResponse),
            Public_IP=safe_parse('Public_IP', CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesPublic_IPResponse),
            BMS=safe_parse('BMS', CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesBMSResponse),
            NAT=safe_parse('NAT', CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesNATResponse),
            Disk_Backup=safe_parse('Disk_Backup', CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesDisk_BackupResponse),
            Vm_Group=safe_parse('Vm_Group', CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesVm_GroupResponse),
            SNAPSHOT=safe_parse('SNAPSHOT', CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesSNAPSHOTResponse),
            ACLLIST=safe_parse('ACLLIST', CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesACLLISTResponse),
            IP_POOL=safe_parse('IP_POOL', CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesIP_POOLResponse),
            IMAGE=safe_parse('IMAGE', CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesIMAGEResponse),
            LB_LISTENER=safe_parse('LB_LISTENER', CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesLB_LISTENERResponse),
            LOADBALANCER=safe_parse('LOADBALANCER', CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesLOADBALANCERResponse),
            OS_Backup=safe_parse('OS_Backup', CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesOS_BackupResponse),
            TrafficMirror_Flow=safe_parse('TrafficMirror_Flow', CtecsTrafficMirrorFlowResponse),
            TrafficMirror_Filter=safe_parse('TrafficMirror_Filter', TrafficMirrorFilterResponse),
            CBR=safe_parse('CBR', CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesCBRResponse),
            CERT=safe_parse('CERT', CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesCERTResponse),
            CBR_VBS=safe_parse('CBR_VBS', CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesCBR_VBSResponse)
        )


@dataclass
class CtecsQueryCustomerResourcesInRegionV41ReturnObjResponse:
    """返回参数"""
    resources: Optional[CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesResponse]  # 资源信息

    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsQueryCustomerResourcesInRegionV41ReturnObjResponse':
        if not json_data:
            return cls(None)

        return cls(resources=CtecsQueryCustomerResourcesInRegionV41ReturnObjResourcesResponse.from_json(json_data["resources"]))


@dataclass
class CtecsQueryCustomerResourcesInRegionV41Response:
    """API响应"""
    statusCode: int  # 返回状态码(800为成功，900为失败)
    errorCode: Optional[str] = None  # 错误码
    message: str = ""  # 错误描述(英文)
    description: str = ""  # 错误描述(中文)
    returnObj: Optional['CtecsQueryCustomerResourcesInRegionV41ReturnObjResponse'] = None  # 返回参数
    error: Optional[str] = None  # 错误码(请求成功时不返回)

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsQueryCustomerResourcesInRegionV41Response':
        """从JSON数据创建响应对象"""
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        return_obj = None
        if 'returnObj' in json_data and json_data['returnObj'] is not None:
            return_obj = CtecsQueryCustomerResourcesInRegionV41ReturnObjResponse.from_json(json_data['returnObj'])

        return cls(
            statusCode=json_data.get('statusCode'),
            errorCode=json_data.get('errorCode'),
            message=json_data.get('message', ""),
            description=json_data.get('description', ""),
            returnObj=return_obj,
            error=json_data.get('error')
        )


class CtecsQueryCustomerResourcesInRegionV41Api:
    """查询用户已有资源API

    功能：根据regionID查询用户已有资源
    接口文档：/v4/region/customer-resources
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
           request: CtecsQueryCustomerResourcesInRegionV41Request) -> CtecsQueryCustomerResourcesInRegionV41Response:
        """执行API请求"""
        try:
            url = f"{endpoint}/v4/region/customer-resources"
            params = request.to_dict()
            response = client.get(
                url=url,
                params=params,
                credential=credential
            )
            return CtecsQueryCustomerResourcesInRegionV41Response.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(f"API请求失败: {str(e)}")
