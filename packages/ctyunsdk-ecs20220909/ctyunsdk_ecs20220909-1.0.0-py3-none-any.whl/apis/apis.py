from typing import Optional
from core.client import CtyunClient
from .ctecs_check_demand_in_region_v41_api import CtecsCheckDemandInRegionV41Api
from .ctecs_get_ecs_flavors_api import CtecsGetEcsFlavorsApi
from .ctecs_query_job_info_v41_api import CtecsQueryJobInfoV41Api
from .ctecs_query_new_order_price_v41_api import CtecsQueryNewOrderPriceV41Api
from .ctecs_query_new_order_price_v42_api import CtecsQueryNewOrderPriceV42Api
from .ctecs_query_order_uuid_v41_api import CtecsQueryOrderUuidV41Api
from .ctecs_query_renew_order_price_v41_api import CtecsQueryRenewOrderPriceV41Api
from .ctecs_query_upgrade_order_price_v41_api import CtecsQueryUpgradeOrderPriceV41Api
from .ctecs_query_customer_quotas_in_region_v41_api import CtecsQueryCustomerQuotasInRegionV41Api
from .ctecs_query_customer_resources_in_region_v41_api import CtecsQueryCustomerResourcesInRegionV41Api
from .ctecs_query_products_in_region_v41_api import CtecsQueryProductsInRegionV41Api
from .ctecs_query_summary_in_region_v41_api import CtecsQuerySummaryInRegionV41Api
from .ctecs_query_zones_in_region_v41_api import CtecsQueryZonesInRegionV41Api
from .ctecs_list_regions_v41_api import CtecsListRegionsV41Api
from .ctecs_query_renew_order_price_v42_api import CtecsQueryRenewOrderPriceV42Api
from .ctecs_query_upgrade_order_price_v42_api import CtecsQueryUpgradeOrderPriceV42Api
from .ctecs_create_keypair_v41_api import CtecsCreateKeypairV41Api
from .ctecs_delete_keypair_v41_api import CtecsDeleteKeypairV41Api
from .ctecs_details_keypair_v41_api import CtecsDetailsKeypairV41Api
from .ctecs_import_keypair_v41_api import CtecsImportKeypairV41Api
from .ctecs_instance_detach_keypair_v41_api import CtecsInstanceDetachKeypairV41Api
from .ctecs_keypair_attach_instance_v41_api import CtecsKeypairAttachInstanceV41Api
from .ctecs_reboot_instance_v41_api import CtecsRebootInstanceV41Api
from .ctecs_rebuild_instance_v41_api import CtecsRebuildInstanceV41Api
from .ctecs_reset_instance_password_v41_api import CtecsResetInstancePasswordV41Api
from .ctecs_resubscribe_instance_v41_api import CtecsResubscribeInstanceV41Api
from .ctecs_start_instance_v41_api import CtecsStartInstanceV41Api
from .ctecs_stop_instance_v41_api import CtecsStopInstanceV41Api
from .ctecs_update_ecs_label_v41_api import CtecsUpdateEcsLabelV41Api
from .ctecs_update_flavor_spec_v41_api import CtecsUpdateFlavorSpecV41Api
from .ctecs_update_keypair_v41_api import CtecsUpdateKeypairV41Api
from .ctecs_describe_instances_api import CtecsDescribeInstancesApi
from .ctecs_create_instance_v41_api import CtecsCreateInstanceV41Api
from .ctecs_query_instance_statistics_v41_api import CtecsQueryInstanceStatisticsV41Api
from .ctecs_update_instance_v41_api import CtecsUpdateInstanceV41Api
from .ctecs_delete_instance_and_related_resource_api import CtecsDeleteInstanceAndRelatedResourceApi
from .ctecs_destroy_instance_api import CtecsDestroyInstanceApi

ENDPOINT_NAME = "ctecs"


class Apis:
    _ctecsgetecsflavorsapi: CtecsGetEcsFlavorsApi
    _ctecsqueryjobinfov41api: CtecsQueryJobInfoV41Api
    _ctecsqueryneworderpricev41api: CtecsQueryNewOrderPriceV41Api
    _ctecsqueryneworderpricev42api: CtecsQueryNewOrderPriceV42Api
    _ctecsqueryorderuuidv41api: CtecsQueryOrderUuidV41Api
    _ctecsqueryreneworderpricev41api: CtecsQueryRenewOrderPriceV41Api
    _ctecsqueryupgradeorderpricev41api: CtecsQueryUpgradeOrderPriceV41Api
    _ctecsquerycustomerquotasinregionv41api: CtecsQueryCustomerQuotasInRegionV41Api
    _ctecsquerycustomerresourcesinregionv41api: CtecsQueryCustomerResourcesInRegionV41Api
    _ctecsqueryproductsinregionv41api: CtecsQueryProductsInRegionV41Api
    _ctecsquerysummaryinregionv41api: CtecsQuerySummaryInRegionV41Api
    _ctecsqueryzonesinregionv41api: CtecsQueryZonesInRegionV41Api
    _ctecslistregionsv41api: CtecsListRegionsV41Api
    _ctecsqueryreneworderpricev42api: CtecsQueryRenewOrderPriceV42Api
    _ctecsqueryupgradeorderpricev42api: CtecsQueryUpgradeOrderPriceV42Api
    _ctecscheckdemandinregionv41api: CtecsCheckDemandInRegionV41Api
    _ctecscreatekeypairv41api: CtecsCreateKeypairV41Api
    _ctecsdeletekeypairv41api: CtecsDeleteKeypairV41Api
    _ctecsdetailskeypairv41api: CtecsDetailsKeypairV41Api
    _ctecsimportkeypairv41api: CtecsImportKeypairV41Api
    _ctecsinstancedetachkeypairv41api: CtecsInstanceDetachKeypairV41Api
    _ctecskeypairattachinstancev41api: CtecsKeypairAttachInstanceV41Api
    _ctecsrebootinstancev41api: CtecsRebootInstanceV41Api
    _ctecsrebuildinstancev41api: CtecsRebuildInstanceV41Api
    _ctecsresetinstancepasswordv41api: CtecsResetInstancePasswordV41Api
    _ctecsresubscribeinstancev41api: CtecsResubscribeInstanceV41Api
    _ctecsstartinstancev41api: CtecsStartInstanceV41Api
    _ctecsstopinstancev41api: CtecsStopInstanceV41Api
    _ctecsupdateecslabelv41api: CtecsUpdateEcsLabelV41Api
    _ctecsupdateflavorspecv41api: CtecsUpdateFlavorSpecV41Api
    _ctecsupdatekeypairv41api: CtecsUpdateKeypairV41Api
    _ctecsdescribeinstancesapi: CtecsDescribeInstancesApi
    _ctecscreatekeypairv41api: CtecsCreateInstanceV41Api
    _ctecsqueryupgradeorderpricev42api: CtecsQueryInstanceStatisticsV41Api
    _ctecsupdateinstancev41api: CtecsUpdateInstanceV41Api
    _ctecsdeleteinstanceandrelatedresourceapi: CtecsDeleteInstanceAndRelatedResourceApi
    _ctecsdestroyinstanceapi: CtecsDestroyInstanceApi

    def __init__(self, endpoint_url: str, client: Optional[CtyunClient] = None):
        self.client = client or CtyunClient()
        self.endpoint = endpoint_url

        self._ctecsqueryjobinfov41api = CtecsQueryJobInfoV41Api(self.client)
        self._ctecsqueryjobinfov41api.set_endpoint(self.endpoint)
        self._ctecsqueryneworderpricev41api = CtecsQueryNewOrderPriceV41Api(self.client)
        self._ctecsqueryneworderpricev41api.set_endpoint(self.endpoint)
        self._ctecsqueryneworderpricev42api = CtecsQueryNewOrderPriceV42Api(self.client)
        self._ctecsqueryneworderpricev42api.set_endpoint(self.endpoint)
        self._ctecsqueryorderuuidv41api = CtecsQueryOrderUuidV41Api(self.client)
        self._ctecsqueryorderuuidv41api.set_endpoint(self.endpoint)
        self._ctecsqueryreneworderpricev41api = CtecsQueryRenewOrderPriceV41Api(self.client)
        self._ctecsqueryreneworderpricev41api.set_endpoint(self.endpoint)
        self._ctecsqueryupgradeorderpricev41api = CtecsQueryUpgradeOrderPriceV41Api(self.client)
        self._ctecsqueryupgradeorderpricev41api.set_endpoint(self.endpoint)
        self._ctecsquerycustomerquotasinregionv41api = CtecsQueryCustomerQuotasInRegionV41Api(self.client)
        self._ctecsquerycustomerquotasinregionv41api.set_endpoint(self.endpoint)
        self._ctecsquerycustomerresourcesinregionv41api = CtecsQueryCustomerResourcesInRegionV41Api(self.client)
        self._ctecsquerycustomerresourcesinregionv41api.set_endpoint(self.endpoint)
        self._ctecsqueryproductsinregionv41api = CtecsQueryProductsInRegionV41Api(self.client)
        self._ctecsqueryproductsinregionv41api.set_endpoint(self.endpoint)
        self._ctecsquerysummaryinregionv41api = CtecsQuerySummaryInRegionV41Api(self.client)
        self._ctecsquerysummaryinregionv41api.set_endpoint(self.endpoint)
        self._ctecsqueryzonesinregionv41api = CtecsQueryZonesInRegionV41Api(self.client)
        self._ctecsqueryzonesinregionv41api.set_endpoint(self.endpoint)
        self._ctecslistregionsv41api = CtecsListRegionsV41Api(self.client)
        self._ctecslistregionsv41api.set_endpoint(self.endpoint)
        self._ctecsqueryreneworderpricev42api = CtecsQueryRenewOrderPriceV42Api(self.client)
        self._ctecsqueryreneworderpricev42api.set_endpoint(self.endpoint)
        self._ctecsqueryupgradeorderpricev42api = CtecsQueryUpgradeOrderPriceV42Api(self.client)
        self._ctecsqueryupgradeorderpricev42api.set_endpoint(self.endpoint)
        self._ctecscheckdemandinregionv41api = CtecsCheckDemandInRegionV41Api(self.client)
        self._ctecscheckdemandinregionv41api.set_endpoint(self.endpoint)
        self._ctecsgetecsflavorsapi = CtecsGetEcsFlavorsApi(self.client)
        self._ctecsgetecsflavorsapi.set_endpoint(self.endpoint)
        self._ctecscreatekeypairv41api = CtecsCreateKeypairV41Api(self.client)
        self._ctecscreatekeypairv41api.set_endpoint(self.client)
        self._ctecsdeletekeypairv41api = CtecsDeleteKeypairV41Api(self.client)
        self._ctecsdeletekeypairv41api.set_endpoint(self.client)
        self._ctecsdetailskeypairv41api = CtecsDetailsKeypairV41Api(self.client)
        self._ctecsdetailskeypairv41api.set_endpoint(self.client)
        self._ctecsimportkeypairv41api = CtecsImportKeypairV41Api(self.client)
        self._ctecsimportkeypairv41api.set_endpoint(self.client)
        self._ctecsinstancedetachkeypairv41api = CtecsInstanceDetachKeypairV41Api(self.client)
        self._ctecsinstancedetachkeypairv41api.set_endpoint(self.client)
        self._ctecskeypairattachinstancev41api = CtecsKeypairAttachInstanceV41Api(self.client)
        self._ctecskeypairattachinstancev41api.set_endpoint(self.client)
        self._ctecsrebootinstancev41api = CtecsRebootInstanceV41Api(self.client)
        self._ctecsrebootinstancev41api.set_endpoint(self.client)
        self._ctecsrebuildinstancev41api = CtecsRebuildInstanceV41Api(self.client)
        self._ctecsrebuildinstancev41api.set_endpoint(self.client)
        self._ctecsresetinstancepasswordv41api = CtecsResetInstancePasswordV41Api(self.client)
        self._ctecsresetinstancepasswordv41api.set_endpoint(self.client)
        self._ctecsresubscribeinstancev41api = CtecsResubscribeInstanceV41Api(self.client)
        self._ctecsresubscribeinstancev41api.set_endpoint(self.client)
        self._ctecsstartinstancev41api = CtecsStartInstanceV41Api(self.client)
        self._ctecsstartinstancev41api.set_endpoint(self.client)
        self._ctecsstopinstancev41api = CtecsStopInstanceV41Api(self.client)
        self._ctecsstopinstancev41api.set_endpoint(self.client)
        self._ctecsupdateecslabelv41api = CtecsUpdateEcsLabelV41Api(self.client)
        self._ctecsupdateecslabelv41api.set_endpoint(self.client)
        self._ctecsupdateflavorspecv41api = CtecsUpdateFlavorSpecV41Api(self.client)
        self._ctecsupdateflavorspecv41api.set_endpoint(self.client)
        self._ctecsupdatekeypairv41api = CtecsUpdateKeypairV41Api(self.client)
        self._ctecsupdatekeypairv41api.set_endpoint(self.client)
        self._ctecsdescribeinstancesapi = CtecsDescribeInstancesApi(self.client)
        self._ctecsdescribeinstancesapi.set_endpoint(self.client)
        self._ctecscreateinstancev41api = CtecsCreateInstanceV41Api(self.client)
        self._ctecscreateinstancev41api.set_endpoint(self.client)
        self._ctecsqueryinstancestatisticsv41api = CtecsQueryInstanceStatisticsV41Api(self.client)
        self._ctecsqueryinstancestatisticsv41api.set_endpoint(self.client)
        self._ctecsupdateinstancev41api = CtecsUpdateInstanceV41Api(self.client)
        self._ctecsupdateinstancev41api.set_endpoint(self.client)
        self._ctecsdeleteinstanceandrelatedresourceapi = CtecsDeleteInstanceAndRelatedResourceApi(self.client)
        self._ctecsdeleteinstanceandrelatedresourceapi.set_endpoint(self.client)
        self._ctecsdestroyinstanceapi = CtecsDestroyInstanceApi(self.client)
        self._ctecsdestroyinstanceapi.set_endpoint(self.client)

    @property  # noqa
    def ctecsqueryjobinfov41api(self) -> CtecsQueryJobInfoV41Api:  # noqa
        return self._ctecsqueryjobinfov41api

    @property  # noqa
    def ctecsqueryneworderpricev41api(self) -> CtecsQueryNewOrderPriceV41Api:  # noqa
        return self._ctecsqueryneworderpricev41api

    @property  # noqa
    def ctecsqueryneworderpricev42api(self) -> CtecsQueryNewOrderPriceV42Api:  # noqa
        return self._ctecsqueryneworderpricev42api

    @property  # noqa
    def ctecsqueryorderuuidv41api(self) -> CtecsQueryOrderUuidV41Api:  # noqa
        return self._ctecsqueryorderuuidv41api

    @property  # noqa
    def ctecsqueryreneworderpricev41api(self) -> CtecsQueryRenewOrderPriceV41Api:  # noqa
        return self._ctecsqueryreneworderpricev41api

    @property  # noqa
    def ctecsqueryupgradeorderpricev41api(self) -> CtecsQueryUpgradeOrderPriceV41Api:  # noqa
        return self._ctecsqueryupgradeorderpricev41api

    @property  # noqa
    def ctecsquerycustomerquotasinregionv41api(self) -> CtecsQueryCustomerQuotasInRegionV41Api:  # noqa
        return self._ctecsquerycustomerquotasinregionv41api

    @property  # noqa
    def ctecsquerycustomerresourcesinregionv41api(self) -> CtecsQueryCustomerResourcesInRegionV41Api:  # noqa
        return self._ctecsquerycustomerresourcesinregionv41api

    @property  # noqa
    def ctecsqueryproductsinregionv41api(self) -> CtecsQueryProductsInRegionV41Api:  # noqa
        return self._ctecsqueryproductsinregionv41api

    @property  # noqa
    def ctecsquerysummaryinregionv41api(self) -> CtecsQuerySummaryInRegionV41Api:  # noqa
        return self._ctecsquerysummaryinregionv41api

    @property  # noqa
    def ctecsqueryzonesinregionv41api(self) -> CtecsQueryZonesInRegionV41Api:  # noqa
        return self._ctecsqueryzonesinregionv41api

    @property  # noqa
    def ctecslistregionsv41api(self) -> CtecsListRegionsV41Api:  # noqa
        return self._ctecslistregionsv41api

    @property  # noqa
    def ctecsqueryreneworderpricev42api(self) -> CtecsQueryRenewOrderPriceV42Api:  # noqa
        return self._ctecsqueryreneworderpricev42api

    @property  # noqa
    def ctecsqueryupgradeorderpricev42api(self) -> CtecsQueryUpgradeOrderPriceV42Api:  # noqa
        return self._ctecsqueryupgradeorderpricev42api

    @property  # noqa
    def ctecscheckdemandinregionv41api(self) -> CtecsCheckDemandInRegionV41Api:  # noqa
        return self._ctecscheckdemandinregionv41api

    @property
    def ctecsgetecsflavorsapi(self) -> CtecsGetEcsFlavorsApi:  # nota
        return self._ctecsgetecsflavorsapi

    @property  # noqa
    def ctecscreatekeypairv41api(self) -> CtecsCreateKeypairV41Api:  # noqa
        return self._ctecscreatekeypairv41api

    @property  # noqa
    def ctecsdeletekeypairv41api(self) -> CtecsDeleteKeypairV41Api:  # noqa
        return self._ctecsdeletekeypairv41api

    @property  # noqa
    def ctecsdetailskeypairv41api(self) -> CtecsDetailsKeypairV41Api:  # noqa
        return self._ctecsdetailskeypairv41api

    @property  # noqa
    def ctecsimportkeypairv41api(self) -> CtecsImportKeypairV41Api:  # noqa
        return self._ctecsimportkeypairv41api

    @property  # noqa
    def ctecsinstancedetachkeypairv41api(self) -> CtecsInstanceDetachKeypairV41Api:  # noqa
        return self._ctecsinstancedetachkeypairv41api

    @property  # noqa
    def ctecskeypairattachinstancev41api(self) -> CtecsKeypairAttachInstanceV41Api:  # noqa
        return self._ctecskeypairattachinstancev41api

    @property  # noqa
    def ctecsrebootinstancev41api(self) -> CtecsRebootInstanceV41Api:  # noqa
        return self._ctecsrebootinstancev41api

    @property  # noqa
    def ctecsrebuildinstancev41api(self) -> CtecsRebuildInstanceV41Api:  # noqa
        return self._ctecsrebuildinstancev41api

    @property  # noqa
    def ctecsresetinstancepasswordv41api(self) -> CtecsResetInstancePasswordV41Api:  # noqa
        return self._ctecsresetinstancepasswordv41api

    @property  # noqa
    def ctecsresubscribeinstancev41api(self) -> CtecsResubscribeInstanceV41Api:  # noqa
        return self._ctecsresubscribeinstancev41api

    @property  # noqa
    def ctecsstartinstancev41api(self) -> CtecsStartInstanceV41Api:  # noqa
        return self._ctecsstartinstancev41api

    @property  # noqa
    def ctecsstopinstancev41api(self) -> CtecsStopInstanceV41Api:  # noqa
        return self._ctecsstopinstancev41api

    @property  # noqa
    def ctecsupdateecslabelv41api(self) -> CtecsUpdateEcsLabelV41Api:  # noqa
        return self._ctecsupdateecslabelv41api

    @property  # noqa
    def ctecsupdateflavorspecv41api(self) -> CtecsUpdateFlavorSpecV41Api:  # noqa
        return self._ctecsupdateflavorspecv41api

    @property  # noqa
    def ctecsupdatekeypairv41api(self) -> CtecsUpdateKeypairV41Api:  # noqa
        return self._ctecsupdatekeypairv41api

    @property
    def ctecsdescribeinstancesapi(self) -> CtecsDescribeInstancesApi:  # noqa
        return self._ctecsdescribeinstancesapi

    @property
    def ctecscreateinstancev41api(self) -> CtecsCreateInstanceV41Api:  # noqa
        return self._ctecscreateinstancev41api

    @property
    def ctecsqueryinstancestatisticsv41api(self) -> CtecsQueryInstanceStatisticsV41Api:  # noqa
        return self._ctecsqueryinstancestatisticsv41api

    @property
    def ctecsupdateinstancev41api(self) -> CtecsUpdateInstanceV41Api:  # noqa
        return self._ctecsupdateinstancev41api

    @property
    def ctecsdeleteinstanceandrelatedresourceapi(self) -> CtecsDeleteInstanceAndRelatedResourceApi:  # noqa
        return self._ctecsdeleteinstanceandrelatedresourceapi

    @property
    def ctecsdestroyinstanceapi(self) -> CtecsDestroyInstanceApi:  # noqa
        return self._ctecsdestroyinstanceapi