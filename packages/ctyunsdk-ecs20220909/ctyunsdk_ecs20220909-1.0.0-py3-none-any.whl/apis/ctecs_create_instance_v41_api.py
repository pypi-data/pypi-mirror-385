from typing import List, Optional, Dict, Any
from core.client import CtyunClient
from core.credential import Credential
from core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtecsCreateInstanceV41LabelListRequest:
    labelKey: str  # 标签键，长度限制1-32字符，注：同一台云主机绑定多个标签时，标签键不可重复
    labelValue: str  # 标签值，长度限制1-32字符

    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if v is not None}


@dataclass
class CtecsCreateInstanceV41DataDiskListRequest:
    diskType: str  # 云硬盘类型，取值范围：<br />SATA（普通IO），<br />SAS（高IO，只有该类型支持FCSAN模式），<br />SSD（超高IO），<br />SSD-genric（通用型SSD），<br />FAST-SSD（极速型SSD，不支持ISCSI模式），<br />XSSD-0、XSSD-1、XSSD-2（X系列云硬盘，不支持加密，不支持ISCSI模式或FCSAN模式）您可以查看<a href="https://www.ctyun.cn/document/10027696/10162918">磁盘类型及性能介绍</a>来了解磁盘类型及其对应性能指标，查看<a href="https://www.ctyun.cn/document/10027696/10179346">X系列云硬盘</a>来了解X系列云硬盘
    diskSize: Any  # 磁盘容量，单位为GB。非X系列云盘，单个数据盘取值范围：[10，32768]；X系列云盘：XSSD-0类型，单个数据盘取值范围：[10~65536]，XSSD-1类型，单个数据盘取值范围：[20~65536]，XSSD-2类型，单个数据盘取值范围：[512~65536]。您可以查看<a href="https://www.ctyun.cn/document/10027696/10027936">磁盘使用限制</a>来了解磁盘容量。
    diskMode: Optional[str] = None  # 云硬盘属性，取值范围：<br />FCSAN：光纤通道协议的SAN网络，<br />ISCSI：小型计算机系统接口，<br />VBD：虚拟块存储设备<br />您可以查看<a href="https://www.ctyun.cn/document/10027696/10162960">磁盘模式及使用方法</a><br />注：默认为VBD
    isEncrypt: Optional[bool] = None # 磁盘是否加密，取值范围：true（加密）、false（不加密），注：默认值false；若该参数为true且不填写cmkID（加密密钥ID），则使用默认密钥进行加密
    cmkID: Optional[str] = None  # 加密密钥ID，注：加密数据盘填写该参数，同时需要填写数据盘是否加密（isEncrypt） 为true；暂不支持包周期密钥
    provisionedIops: Any = None  # 磁盘类型为XSSD时，可设置盘的预配置iops值，其他类型的盘不支持设置。 当provisionedIops为0或者不传时，表示不配置iops值。当配置iops值时，最小值为1。
    diskName: Optional[str] = None  # 云硬盘名称，仅允许英文字母、数字及_或者-，长度为2-63字符，不能以特殊字符开头。<br />注：该参数在非多可用区类型资源池下无效

    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if v is not None}

@dataclass
class CtecsCreateInstanceV41NetworkCardListRequest:
    isMaster: bool  # 是否主网卡，取值范围：<br />true：表示主网卡，<br />false：表示扩展网卡<br />注：只能含有一个主网卡
    subnetID: str  # 子网ID，您可以查看<a href="https://www.ctyun.cn/document/10026755/10098380">基本概念</a>来查找子网的相关定义 <br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=18&api=8659&data=94">查询子网列表</a><br /><span style="background-color: rgb(97, 175, 254);color: rgb(255,255,255);padding: 2px; margin:2px">创</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=18&api=4812&data=94">创建子网</a><br />注：在多可用区类型资源池下，subnetID通常以“subnet-”开头，非多可用区类型资源池subnetID为uuid格式
    fixedIP: Optional[str] = None  # 内网IPv4地址，注：不可使用已占用IP

    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if v is not None}

@dataclass
class CtecsCreateInstanceV41Request:
    clientToken: str  # 客户端存根，用于保证订单幂等性。保留时间为24小时，使用同一个clientToken值，则代表为同一个请求
    regionID: str
    azName: str  # 可用区名称，您可以查看<a href="https://www.ctyun.cn/document/10026730/10028695">地域和可用区</a>来了解可用区 <br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a  href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=5855&data=87">资源池可用区查询</a><br />注：<br />1、查询结果中zoneList内返回存在可用区名称(即多可用区，本字段填写实际可用区名称)，若查询结果中zoneList为空（即为单可用区,无需填写本字段）<br />2、当多可用区时支持随机分配可用区，本字段填写random 
    instanceName: str  # 云主机名称。不同操作系统下，云主机名称规则有差异<br />Windows：长度为2-15个字符，允许使用大小写字母、数字或连字符（-）。不能以连字符（-）开头或结尾，不能连续使用连字符（-），也不能仅使用数字；<br />其他操作系统：长度为2-64字符，允许使用点（.）分隔字符成多段，每段允许使用大小写字母、数字或连字符（-），但不能连续使用点号（.）或连字符（-），不能以点号（.）或连字符（-）开头或结尾，也不能仅使用数字
    displayName: str  # 云主机显示名称，长度为2-63字符
    imageType: Any  # 镜像类型，您可以查看<a href="https://www.ctyun.cn/document/10026730/10030151">镜像概述</a>查看关于云主机镜像介绍。您可以查看<a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=23&api=4763&data=89">查询可以使用的镜像资源</a>中 imageVisibilityCode 了解具体取值范围
    imageID: str  # 镜像ID，您可以查看<a href="https://www.ctyun.cn/document/10026730/10030151">镜像概述</a>来了解云主机镜像<br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=23&api=4763&data=89">查询可以使用的镜像资源</a><br /><span style="background-color: rgb(97, 175, 254);color: rgb(255,255,255);padding: 2px; margin:2px">创</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=23&api=4765&data=89">创建私有镜像（云主机系统盘）</a><br /><span style="background-color: rgb(97, 175, 254);color: rgb(255,255,255);padding: 2px; margin:2px">创</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=23&api=5230&data=89">创建私有镜像（云主机数据盘）</a><br />注：同一镜像名称在不同资源池的镜像ID是不同的，调用前需确认镜像ID是否归属当前资源池
    bootDiskType: str  # 系统盘类型，取值范围：<br />取值范围：<br />SATA（普通IO），<br />SAS（高IO，只有该类型支持FCSAN模式），<br />SSD（超高IO），<br />SSD-genric（通用型SSD），<br />FAST-SSD（极速型SSD，不支持ISCSI模式），<br />XSSD-0、XSSD-1、XSSD-2（X系列云硬盘，不支持加密，不支持ISCSI模式或FCSAN模式）您可以查看<a href="https://www.ctyun.cn/document/10027696/10162918">磁盘类型及性能介绍</a>来了解磁盘类型及其对应性能指标，查看<a href="https://www.ctyun.cn/document/10027696/10179346">X系列云硬盘</a>来了解X系列云硬盘
    bootDiskSize: Any  # 系统盘大小单位为GiB。非X系列云盘，单个系统盘取值范围：[所选镜像大小，2048]；X系列系云盘，单个系统盘取值范围：[所选镜像大小，2048]，如果为XSSD-2类型，单个系统盘取值范围：[max(所选镜像大小，512)~2048]，您可以查看<a href="https://www.ctyun.cn/document/10027696/10027936">磁盘使用限制</a>来了解磁盘容量。<br />注：创建云主机过程中会存在单位转换，因此该参数只能传入整型，如果填写小数值则会被取整，影响到涉及计费
    bootDiskProvisionedIops: Any  # 系统盘类型为XSSD时，可设置盘的预配置iops值，其他类型的盘不支持设置。当provisionedIops为0或者不传时，表示不配置iops值。当配置iops值时，最小值为1。
    vpcID: str  # 虚拟私有云ID，您可以查看<a href="https://www.ctyun.cn/document/10026755/10028310">产品定义-虚拟私有云</a>来了解虚拟私有云<br /> 获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a  href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=18&api=4814&data=94">查询VPC列表</a><br /><span style="background-color: rgb(97, 175, 254);color: rgb(255,255,255);padding: 2px; margin:2px">创</span> <a  href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=18&api=4811&data=94">创建VPC</a><br />注：在多可用区类型资源池下，vpcID通常为“vpc-”开头，非多可用区类型资源池vpcID为uuid格式
    onDemand: bool  # 购买方式，取值范围：<br />false：按周期，<br />true：按需<br />您可以查看<a href="https://www.ctyun.cn/document/10026730/10030877">计费模式</a>了解云主机的计费模式<br />注：按周期（false）创建云主机需要同时指定cycleCount和cycleType参数
    networkCardList: List[CtecsCreateInstanceV41NetworkCardListRequest]  # 网卡信息列表，您可以查看<a href="https://www.ctyun.cn/document/10026730/10225195">弹性网卡概述</a>了解弹性网卡相关信息
    extIP: str  # 是否使用弹性公网IP，取值范围：<br />0：不使用，<br />1：自动分配，<br />2：使用已有<br />注：自动分配弹性公网，默认分配IPv4弹性公网，需填写带宽大小，如需ipv6请填写弹性IP版本（即参数extIP="1"时，需填写参数bandwidth、ipVersion，ipVersion含默认值ipv4）；<br />使用已有弹性公网，请填写弹性公网IP的ID，默认为ipv4版本，如使用已有ipv6，请填写弹性ip版本（即参数extIP="2"时，需填写eipID或ipv6AddressID，同时ipv6情况下请填写ipVersion）
    flavorName: Optional[str] = None  # 云主机规格名称，您可以查看<a href="https://www.ctyun.cn/document/10026730/10118193">规格说明</a>了解弹性云主机的选型基本信息<br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a  href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=8327&data=87">查询一个或多个云主机规格资源</a><br />注：当创建云主机随机分配可用区时，规格名称为必填项，规格ID无效。当采用确定可用区时，规格ID和规格名称两者均可使用，必填其中一个，当两个都填写以规格ID为准。
    flavorID: Optional[str] = None  # 云主机规格ID，您可以查看<a href="https://www.ctyun.cn/document/10026730/10118193">规格说明</a>了解弹性云主机的选型基本信息<br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a  href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=8327&data=87">查询一个或多个云主机规格资源</a><br />注：同一规格名称在不同资源池不同可用区的规格ID是不同的，调用前需确认规格ID是否归属当前资源池，多可用区资源池确认是否归属当前可用区
    bootDiskIsEncrypt: Optional[bool] = None  # 系统盘是否加密，取值范围：true（加密）、false（不加密），默认值false；<br />注：填写true时，若填写bootDiskCmkID值，则使用已填写的密钥，若不填写bootDiskCmkID值，则使用默认密钥加密。
    bootDiskCmkID: Optional[str] = None  # 系统盘加密密钥ID，您可以查看<a href="https://www.ctyun.cn/document/10014047/10789926">密钥管理概述</a>了解密钥<br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a  href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=7&api=5840&data=107&isNormal=1&vid=101">批量查询密钥信息</a><br />注：bootDiskCmkID与bootDiskIsEncrypt组合使用，需要填写系统盘是否加密（bootDiskIsEncrypt） 为true；暂不支持包周期密钥
    projectID: Optional[str] = None  # 企业项目ID，企业项目管理服务提供统一的云资源按企业项目管理，以及企业项目内的资源管理，成员管理。您可以通过查看<a href="https://www.ctyun.cn/document/10017248/10017961">创建企业项目</a>了解如何创建企业项目<br />注：默认值为"0"
    secGroupList: Optional[List[Optional[str]]] = None  # 安全组ID列表，您可以查看<a href="https://www.ctyun.cn/document/10026755/10028520">安全组概述</a>了解安全组相关信息 <br />获取： <br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=18&api=4817&data=94">查询用户安全组列表</a><br /><span style="background-color: rgb(97, 175, 254);color: rgb(255,255,255);padding: 2px; margin:2px">创</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=18&api=4821&data=94">创建安全组</a><br />注：在多可用区类型资源池下，安全组ID通常以“sg-”开头，非多可用区类型资源池安全组ID为uuid格式；默认使用默认安全组，无默认安全组情况下请填写该参数
    dataDiskList: Optional[List[Optional[CtecsCreateInstanceV41DataDiskListRequest]]] = None  # 数据盘信息列表，注：同一云主机下最多可挂载8块数据盘
    ipVersion: Optional[str] = None  # 弹性IP版本，取值范围：<br />ipv4：v4地址，<br />ipv6：v6地址<br />不指定默认为ipv4。注：请先确认该资源池是否支持ipv6（多可用区类资源池暂不支持）
    bandwidth: Any = None  # 带宽大小，单位为Mbit/s，取值范围：[1, 2000]
    ipv6AddressID: Optional[str] = None  # 弹性公网IPv6的ID；填写该参数时请填写ipVersion为ipv6
    eipID: Optional[str] = None  # 弹性公网IP的ID，您可以查看<a href="https://www.ctyun.cn/document/10026753/10026909">产品定义-弹性IP</a>来了解弹性公网IP <br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=18&api=8652&data=94&isNormal=1&vid=88">查询指定地域已创建的弹性 IP</a><br /><span style="background-color: rgb(97, 175, 254);color: rgb(255,255,255);padding: 2px; margin:2px">创</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=18&api=5723&data=94&vid=88">创建弹性 IP</a>
    affinityGroupID: Optional[str] = None  # 云主机组ID，获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=8324&data=87">查询云主机组列表或者详情</a><br /><span style="background-color: rgb(97, 175, 254);color: rgb(255,255,255);padding: 2px; margin:2px">创</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=8316&data=87"> 创建云主机组</a>
    keyPairID: Optional[str] = None  # 密钥对ID，您可以查看<a href="https://www.ctyun.cn/document/10026730/10230540">密钥对</a>来了解密钥对相关内容 <br />获取：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=8342&data=87">查询一个或多个密钥对</a><br /><span style="background-color: rgb(97, 175, 254);color: rgb(255,255,255);padding: 2px; margin:2px">创</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=8344&data=87">创建一对SSH密钥对</a>
    userName: Optional[str] = None  # 用户名。当操作系统为非Windows使用密码登录时，用户名取值范围：<br />root（系统超级用户），<br />ecs-user（系统普通用户），<br />注：非Windows云主机用户默认为root，该参数大小写敏感
    userPassword: Optional[str] = None  # 用户密码，满足以下规则：<br />长度在8～30个字符；<br />必须包含大写字母、小写字母、数字以及特殊符号中的三项；<br />特殊符号可选：()`-!@#$%^&*_-+=｜{}[]:;'<>,.?/且不能以斜线号 / 开头；<br />不能包含3个及以上连续字符；<br />Linux镜像不能包含镜像用户名（root）、用户名的倒序（toor）、用户名大小写变化（如RoOt、rOot等），若Linux镜像用户名为ecs-user，密码不能包含用户名(ecs-user)、用户名的倒序(resu-sce)、用户名大小写变化(如ECS-USER等)；<br />Windows镜像不能包含镜像用户名（Administrator）、用户名大小写变化（adminiSTrator等）<br />注：密码和密钥对ID，请避免同时使用，同时使用时只有绑定密钥生效
    cycleCount: Any = None  # 订购时长，该参数需要与cycleType一同使用<br />注：最长订购周期为60个月（5年）；cycleType与cycleCount一起填写；按量付费（即onDemand为true）时，无需填写该参数（填写无效）
    cycleType: Optional[str] = None  # 订购周期类型，取值范围：<br />MONTH：按月，<br />YEAR：按年<br />注：cycleType与cycleCount一起填写；按量付费（即onDemand为true）时，无需填写该参数（填写无效）
    autoRenewStatus: Any = None  # 是否自动续订，取值范围：<br />0：不续费，<br />1：自动续费<br />注：按月购买，自动续订周期为1个月；按年购买，自动续订周期为1年
    userData: Optional[str] = None  # 用户自定义数据，需要以Base64方式编码，Base64编码后的长度限制为1-16384字符
    payVoucherPrice: Any = None  # 代金券，满足以下规则：<br />两位小数，不足两位自动补0，超过两位小数无效；<br />不可为负数；<br />注：字段为0时表示不使用代金券，默认不使用
    labelList: Optional[List[Optional[CtecsCreateInstanceV41LabelListRequest]]] = None  # 标签信息列表，注：单台云主机最多可绑定10个标签；主机创建完成后，云主机变为运行状态，此时标签仍可能未绑定，需等待一段时间（0-10分钟）
    gpuDriverKits: Optional[str] = None  # GPU云主机安装驱动的工具包，仅在同时选择NVIDIA显卡、计算加速型、linux公共镜像三个条件下，支持安装驱动
    monitorService: Optional[bool] = None  # 监控参数，支持通过该参数指定云主机在创建后是否开启详细监控，取值范围： <br />false：不开启，<br />true：开启<br />若指定该参数为true或不指定该参数，云主机内默认开启最新详细监控服务<br />若指定该参数为false，默认公共镜像不开启最新监控服务；私有镜像使用镜像中保留的监控服务<br />说明：仅部分资源池支持monitorService参数，详细请参考<a href="https://www.ctyun.cn/document/10026730/10325957">监控Agent概览</a>
    instanceDescription: Optional[str] = None  # 云主机描述，限制长度为0-255个字符
    lineType: Optional[str] = None  # 弹性IP线路类型，当自动分配弹性IP时，该值生效<br />弹性IP为IPv4时，取值范围： <br />bgp_standalone：BGP多线，<br />standalone：单线-中国电信，<br />prostandalone：精品线路<br />弹性IP为IPv6时，取值范围：<br />standalone：单线-中国电信<br />默认为单线-中国电信
    demandBillingType: Optional[str] = None  # 弹性IP的计费类型，当创建按量付费云主机，且自动分配弹性IP时，该值生效。取值范围：<br />bandwidth（按带宽），<br />upflowc（按流量）。注：默认为按带宽计费，暂不支持精品线路类型指定按流量计费
    securityProduct: Optional[str] = None  # 安全防护类型，取值范围：<br />EnterpriseEdition：企业版，<br />UltimateEdition：旗舰版，<br />BasicEdition：基础版，<br />false：不开启<br />注：默认不开启
    segmentID: Optional[str] = None  # 专属eip池id（网段id）。此功能属于公测期，如果您希望试用该功能，可以提交工单申请
    threadsPerCore: Any = None  # CPU 线程数，默认值为2。取值范围：1：表示关闭 CPU 超线程，2：表示开启CPU 超线程。注：当前仅hc3、hm3规格支持设置 CPU 线程数。此功能属于公测期，如果您希望试用该功能，可以提交工单申请。关闭超线程后，部分规格的带宽、最大收发包能力达不到规格指标。

    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if v is not None}


@dataclass
class CtecsCreateInstanceV41ReturnObjResponse:
    masterOrderID: Optional[str] = None  # 主订单ID。调用方在拿到masterOrderID之后，可以使用materOrderID进一步确认订单状态及资源状态<br />查询订单状态及资源UUID：<br /><span style="background-color: rgb(73, 204, 144);color: rgb(255,255,255);padding: 2px; margin:2px">查</span> <a href="https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=25&api=9607&data=87&isNormal=1">根据masterOrderID查询云主机ID</a>
    masterOrderNO: Optional[str] = None  # 订单号
    masterResourceID: Optional[str] = None  # 主资源ID
    regionID: Optional[str] = None  # 资源池ID

    @staticmethod
    def from_json(json_data: dict) -> Optional['CtecsCreateInstanceV41ReturnObjResponse']:
        if not json_data:
            return None
        obj = CtecsCreateInstanceV41ReturnObjResponse(
            masterOrderID=json_data.get("masterOrderID"),
            masterOrderNO=json_data.get("masterOrderNO"),
            masterResourceID=json_data.get("masterResourceID"),
            regionID=json_data.get("regionID")
        )
        return obj

@dataclass
class CtecsCreateInstanceV41Response:
    statusCode: Any = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 英文描述信息
    description: Optional[str] = None  # 中文描述信息
    returnObj: Optional[CtecsCreateInstanceV41ReturnObjResponse] = None  # 成功时返回的数据

    @staticmethod
    def from_json(json_data: dict) -> Optional['CtecsCreateInstanceV41Response']:
        if not json_data:
            return None

        return_obj = None
        if "returnObj" in json_data:
            returnObj = json_data.get("returnObj")
            if returnObj is not None:
                return_obj = CtecsCreateInstanceV41ReturnObjResponse.from_json(returnObj)

        obj = CtecsCreateInstanceV41Response(
            statusCode=json_data.get("statusCode"),
            errorCode=json_data.get("errorCode"),
            error=json_data.get("error"),
            message=json_data.get("message"),
            description=json_data.get("description"),
            returnObj=return_obj,
        )
        return obj


# 支持创建一台按量付费或包年包月的云主机
class CtecsCreateInstanceV41Api:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtecsCreateInstanceV41Request) -> CtecsCreateInstanceV41Response:
        url = endpoint + "/v4/ecs/create-instance"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtecsCreateInstanceV41Response.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
