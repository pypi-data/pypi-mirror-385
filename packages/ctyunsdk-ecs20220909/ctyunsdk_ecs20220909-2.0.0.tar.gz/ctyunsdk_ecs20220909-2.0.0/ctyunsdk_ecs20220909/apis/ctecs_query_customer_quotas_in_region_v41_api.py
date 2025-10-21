from typing import Optional
from dataclasses import dataclass, fields
from ctyunsdk_ecs20220909.core.client import CtyunClient
from ctyunsdk_ecs20220909.core.credential import Credential
from ctyunsdk_ecs20220909.core.exception import CtyunRequestException


@dataclass
class CtecsQueryCustomerQuotasInRegionV41Request:
    """请求参数类"""
    regionID: str  # 资源池ID(必填)

    def to_dict(self) -> dict:
        """转换为请求参数字典"""
        return {k: v for k, v in vars(self).items() if v is not None}


@dataclass
class CtecsQueryCustomerQuotasInRegionV41ReturnObjGlobalQuotaResponse:
    """全局配额信息"""
    global_public_ip_limit: Optional[int] = None  # 弹性公网IP个数上限

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsQueryCustomerQuotasInRegionV41ReturnObjGlobalQuotaResponse':
        """从JSON数据创建全局配额对象"""
        if not json_data:
            return cls()
        return cls(
            global_public_ip_limit=json_data.get("global_public_ip_limit")
        )

@dataclass
class CtecsQueryCustomerQuotasInRegionV41ReturnObjQuotasResponse:
    """本资源池配额信息(完整版)"""
    network_acl_limit: Optional[int] = None  # ACL规则个数
    dr_client_limit: Optional[int] = None  # 单用户单个资源池客户端数
    ch_create_limit: Optional[int] = None  # 创建云间高速默认配额
    ch_create_net_manage_limit: Optional[int] = None  # 创建云网关默认配额
    ch_netmanagement_vpc_limit: Optional[int] = None  # vpc网络实例默认配额
    ch_netmanagement_cda_limit: Optional[int] = None  # cda网络实例默认配额
    ch_netmanagement_accountvpc_limit: Optional[int] = None  # 授权vpc网络实例默认配额
    ch_reconsitution_accredit_limit: Optional[int] = None  # 云间高速跨账号授权配额上限
    ch_create_route_limit: Optional[int] = None  # 云间高速路由管理创建自定义路由表配额上限
    ch_cda_subnet_limit: Optional[int] = None  # 云间高速cda子网选择上限配额
    ch_create_route_num_limit: Optional[int] = None  # 云间高速路由条目配额
    ch_vpc_subnet_limit: Optional[int] = None  # 云间高速vpc子网选择上限配额
    ch_vpc_instance_bind_limit: Optional[int] = None  # 单个vpc被相同云间高速加载次数
    ch_order_bandwidth_num_limit_v2: Optional[int] = None  # 云间高速购买带宽包个数上限2.0
    ch_order_bandwidth_limit_v2: Optional[int] = None  # 云间高速2.0订单带宽值上限
    elb_cidr_policy_limit: Optional[int] = None  # 负载均衡访问策略组配额
    elb_cidr_ip_count_limit: Optional[int] = None  # 访问策略组IP地址数量
    nic_relate_security_group_limit: Optional[int] = None  # 网卡可绑定的安全组数量上限
    ssl_vpn_server_limit: Optional[int] = None  # ssl服务端默认配额
    ssl_vpn_client_limit: Optional[int] = None  # ssl客户端默认配额
    snap_volume_limit: Optional[int] = None  # 快照创建云硬盘个数
    ssl_vpn_gate_count_limit: Optional[int] = None  # sslvpn网关个数上限
    sfs_oceanfs_volume_limit: Optional[int] = None  # 海量文件系统总容量上限(TB)
    sfs_oceanfs_count_limit: Optional[int] = None  # 海量文件系统个数上限
    sfs_hpfs_volume_limit: Optional[int] = None  # 并行文件系统总容量上限(TB)
    sfs_hpfs_count_limit: Optional[int] = None  # 并行文件系统个数上限
    cbr_ecs_limit: Optional[int] = None  # 云备份客户端配额
    cbr_vault_limit: Optional[int] = None  # 云备份存储库配额
    vip_limit: Optional[int] = None  # 单用户单资源池可创建虚拟IP个数
    vpc_create_vip_limit: Optional[int] = None  # 单VPC支持创建的VIP数量
    public_ip_cn2_limit: Optional[int] = None  # cn2列表
    rules_limit_of_per_security_group: Optional[int] = None  # 单安全组的规则个数上限
    public_ip_v6_limit: Optional[int] = None  # ipv6带宽的个数上限
    max_capacity_of_disk_creation_cs: Optional[int] = None  # 单块磁盘创建时的最大容量-CS(GB)
    disk_backup_capacity_limit: Optional[int] = None  # 云硬盘备份容量上限-OS(GB)
    storage_limit: Optional[int] = None  # 存储总容量上限(GB)
    network_limit_each_vpc: Optional[int] = None  # 单个VPC下子网个数上限-CS
    load_balancer_limit_each_ip_os: Optional[int] = None  # 单个负载均衡下的监听器个数上限-OS
    monitoring_item_limit: Optional[int] = None  # 单个监控视图下的监控项个数上限
    monitor_alerm_rules_limit: Optional[int] = None  # 告警规则个数上限
    vm_limit_each_load_balancer_os: Optional[int] = None  # 单个监听器下可绑定的主机个数上限
    network_limit_each_vpc_os: Optional[int] = None  # 单个VPC下的子网个数上限-OS
    pm_limit_per_platform: Optional[int] = None  # 单资源池下物理机个数上限
    snapshot_limit_per_cloud_server_os: Optional[int] = None  # 单台云服务器快照上限-OS
    max_duration_of_elastic_ip_creation: Optional[str] = None  # 创建弹性IP可选的最大时长(年)
    vpc_limit_os: Optional[int] = None  # VPC上限-OS
    memory_limit: Optional[int] = None  # 内存上限(GB)
    max_bandwidth_of_elastic_ip_creation: Optional[int] = None  # 创建弹性IP时的带宽上限
    network_cards_limit: Optional[int] = None  # 单个主机网卡个数上限
    private_image_limit: Optional[int] = None  # 私有镜像上限-CS
    snapshot_limit_os: Optional[int] = None  # 快照个数上限-OS
    vm_limit_each_time: Optional[int] = None  # 单次创建云主机个数上限
    vpc_limit: Optional[int] = None  # VPC上限-CS
    pm_mem_total_limit_per_platform: Optional[int] = None  # 单资源池物理机内存总额上限
    load_balancer_limit_each_ip: Optional[int] = None  # 单个负载均衡下监听器个数上限-CS
    volume_limit_each_time: Optional[int] = None  # 单次创建磁盘个数上限
    load_balancer_limit: Optional[int] = None  # 负载均衡个数上限-CS
    disk_backup_amount_limit: Optional[int] = None  # 云硬盘备份的数量上限-OS
    max_capacity_of_disk_creation_os: Optional[int] = None  # 创建单块磁盘时最大容量-OS
    key_pair_limit: Optional[int] = None  # 密匙对上限
    max_duration_of_host_creation: Optional[str] = None  # 创建主机时可选的最大时长(年)
    security_group_rules_limit: Optional[int] = None  # 安全组规则个数上限
    pm_cpu_total_limit_per_platform: Optional[int] = None  # 单资源池物理机CPU总配额
    max_duration_of_disk_product_creation: Optional[str] = None  # 磁盘产品创建时可选最大时长(年)
    max_capacity_of_sys_disk_creation_os: Optional[int] = None  # 创建系统盘时可选的最大容量-OS(GB)
    snapshot_limit_per_cloud_server: Optional[int] = None  # 单台云服务器快照个数上限-cs
    network_acl_limit_os: Optional[int] = None  # ACL规则个数上限-OS
    volume_limit_each_vm: Optional[int] = None  # 单台云主机可挂载磁盘块数上限
    volume_size_limit: Optional[int] = None  # 磁盘总容量上限(GB)
    snapshot_limit: Optional[int] = None  # 快照总个数上限-CS
    public_ip_limit_each_time: Optional[int] = None  # 单次创建公网IP个数上限
    private_image_limit_os: Optional[int] = None  # 私有镜像上限-OS
    load_balancer_limit_os: Optional[int] = None  # 负载均衡个数上限-OS
    volume_size_lower_limit: Optional[int] = None  # 单块磁盘创建时可选的最小容量(GB)
    monitor_view_limit: Optional[int] = None  # 单个监控面板下可添加的监控视图个数上限
    vcpu_limit: Optional[int] = None  # VCPU总核数
    self_customized_alerm_model_limit: Optional[int] = None  # 自定义告警模板个数上限
    monitor_panel_limit: Optional[int] = None  # 监控面板个数上限
    vm_limit_each_load_balancer: Optional[int] = None  # 单个监听器可绑定的主机个数上限-CS
    public_ip_limit: Optional[int] = None  # 弹性公网IP个数上限
    security_groups_limit: Optional[int] = None  # 安全组个数上限
    total_volume_limit: Optional[int] = None  # 磁盘总块数
    backup_policy_limit: Optional[int] = None  # 云硬盘备份策略个数上限
    vm_limit: Optional[int] = None  # 云主机总数上限
    rule_limit_of_direction_out_per_acl_cs: Optional[int] = None  # 单ACL下出方向规则个数上限-CS
    rule_limit_of_direction_out_per_acl_os: Optional[int] = None  # 单ACL下出方向规则个数上限-OS
    rule_limit_of_direction_in_per_acl_os: Optional[int] = None  # 单ACL下入方向规则个数上限-OS
    rule_limit_of_direction_in_per_acl_cs: Optional[int] = None  # 单ACL下入方向规则个数上限-CS
    public_ip_v6_os_limit: Optional[int] = None  # ipv6带宽包上限-OS
    csbs_backup_policy_limit: Optional[int] = None  # 云主机备份策略上限
    csbs_backup_policy_instance_limit: Optional[int] = None  # 云主机备份策略绑定云主机个数上限
    csbs_backup_amount_limit: Optional[int] = None  # 云主机备份上限
    csbs_backup_amount_limit_os: Optional[int] = None  # OS资源池云主机备份上限
    csbs_backup_capacity_limit: Optional[int] = None  # 云主机备份磁盘容量上限(GB)
    csbs_backup_capacity_limit_os: Optional[int] = None  # OS资源池云主机备份磁盘容量上限(GB)
    max_count_of_nic_per_vm: Optional[int] = None  # 单台虚机可添加网卡数量上限
    max_num_of_vm_per_vip: Optional[int] = None  # 单虚IP可绑定的主机数量上限
    volume_limit_each_vm_os: Optional[int] = None  # 单台云主机可挂载磁盘块数上限-OS
    vm_group_limit: Optional[int] = None  # 云主机反亲和组个数上限
    vm_limit_per_group: Optional[int] = None  # 单个云主机反亲和组可绑定的主机数量上限
    sdwan_limit: Optional[int] = None  # sdwan总数上限
    sdwan_limit_each_edge: Optional[int] = None  # 单个sdwan可包含的翼云edge个数上限
    sdwan_limit_each_site: Optional[int] = None  # 单个sdwan可包含的站点个数上限
    edge_limit: Optional[int] = None  # edge个数上限
    site_limit: Optional[int] = None  # 站点个数上限
    share_bandwidth_count_per_user_limit: Optional[int] = None  # 单个用户可以购买的共享带宽数量
    max_duration_of_share_bandwidth_creation: Optional[str] = None  # 共享带宽产品创建的最大时长(年)
    max_num_of_share_bandwidth_per_user: Optional[int] = None  # 共享带宽产品创建的带宽最大值
    ip_count_per_share_bandwidth: Optional[int] = None  # 单个共享带宽可添加的公网 IP 最大值
    max_buckets_of_oss: Optional[int] = None  # 单个资源池下对象存储可创建的存储桶个数
    max_capacity_of_csbs_repo: Optional[int] = None  # 单个云主机备份存储库最大容量(GB)
    min_capacity_of_csbs_repo: Optional[int] = None  # 单个云主机备份存储库最小容量(GB)
    csbs_repo_limit: Optional[int] = None  # 云主机备份存储库个数
    max_duration_of_csbs_repo_creation: Optional[str] =None  # 云主机备份存储库创建的最大时长(年)
    csbs_backup_policy_repository_limit: Optional[int] = None  # 单个策略可绑定存储库上限
    scaling_group_limit: Optional[int] = None  # 弹性伸缩组上限
    scaling_config_limit: Optional[int] = None  # 弹性伸缩配置上限
    scaling_rule_limit: Optional[int] = None  # 弹性伸缩策略上限
    max_bandwidth_of_elastic_ip_v6_creation: Optional[int] = None  # 创建IPV6时的带宽上限
    site_limit_each_time: Optional[int] = None  # 单次创建站点个数上限
    address_limit: Optional[int] = None  # 收货地址个数上限
    address_limit_each_time: Optional[int] = None  # 单次创建收货地址个数上限
    sdwan_acl_limit: Optional[int] = None  # SDWAN_ACL个数上限
    sdwan_acl_rule_limit: Optional[int] = None  # SDWAN_ACL规则个数上限
    pm_create_num_limit_per_time: Optional[int] = None  # 单次物理机创建个数最大值
    p_image_share_to_others_quota: Optional[int] = None  # 私有镜像共享人数上限
    ch_network_instance_limit: Optional[int] = None  # 云间高速加载网络实例个数上限
    ch_network_instance_region_limit: Optional[int] = None  # 云间高速加载网络实例区域个数上限
    ch_limit: Optional[int] = None  # 云间高速个数上限
    siteTmpl_limit: Optional[int] = None  # 站点模板数量上限
    max_bandwidth_of_elastic_ip_creation_os: Optional[int] = None  # 创建弹性IP时的带宽上限-OS
    max_num_of_vip_per_vm: Optional[int] = None  # 单台虚机可绑定的虚IP数量上限
    sdwan_monitor_alarm_rules_limit: Optional[int] = None  # SDWAN告警规则个数上限
    max_num_of_vip_per_pm: Optional[int] = None  # 单台物理机可绑定的虚IP数量上限
    max_num_of_pm_per_vip: Optional[int] = None  # 单个虚IP可绑定的物理机数量上限
    sfs_fs_count_limit: Optional[int] = None  # 弹性文件系统个数上限
    sfs_fs_volume_limit: Optional[int] = None  # 弹性文件系统总容量上限(TB)
    sfs_fs_mount_point_count_limit: Optional[int] = None  # 弹性文件系统挂载点个数上限
    sfs_permission_group_count_limit: Optional[int] = None  # 弹性文件系统权限组个数上限
    sfs_permission_rule_count_limit: Optional[int] = None  # 弹性文件系统权限组规则个数上限
    elb_cert_limit: Optional[int] = None  # 负载均衡证书总个数
    vpc_router_limit_per_table: Optional[int] = None  # 单个VPC下路由规则个数上限
    bks_repo_limit: Optional[int] = None  # 云硬盘备份存储库个数
    max_capacity_of_bks_repo: Optional[int] = None  # 单个云硬盘备份存储库最大容量
    min_capacity_of_bks_repo: Optional[int] = None  # 单个硬盘备份存储库最小容量(GB)
    max_duration_of_bks_repo_creation: Optional[str] = None  # 云硬盘备份存储库创建的最大时长(年)
    bks_backup_policy_repository_limit: Optional[int] = None  # 单个云硬盘备份策略可绑定存储库上限
    bks_backup_policy_disk_limit: Optional[int] = None  # 云硬盘备份策略绑定云硬盘个数上限
    routing_table_limit: Optional[int] = None  # 路由表默认配额
    share_ebs_attach_count: Optional[int] = None  # 共享硬盘可配置数量
    p2p_router_count_limit_per_connection: Optional[int] = None  # 对等连接内路由数量上限
    p2p_connection_count_limit: Optional[int] = None  # 对等连接数量上限
    p2p_router_count_limit_per_batch: Optional[int] = None  # 对等连接单次创建路由数量上限
    ch_order_bandwidth_limit: Optional[int] = None  # 云间高速购买带宽包带宽值上限
    ch_order_bandwidth_num_limit: Optional[int] = None  # 云间高速购买带宽包个数上限
    oss_bucket_count_limit: Optional[int] = None  # 对象存储默认配额
    vpn_user_gate_count_limit: Optional[int] = None  # VPN用户网关个数上限
    vpn_connection_count_limit: Optional[int] = None  # VPN连接个数上限
    vpn_gate_count_limit: Optional[int] = None  # VPN网关个数上限
    route_limit_per_table: Optional[int] = None  # 路由规则
    vpce_limit_per_vpc: Optional[int] = None  # 单个VPC下终端节点个数上限
    vpce_server_limit_per_vpc: Optional[int] = None  # 单个VPC下终端服务节点个数上限
    total_traffic_mirror_limit: Optional[int] = None  # 流量镜像产品筛选条件配额
    total_traffic_session_limit: Optional[int] = None  # 流量镜像产品镜像会话配额
    volume_limit_each_vm_ElasticPM: Optional[int] = None  # 裸金属单块磁盘创建时可选的最小容量(GB)
    max_capacity_of_disk_creation_ElasticPM: Optional[int] = None  # 单块磁盘创建时的最大容量-裸金属(GB)
    cnssl_site_limit: Optional[int] = None  # 云网超级专线站点数量
    total_intranet_dns_limit: Optional[int] = None  # DNS域名配额
    max_count_of_nic_per_pm: Optional[int] = None  # 单台物理机可添加网卡数量上限
    cnssl_physicsLine_route_limit: Optional[int] = None  # SD-WANoe0 0i
    snapshot_policy_limit: Optional[int] = None  # 云主机快照策略上限
    snapshot_policy_instance_limit: Optional[int] = None  # 云主机快照策略绑定云主机上限
    cnssl_physicsLine_snat_limit: Optional[int] = None  # SD-WAN（尊享版）-物理专线SNAT数量
    cnssl_physicsLine_dnat_limit: Optional[int] = None  # SD-WAN（尊享版）-物理专线DNAT数量
    cnssl_physicsLine_vpc_limit: Optional[int] = None  # SD-WAN（尊享版）-物理专线入云数量
    cnssl_route_ip_limit: Optional[int] = None  # SD-WAN（尊享版）-客户侧路由ipv4个数限制
    cnssl_edge_route_limit: Optional[int] = None  # SD-WAN（尊享版）-智能网关-路由数量
    cnssl_edge_vpc_limit: Optional[int] = None  # SD-WAN（尊享版）-智能网关-入云限制数量
    cnssl_edge_subnet_limit: Optional[int] = None  # SD-WAN（尊享版）-智能网关-子网IP限制数量
    cnssl_physicsLine_app_vpc_limit: Optional[int] = None  # SD-WAN（尊享版）-物理专线应用保障添加VPC数量
    load_balancer_policy_limit_per_listener: Optional[int] = None  # 单个监听器下创建的负载均衡转发策略上限
    edge_limit_each_pnet: Optional[int] = None  # 单个edge下可配置子网数量
    sdwan_qos_rule_limt: Optional[int] = None  # sdwan下Qos规则数量
    sdwan_qos_rule_group_limt: Optional[int] = None  # sdwan下Qos规则下五元组数量
    sdwan_qos_limit: Optional[int] = None  # sdwan下的qos数量
    sdwan_edge_mpls_ip_limit: Optional[int] = None  # sdwan下edge的过载保护目标检测ip数量上限
    sfs_single_fs_volume_limit: Optional[int] = None  # 单个弹性文件系统容量上限(TB)
    sfs_single_exclusive_fs_volume_limit: Optional[int] = None  # 单个专属型文件系统容量上限
    max_duration_of_host_new_creation: Optional[str] = None # 创建非GPU主机时可选的最大时长(年)
    max_duration_of_network_creation: Optional[str] =None  # 创建VPN和文件系统时可选的最大时长(年)
    sdwan_edge_static_router_limit: Optional[int] = None  # sdwan下单个edge里可创建的静态路由数量


    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsQueryCustomerQuotasInRegionV41ReturnObjQuotasResponse':
        """从JSON数据创建配额对象
        参数: json_data: 包含配额信息的JSON数据
        返回: 初始化后的配额对象
        异常: ValueError: 当json_data为空时抛出
        """
        if not json_data:
            return cls()

        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}

        return cls(**filtered_data)

@dataclass
class CtecsQueryCustomerQuotasInRegionV41ReturnObjResponse:
    """返回参数"""
    quotas: Optional[CtecsQueryCustomerQuotasInRegionV41ReturnObjQuotasResponse]  # 本资源池配额信息
    global_quota: Optional[CtecsQueryCustomerQuotasInRegionV41ReturnObjGlobalQuotaResponse]  # 全局配额信息

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsQueryCustomerQuotasInRegionV41ReturnObjResponse':
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        return cls(
            quotas=CtecsQueryCustomerQuotasInRegionV41ReturnObjQuotasResponse.from_json(json_data.get('quotas')),
            global_quota=CtecsQueryCustomerQuotasInRegionV41ReturnObjGlobalQuotaResponse.from_json(json_data.get('global_quota'))
        )

@dataclass
class CtecsQueryCustomerQuotasInRegionV41Response:
    statusCode: int  # 返回状态码(800为成功，900为失败)
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: str = ""  # 失败时的错误描述(英文)
    description: str = ""  # 失败时的错误描述(中文)
    returnObj: Optional[CtecsQueryCustomerQuotasInRegionV41ReturnObjResponse] = None  # 返回参数
    error: Optional[str] = None  # 错误码，请求成功时不返回

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsQueryCustomerQuotasInRegionV41Response':
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        return_obj = None
        if 'returnObj' in json_data and json_data['returnObj'] is not None:
            return_obj = CtecsQueryCustomerQuotasInRegionV41ReturnObjResponse.from_json(json_data['returnObj'])

        return cls(
            statusCode=json_data.get('statusCode'),
            errorCode=json_data.get('errorCode'),
            message=json_data.get('message', ''),
            description=json_data.get('description', ''),
            returnObj=return_obj,
            error=json_data.get('error')
        )


class CtecsQueryCustomerQuotasInRegionV41Api:
    """查询客户配额API

    功能：根据regionID查询用户配额
    接口文档：/v4/region/customer-quotas
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
           request: CtecsQueryCustomerQuotasInRegionV41Request) -> 'CtecsQueryCustomerQuotasInRegionV41Response':
        """执行API请求"""
        try:
            url = f"{endpoint}/v4/region/customer-quotas"
            params = request.to_dict()
            response = client.get(
                url=url,
                params=params,
                credential=credential
            )
            return CtecsQueryCustomerQuotasInRegionV41Response.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(f"API请求失败: {str(e)}")
