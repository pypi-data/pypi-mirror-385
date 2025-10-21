from ctyunsdk_ecs20220909.core.client import CtyunClient
from ctyunsdk_ecs20220909.core.credential import Credential
from ctyunsdk_ecs20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, fields
from typing import Optional, List, Any


@dataclass
class CtecsQueryProductsInRegionV41Request:
    regionID: str  # 资源池ID

    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if v is not None}


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjAzListDetailsStorageTypeResponse:
    type: Optional[str] = None  # 存储类型
    name: Optional[str] = None  # 类型名称

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsQueryProductsInRegionV41ReturnObjAzListDetailsStorageTypeResponse':
        if not json_data:
            return cls()

        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}

        return cls(**filtered_data)


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjAzListDetailsResponse:
    """可用区详细信息"""
    storageType: Optional[
        List[Optional[CtecsQueryProductsInRegionV41ReturnObjAzListDetailsStorageTypeResponse]]] = None  # 不同az可用区的存储类型

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsQueryProductsInRegionV41ReturnObjAzListDetailsResponse':
        if not json_data:
            return cls()

        storage_type = [CtecsQueryProductsInRegionV41ReturnObjAzListDetailsStorageTypeResponse.from_json(item) for item
                        in json_data.get('storageType', [])]
        return cls(
            storageType=storage_type
        )


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjEbsStorageTypeList:
    """ebs云产品"""
    type: Optional[str] = None
    name: Optional[str] = None

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsQueryProductsInRegionV41ReturnObjEbsStorageTypeList':
        if not json_data:
            return cls()

        return cls(
            type=json_data.get("type"),
            name=json_data.get("name")
        )


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjEbs:
    """ebs云产品"""
    storageType: Optional[list[CtecsQueryProductsInRegionV41ReturnObjEbsStorageTypeList]] = None
    hasBks: Optional[str] = None
    hasEbsKms: Optional[str] = None
    hasEbsFromBks: Optional[str] = None
    hasEbsFromBksFlag: Optional[str] = None
    hasISCSI: Optional[str] = None
    hasFCSAN: Optional[str] = None
    shareEbs: Optional[str] = None
    hasVolumeSpeedLimit: Optional[str] = None
    upgradeSysVolume: Optional[str] = None
    HasVolumePool: Optional[str] = None
    hasEbsSnapshot: Optional[str] = None
    hasAutoSnapPolicy: Optional[str] = None
    hasEbsUpdateDisk: Optional[str] = None

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsQueryProductsInRegionV41ReturnObjEbs':
        if not json_data:
            return cls()

        storage_type = None
        if json_data.get('storageType') is not None:
            storage_type = [CtecsQueryProductsInRegionV41ReturnObjEbsStorageTypeList.from_json(item) for item in
                            json_data.get('storageType', [])]
        return cls(
            storageType=storage_type,
            hasBks=json_data.get("hasBks"),
            hasEbsKms=json_data.get("hasEbsKms"),
            hasEbsFromBks=json_data.get("hasEbsFromBks"),
            hasEbsFromBksFlag=json_data.get("hasEbsFromBksFlag"),
            hasISCSI=json_data.get("hasISCSI"),
            hasFCSAN=json_data.get("hasFCSAN"),
            shareEbs=json_data.get("shareEbs"),
            hasVolumeSpeedLimit=json_data.get("hasVolumeSpeedLimit"),
            upgradeSysVolume=json_data.get("upgradeSysVolume"),
            HasVolumePool=json_data.get("HasVolumePool"),
            hasEbsSnapshot=json_data.get("hasEbsSnapshot"),
            hasAutoSnapPolicy=json_data.get("hasAutoSnapPolicy"),
            hasEbsUpdateDisk=json_data.get("hasEbsUpdateDisk")
        )


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjEcsFlavorTypes:
    """ecs云产品"""
    s: Optional[list[str]] = None
    m: Optional[list[str]] = None
    c: Optional[list[str]] = None
    hs: Optional[list[str]] = None
    hc: Optional[list[str]] = None
    hm: Optional[list[str]] = None
    fs: Optional[list[str]] = None
    fc: Optional[list[str]] = None
    fm: Optional[list[str]] = None
    kc: Optional[list[str]] = None
    km: Optional[list[str]] = None
    ks: Optional[list[str]] = None
    g: Optional[list[str]] = None
    p: Optional[list[str]] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjEcsFlavorTypes']:
        if not json_data:
            return cls()

        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}

        return cls(**filtered_data)


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjEcs:
    """ecs云产品"""
    hasGroup: Optional[str] = None
    hasCloneVM: Optional[str] = None
    hasCloneVMNew: Optional[str] = None
    hasAdvancedConfiguration: Optional[str] = None
    hasCreateVMByBackup: Optional[str] = None
    hasCsbs: Optional[str] = None
    hasSnapshot: Optional[str] = None
    hasAddNic: Optional[str] = None
    hasChangeNetwork: Optional[str] = None
    hasChangeV6Network: Optional[str] = None
    hasVnc: Optional[str] = None
    vmVncDomainName: Optional[str] = None
    hasS2M2: Optional[str] = None
    hasS6: Optional[str] = None
    hasS7: Optional[str] = None
    flavorTypes: Optional[CtecsQueryProductsInRegionV41ReturnObjEcsFlavorTypes] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjEcs']:
        if not json_data:
            return cls()

        return cls(
            hasGroup=json_data.get("hasGroup"),
            hasCloneVM=json_data.get("hasCloneVM"),
            hasCloneVMNew=json_data.get("hasCloneVMNew"),
            hasAdvancedConfiguration=json_data.get("hasAdvancedConfiguration"),
            hasCreateVMByBackup=json_data.get("hasCreateVMByBackup"),
            hasCsbs=json_data.get("hasCsbs"),
            hasSnapshot=json_data.get("hasSnapshot"),
            hasAddNic=json_data.get("hasAddNic"),
            hasChangeNetwork=json_data.get("hasChangeNetwork"),
            hasChangeV6Network=json_data.get("hasChangeV6Network"),
            hasVnc=json_data.get("hasVnc"),
            vmVncDomainName=json_data.get("vmVncDomainName"),
            hasS2M2=json_data.get("hasS2M2"),
            hasS6=json_data.get("hasS6"),
            hasS7=json_data.get("hasS7"),
            flavorTypes=CtecsQueryProductsInRegionV41ReturnObjEcsFlavorTypes.from_json(json_data.get('flavorTypes'))
        )


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjPm:
    """pm云产品"""
    pm: Optional[str] = None
    PmVnc: Optional[str] = None
    pmVncDomainName: Optional[str] = None
    hasPmChangeVpc: Optional[str] = None
    hasPmGpu: Optional[str] = None
    hasPMMultiNic: Optional[str] = None
    hasPmAdaptation: Optional[str] = None
    hasPmKeypair: Optional[str] = None
    hasPmBindNic: Optional[str] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjPm']:
        if not json_data:
            return cls()

        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}

        return cls(**filtered_data)


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjImage:
    selectionImage: Optional[str] = None
    shareImage: Optional[str] = None
    safeImage: Optional[str] = None
    hasMakeDiskImage: Optional[str] = None
    hasExportDiskImage: Optional[str] = None
    hasPrivateImageExport: Optional[str] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjImage']:
        if not json_data:
            return cls()

        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}

        return cls(**filtered_data)


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjMonitor:
    hasMonitor: Optional[str] = None
    hasAuditLog: Optional[str] = None
    hasChMonitor: Optional[str] = None
    hasEipMonitor: Optional[str] = None
    hasV6NicMonitor: Optional[str] = None
    hasFGMonitor: Optional[str] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjMonitor']:
        if not json_data:
            return cls()

        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}

        return cls(**filtered_data)


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjOss:
    hasMakeImageByOss: Optional[str] = None
    hasOss: Optional[str] = None
    hasOssKms: Optional[str] = None
    hasOSSWebSite: Optional[str] = None
    hasOssServerOpen: Optional[str] = None
    hasOssVpc: Optional[str] = None
    hasOssResource: Optional[str] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjOss']:
        if not json_data:
            return cls()

        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}

        return cls(**filtered_data)


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjPaas:
    PaaSPayAsYouGoProducts: Optional[str] = None
    PaasUpgradeProducts: Optional[str] = None
    aiPaasContentdetection: Optional[str] = None
    aiPaasFacedetection: Optional[str] = None
    dataPaasMapreduce: Optional[str] = None
    dataPaasMapreduceUrl: Optional[str] = None
    dbPaasDrds: Optional[str] = None
    dbPaasDrdsUrl: Optional[str] = None
    dbPaasHbase: Optional[str] = None
    dbPaasHbaseUrl: Optional[str] = None
    dbPaasMemcache: Optional[str] = None
    dbPaasMemcacheUrl: Optional[str] = None
    dbPaasMongodb: Optional[str] = None
    dbPaasMongodbUrl: Optional[str] = None
    dbPaasPgsql: Optional[str] = None
    dbPaasPgsqlUrl: Optional[str] = None
    dbPaasRds: Optional[str] = None
    dbPaasRdsUrl: Optional[str] = None
    dbPaasRedis: Optional[str] = None
    dbPaasRedisUrl: Optional[str] = None
    dbPaasTsdb: Optional[str] = None
    dbPaasTsdbUrl: Optional[str] = None
    middlewarePaasKafka: Optional[str] = None
    middlewarePaasKafkaUrl: Optional[str] = None
    middlewarePaasMq: Optional[str] = None
    middlewarePaasMqUrl: Optional[str] = None
    middlewarePaasMqtt: Optional[str] = None
    middlewarePaasMqttUrl: Optional[str] = None
    middlewarePaasRabbit: Optional[str] = None
    middlewarePaasRabbitUrl: Optional[str] = None
    paasApiUrl: Optional[str] = None
    paasCidr: Optional[str] = None
    paasProZone: Optional[str] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjPaas']:
        if not json_data:
            return cls()

        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}

        return cls(**filtered_data)


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjCaas:
    computedCaas: Optional[str] = None
    computedCaasUrl: Optional[str] = None
    computedCce: Optional[str] = None
    computedCceUrl: Optional[str] = None
    computedCcr: Optional[str] = None
    computedCcrUrl: Optional[str] = None
    caasApiUrl: Optional[str] = None
    caasShareNetworkId: Optional[str] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjCaas']:
        if not json_data:
            return cls()

        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}

        return cls(**filtered_data)


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjHpc:
    computedHpc: Optional[str] = None
    computedHpcUrl: Optional[str] = None
    hpcApiUrl: Optional[str] = None
    hpcShareNetworkId: Optional[str] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjHpc']:
        if not json_data:
            return cls()

        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}

        return cls(**filtered_data)


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjSdwan:
    hasSdwan: Optional[str] = None
    hasSdwanIpv6: Optional[str] = None
    hasQos: Optional[str] = None
    sdwanQlinksSafeFw: Optional[str] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjSdwan']:
        if not json_data:
            return cls()

        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}

        return cls(**filtered_data)


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjOrder:
    hasAutoRenew: Optional[str] = None
    hasAutoRevoke: Optional[str] = None
    billingByQuantity: Optional[str] = None
    ctcsVmBind: Optional[str] = None
    hasCycleTerminate: Optional[str] = None
    hasRecoveredOrder: Optional[str] = None
    supportDownConfig: Optional[str] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjOrder']:
        if not json_data:
            return cls()

        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}

        return cls(**filtered_data)


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjVpc:
    dns1: Optional[str] = None
    dns2: Optional[str] = None
    getguestcidr6suffix: Optional[str] = None
    hasV6Nic: Optional[str] = None
    hasV6NicMonitor: Optional[str] = None
    hasVPCRouter: Optional[str] = None
    hasVPN: Optional[str] = None
    hasVirtualIp: Optional[str] = None
    hasSharedBw: Optional[str] = None
    hasNat: Optional[str] = None
    ipv6: Optional[str] = None
    hasP2P: Optional[str] = None
    shareNetworkId: Optional[str] = None
    subnetPoolId: Optional[str] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjVpc']:
        if not json_data:
            return cls()

        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}

        return cls(**filtered_data)


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjLb:
    hasElb: Optional[str] = None
    hasElbPG: Optional[str] = None
    hasElbBA: Optional[str] = None
    subnetOfferingIdWithInternalLb: Optional[str] = None
    subnetOfferingIdWithInternalLbNosnat: Optional[str] = None
    subnetOfferingIdWithLb: Optional[str] = None
    subnetOfferingIdWithLbNosnat: Optional[str] = None
    hasLBSupportSession: Optional[str] = None
    hasListenerOnHttps: Optional[str] = None
    hasListenerOnHttp: Optional[str] = None
    hasElbCert: Optional[str] = None
    hasElbSubnetIpv6: Optional[str] = None
    hasElbListenerHttpRedirect: Optional[str] = None
    hasElbHttp2: Optional[str] = None
    hasElbCustomTimeout: Optional[str] = None
    hasElbCrossVpc: Optional[str] = None
    hasKeepSession: Optional[str] = None
    hasElbAddEcmGroup: Optional[str] = None
    hasElbProtocolProto: Optional[str] = None
    hasElbProtocolPort: Optional[str] = None
    hasElbClientRealSourceIp: Optional[str] = None
    hasElbPgHigh2: Optional[str] = None
    hasElbPgSupper1: Optional[str] = None
    hasElbPgSupper2: Optional[str] = None
    hasElbPackYearDiscount: Optional[str] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjLb']:
        if not json_data:
            return cls()

        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}

        return cls(**filtered_data)


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjScaling:
    hasEss: Optional[str] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjScaling']:
        if not json_data:
            return cls()

        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}

        return cls(**filtered_data)


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjEip:
    hasPayByTraffic: Optional[str] = None
    hasEipMonitor: Optional[str] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjEip']:
        if not json_data:
            return cls()

        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}

        return cls(**filtered_data)


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjSfs:
    fileSystem: Optional[str] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjSfs']:
        if not json_data:
            return cls()

        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}

        return cls(**filtered_data)


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjSaas:
    middlewareSaasServicestage: Optional[str] = None
    middlewareSaasServicestageUrl: Optional[str] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjSaas']:
        if not json_data:
            return cls()

        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}

        return cls(**filtered_data)


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjDec:
    hasDec: Optional[str] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjDec']:
        if not json_data:
            return cls()

        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}

        return cls(**filtered_data)


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjCh:
    hasCh: Optional[str] = None
    hasChMonitor: Optional[str] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjCh']:
        if not json_data:
            return cls()

        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}

        return cls(**filtered_data)


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjCnssl:
    hasCnssl: Optional[str] = None
    hasCnsslEdgeActiveStandby: Optional[str] = None
    hasCnsslOrderFee: Optional[str] = None
    hasCnsslLineSafeguard: Optional[str] = None
    hasCnsslOrderFeeSafeguard: Optional[str] = None
    hasCnsslOverviewMapview: Optional[str] = None
    hasCnsslLineOnlineDnat: Optional[str] = None
    hasCnsslLineSecure: Optional[str] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjCnssl']:
        if not json_data:
            return cls()

        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}

        return cls(**filtered_data)


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjSecuritySafe:
    securitySafe: Optional[str] = None
    securitySafeUrl: Optional[str] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjSecuritySafe']:
        if not json_data:
            return cls()

        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}

        return cls(**filtered_data)


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjRds:
    rdsStorage: Optional[str] = None
    rdsStorageType: Optional[str] = None
    hasFixedVIP4RDS: Optional[str] = None
    hasRDSReadnode: Optional[str] = None  # 是否RDS支持只读实例
    hasRDSReadNode: Optional[str] = None  # 兼容hasRDSReadnode，目前无法使用
    hasRDSZOS: Optional[str] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjRds']:
        if not json_data:
            return cls()

        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}

        return cls(**filtered_data)


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjKms:
    hasKms: Optional[str] = None
    hasKmsServer: Optional[str] = None
    hasEfsKms: Optional[str] = None
    hasOssKms: Optional[str] = None
    hasEbsKms: Optional[str] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjKms']:
        if not json_data:
            return cls()

        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}

        return cls(**filtered_data)


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjAcl:
    hasAcl: Optional[str] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjAcl']:
        if not json_data:
            return cls()

        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}

        return cls(**filtered_data)


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjCda:
    hasCda: Optional[str] = None
    hasCda2: Optional[str] = None
    hasCdaMonitor: Optional[str] = None
    hasCdaPermission: Optional[str] = None
    hasCdaGrant: Optional[str] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjCda']:
        if not json_data:
            return cls()

        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}

        return cls(**filtered_data)


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjEfs:
    hasEfsPermission: Optional[str] = None
    hasEfsKms: Optional[str] = None
    hasEfsPay: Optional[str] = None
    hasEfsIpv6: Optional[str] = None
    hasEfsV6Tip: Optional[str] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjEfs']:
        if not json_data:
            return cls()

        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}

        return cls(**filtered_data)


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjOther:
    GPU: Optional[str] = None
    hasMetalSubnet: Optional[str] = None
    hasPmForceStop: Optional[str] = None
    hasPmForceRestart: Optional[str] = None
    hasPmDesc: Optional[str] = None
    hasPmUserData: Optional[str] = None
    hasPmEditProps: Optional[str] = None
    setDiskReleaseWithPm: Optional[str] = None
    hasPmPayOnDemand: Optional[str] = None
    hasMetalIms: Optional[str] = None
    hasClonePm: Optional[str] = None
    computedServerless: Optional[str] = None
    cutover: Optional[str] = None
    dtpApiUrl: Optional[str] = None
    eLoadBalance: Optional[str] = None
    hasBackupUsedSize: Optional[str] = None
    hasEfsKms: Optional[str] = None
    hasEfsPay: Optional[str] = None
    hasMaintenanceLog: Optional[str] = None
    hasMultiCidr4VPC: Optional[str] = None
    hasPps: Optional[str] = None
    hasSMSAlarm: Optional[str] = None
    hasShoppingCart: Optional[str] = None
    hasTranscoding: Optional[str] = None
    hbaseApiUrl: Optional[str] = None
    hostGroupAdjustable: Optional[str] = None
    lat: Optional[str] = None
    lng: Optional[str] = None
    mapReduceShareNetworkId: Optional[str] = None
    mqttInternetAbility: Optional[str] = None
    mrApiUrl: Optional[str] = None
    resourceSoldout: Optional[str] = None
    userRole: Optional[str] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjOther']:
        if not json_data:
            return cls()

        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}

        return cls(**filtered_data)


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjAzListDetailsStorageType:
    type: Optional[str] = None
    name: Optional[str] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjAzListDetailsStorageType']:
        if not json_data:
            return cls()

        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in json_data.items() if k in valid_fields}

        return cls(**filtered_data)


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjAzListDetails:
    storageType: Optional[list[CtecsQueryProductsInRegionV41ReturnObjAzListDetailsStorageType]] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjAzListDetails']:
        if not json_data:
            return cls()
        return cls(
            storageType=[CtecsQueryProductsInRegionV41ReturnObjAzListDetailsStorageType.from_json(item) for item in json_data.get("storageType", [])]
        )


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjAzListDetailsStorageType:
    type: Optional[str] = None
    name: Optional[str] = None

    @classmethod
    def from_json(cls, json_data: dict) -> Optional['CtecsQueryProductsInRegionV41ReturnObjAzListDetailsStorageType']:
        if not json_data:
            return cls()
        return cls(
            type=json_data.get("type"),
            name=json_data.get("name")
        )

@dataclass
class CtecsQueryProductsInRegionV41ReturnObjAzList:
    """az分区信息"""
    azName: Optional[str] = None  # 可用区名称
    azDisplayName: Optional[str] = None  # 可用区展示名
    details: Optional[CtecsQueryProductsInRegionV41ReturnObjAzListDetails] = None  # 可用区详细信息

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsQueryProductsInRegionV41ReturnObjAzList':
        if not json_data:
            return cls()

        return cls(
            azName=json_data.get("azName"),
            azDisplayName=json_data.get("azDisplayName"),
            details=CtecsQueryProductsInRegionV41ReturnObjAzListDetails.from_json(json_data.get("details"))
        )


@dataclass
class CtecsQueryProductsInRegionV41ReturnObjResponse:
    """返回参数"""
    ebs: Optional[CtecsQueryProductsInRegionV41ReturnObjEbs] = None
    ecs: Optional[CtecsQueryProductsInRegionV41ReturnObjEcs] = None
    pm: Optional[CtecsQueryProductsInRegionV41ReturnObjPm] = None
    image: Optional[CtecsQueryProductsInRegionV41ReturnObjImage] = None
    vpc: Optional[CtecsQueryProductsInRegionV41ReturnObjVpc] = None
    monitor: Optional[CtecsQueryProductsInRegionV41ReturnObjMonitor] = None
    oss: Optional[CtecsQueryProductsInRegionV41ReturnObjOss] = None
    paas: Optional[CtecsQueryProductsInRegionV41ReturnObjPaas] = None
    saas: Optional[CtecsQueryProductsInRegionV41ReturnObjSaas] = None
    caas: Optional[CtecsQueryProductsInRegionV41ReturnObjCaas] = None
    hpc: Optional[CtecsQueryProductsInRegionV41ReturnObjHpc] = None
    sdwan: Optional[CtecsQueryProductsInRegionV41ReturnObjSdwan] = None
    order: Optional[CtecsQueryProductsInRegionV41ReturnObjOrder] = None
    lb: Optional[CtecsQueryProductsInRegionV41ReturnObjLb] = None
    scaling: Optional[CtecsQueryProductsInRegionV41ReturnObjScaling] = None
    eip: Optional[CtecsQueryProductsInRegionV41ReturnObjEip] = None
    sfs: Optional[CtecsQueryProductsInRegionV41ReturnObjSfs] = None
    dec: Optional[CtecsQueryProductsInRegionV41ReturnObjDec] = None
    ch: Optional[CtecsQueryProductsInRegionV41ReturnObjCh] = None
    securitySafe: Optional[CtecsQueryProductsInRegionV41ReturnObjSecuritySafe] = None
    cnssl: Optional[CtecsQueryProductsInRegionV41ReturnObjCnssl] = None
    rds: Optional[CtecsQueryProductsInRegionV41ReturnObjRds] = None
    kms: Optional[CtecsQueryProductsInRegionV41ReturnObjKms] = None
    acl: Optional[CtecsQueryProductsInRegionV41ReturnObjAcl] = None
    cda: Optional[CtecsQueryProductsInRegionV41ReturnObjCda] = None
    efs: Optional[CtecsQueryProductsInRegionV41ReturnObjEfs] = None
    other: Optional[CtecsQueryProductsInRegionV41ReturnObjOther] = None
    azList: Optional[List[CtecsQueryProductsInRegionV41ReturnObjAzList]] = None

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsQueryProductsInRegionV41ReturnObjResponse':
        if not json_data:
            return cls()

        def safe_parse(field: str, target_cls: type) -> Optional[Any]:
            return target_cls.from_json(json_data.get(field, {})) if json_data.get(field) else None

        az_list =  None
        if json_data.get('azList'):
            az_list = [CtecsQueryProductsInRegionV41ReturnObjAzList.from_json(az) for az in json_data.get('azList')]

        return cls(
            ebs=safe_parse('ebs', CtecsQueryProductsInRegionV41ReturnObjEbs),
            ecs=safe_parse('ecs', CtecsQueryProductsInRegionV41ReturnObjEcs),
            pm=safe_parse('pm', CtecsQueryProductsInRegionV41ReturnObjPm),
            image=safe_parse('image', CtecsQueryProductsInRegionV41ReturnObjImage),
            vpc=safe_parse('vpc', CtecsQueryProductsInRegionV41ReturnObjVpc),
            monitor=safe_parse('monitor', CtecsQueryProductsInRegionV41ReturnObjMonitor),
            oss=safe_parse('oss', CtecsQueryProductsInRegionV41ReturnObjOss),
            paas=safe_parse('paas', CtecsQueryProductsInRegionV41ReturnObjPaas),
            saas=safe_parse('saas', CtecsQueryProductsInRegionV41ReturnObjSaas),
            caas=safe_parse('caas', CtecsQueryProductsInRegionV41ReturnObjCaas),
            hpc=safe_parse('hpc', CtecsQueryProductsInRegionV41ReturnObjHpc),
            sdwan=safe_parse('sdwan', CtecsQueryProductsInRegionV41ReturnObjSdwan),
            order=safe_parse('order', CtecsQueryProductsInRegionV41ReturnObjOrder),
            lb=safe_parse('lb', CtecsQueryProductsInRegionV41ReturnObjLb),
            scaling=safe_parse('scaling', CtecsQueryProductsInRegionV41ReturnObjScaling),
            eip=safe_parse('eip', CtecsQueryProductsInRegionV41ReturnObjEip),
            sfs=safe_parse('sfs', CtecsQueryProductsInRegionV41ReturnObjSfs),
            dec=safe_parse('dec', CtecsQueryProductsInRegionV41ReturnObjDec),
            ch=safe_parse('ch', CtecsQueryProductsInRegionV41ReturnObjCh),
            securitySafe=safe_parse('securitySafe', CtecsQueryProductsInRegionV41ReturnObjSecuritySafe),
            cnssl=safe_parse('cnssl', CtecsQueryProductsInRegionV41ReturnObjCnssl),
            rds=safe_parse('rds', CtecsQueryProductsInRegionV41ReturnObjRds),
            kms=safe_parse('kms', CtecsQueryProductsInRegionV41ReturnObjKms),
            acl=safe_parse('acl', CtecsQueryProductsInRegionV41ReturnObjAcl),
            cda=safe_parse('cda', CtecsQueryProductsInRegionV41ReturnObjCda),
            efs=safe_parse('efs', CtecsQueryProductsInRegionV41ReturnObjEfs),
            other=safe_parse('other', CtecsQueryProductsInRegionV41ReturnObjOther),
            azList=az_list
        )

@dataclass
class CtecsQueryProductsInRegionV41Response:
    statusCode: int  # 返回状态码(800为成功，900为失败)
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: str = ""  # 失败时的错误描述(英文)
    description: str = ""  # 失败时的错误描述(中文)
    returnObj: Optional[CtecsQueryProductsInRegionV41ReturnObjResponse] = None  # 返回参数
    error: Optional[str] = None  # 错误码，请求成功时不返回

    @classmethod
    def from_json(cls, json_data: dict) -> 'CtecsQueryProductsInRegionV41Response':
        if not json_data:
            raise ValueError("JSON data cannot be empty")

        return_obj = None
        if 'returnObj' in json_data and json_data['returnObj'] is not None:
            return_obj = CtecsQueryProductsInRegionV41ReturnObjResponse.from_json(json_data['returnObj'])

        return cls(
            statusCode=json_data.get('statusCode'),
            errorCode=json_data.get('errorCode'),
            message=json_data.get('message', ''),
            description=json_data.get('description', ''),
            returnObj=return_obj,
            error=json_data.get('error')
        )


# 查询一个资源池支持的云产品信息列表，以及云产品的产品特性信息。
class CtecsQueryProductsInRegionV41Api:
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
           request: CtecsQueryProductsInRegionV41Request) -> CtecsQueryProductsInRegionV41Response:
        try:
            url = f"{endpoint}/v4/region/get-products"
            params = request.to_dict()
            response = client.get(
                url=url,
                params=params,
                credential=credential
            )
            return CtecsQueryProductsInRegionV41Response.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(f"API请求失败: {str(e)}")
