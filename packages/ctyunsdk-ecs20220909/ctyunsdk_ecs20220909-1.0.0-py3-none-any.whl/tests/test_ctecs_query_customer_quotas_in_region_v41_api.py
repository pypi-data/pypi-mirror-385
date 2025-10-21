import unittest
from unittest.mock import patch

from apis.apis import Apis
from core.client import CtyunClient
from core.credential import Credential
from core.exception import CtyunRequestException
from apis.ctecs_query_customer_quotas_in_region_v41_api import (
    CtecsQueryCustomerQuotasInRegionV41Api,
    CtecsQueryCustomerQuotasInRegionV41Request,
    CtecsQueryCustomerQuotasInRegionV41Response,
)


class TestCtecsQueryCustomerQuotasInRegionV41Api(unittest.TestCase):
    def setUp(self):
        self.client = CtyunClient()
        self.credential = Credential('<YOUR_AK>', '<YOUR_SK>')
        self.endpoint = 'https://<YOUR_ENDPOINT>'
        self.apis = Apis(self.endpoint, self.client)

    def test_request_construction(self):
        """测试请求参数构造"""
        region_id = '81f7728662dd11ec810800155d307d5b'
        request = CtecsQueryCustomerQuotasInRegionV41Request(regionID=region_id)
        self.assertEqual(request.regionID, region_id)
        self.assertEqual(request.to_dict(), {'regionID': region_id})

    def test_successful_request(self):
        """测试成功的API调用"""
        test_region_id = '81f7728662dd11ec810800155d307d5b'
        request = CtecsQueryCustomerQuotasInRegionV41Request(regionID=test_region_id)

        # 准备模拟响应
        mock_response = {
            "returnObj": {
                "global_quota": {
                    "global_ch_create_net_manage_limit": 10,
                    "test5": 6,
                    "sdwan_limit_each_cpe_client": 20,
                    "global_ch_attach_pakg_limit": 20,
                    "nic_ipv6_addr_limit": 10,
                    "global_ch_through_bandwidth_limit": 1,
                    "global_ch_trial_bandwidth_limit": 10,
                    "global_ch_traffic_mo_pkg_limit": 20,
                    "global_ch_order_bandwidth_num_limit_v2": 3,
                    "test6": 1,
                    "site_monitor_task_limit": 20,
                    "hybrid_namespace_limit": 10,
                    "global_ch_connect_service_limit": 30,
                    "hybrid_monitor_board_limit": 20,
                    "global_has_ch_need_free_pkg_type": 1,
                    "global_ch_connect_port_limit": 30,
                    "global_has_ch_cgw_need_order": 2,
                    "global_ch_trial_time_limit": 7,
                    "global_ch_order_bandwidth_limit_v2": 2000,
                    "test2": 3,
                    "global_ch_reconsitution_accredit_limit": 5,
                    "global_ch_traffic_pkg_limit": 20,
                    "testQuota3": 5,
                    "testzxh": 3,
                    "global_ch_create_limit": 10,
                    "test1122": 3,
                    "global_ch_cross_traffic_bandwidth_limit": 50,
                    "global_has_ch_need_promise_taffic": 1,
                    "global_public_ip_limit": 20,
                    "global_ch_basic_pkg_count_limit": 1,
                    "global_ch_connect_line_limit": 20,
                    "global_ch_through_create_limit": 10,
                    "global_ch_through_create_accessPoint_limit": 5,
                    "global_ch_connect_ctyun_port_limt": 1
                },
                "quotas": {
                    "50": 50,
                    "200": 200,
                    "500": 500,
                    "max_snat_num": 50,
                    "network_acl_limit": 200,
                    "sfs_hpfs_volume_limit": 100,
                    "liteecm_create_ebs_max_num": 5,
                    "cnssl_physicsLine_vpc_limit": 5,
                    "max_bandwidth_of_elastic_ip_v6_creation": 300,
                    "max_duration_of_elastic_ip_creation": "5Y",
                    "sfs_fs_cross_domain_count_limit": 5,
                    "max_bandwidth_of_elastic_ip_creation": 300,
                    "ch_create_net_manage_limit": 5,
                    "max_snat_num_private_small": 10,
                    "sdwan_monitor_alarm_rules_limit": 3,
                    "replication_policy_limit": 20,
                    "vip_limit": 550,
                    "ch_vpc_subnet_limit": 10,
                    "eni_bind_member_eni_limit": 100,
                    "max_capacity_of_disk_creation_os": 32768,
                    "replication_bind_max_repo_count": 20,
                    "public_ip_cn2_limit": 20,
                    "edge_limit_each_pnet": 20,
                    "max_num_of_vip_per_pm_port": 10,
                    "cidr_limit_per_vpc": 2,
                    "csbs_backup_policy_repository_limit": 10,
                    "ch_create_trafficRule_limit": 20,
                    "cda_vpc_bind_cloud_bgp_limit": 5,
                    "ch_order_bandwidth_num_limit_v2": 3,
                    "snap_volume_limit": 128,
                    "sdwan_inline_mode_follow_ip_limit": 5,
                    "sdwan_reconsitution_accredit_limit": 50,
                    "snapshot_policy_instance_limit": 10,
                    "private_image_limit": 10,
                    "private_image_limit_os": 10,
                    "create_ims_data_disk_limit": 1024,
                    "multicast_limit": 50,
                    "cbr_plan_limit": 20,
                    "ch_network_instance_limit": 100,
                    "dhcpConnectVpcLimit": 10,
                    "bks_backup_policy_disk_limit": 256,
                    "alarm_template_limit": 50,
                    "total_elb_gslb_limit": 10,
                    "edge_limit": 100,
                    "normalMaxBandWidth": 1000,
                    "siteTmpl_limit": 50,
                    "ch_network_instance_region_limit": 10,
                    "cdaGatewayBGPRoutePrefixLimit": 20,
                    "cda_qos_policy_limit": 50,
                    "backup_policy_limit": 20,
                    "cacheNum": 4,
                    "ecm_single_batch_turn_cycle_limit": 10,
                    "ch_order_bandwidth_limit v2": 2000,
                    "max_capacity_of_disk_creation_cs": 8192,
                    "cda_internetPublicIP_count_limit": 20,
                    "prefix_limit": 100,
                    "hybrid_prometheus_task_limit": 20,
                    "hpfs_protocol_service_count_limit": 10,
                    "eip_bind_max_num": 2,
                    "vm_limit_each_load_balancer_os": 100,
                    "max_num_of_vip_per_vm_port": 10,
                    "snapshot_limit_per_cloud_server_os": 7,
                    "dr_client_limit_max": 200,
                    "max_duration_of_efs_product_creation": "3Y",
                    "cda_dedgw_client_router_limit": 50,
                    "PathAnalyzerNum": 10,
                    "liteecm_limit_num": 10,
                    "network_mirror_session_has_filter_limit": 10,
                    "pm_iops_limit": 264000,
                    "dr_client_limit": 20,
                    "p_image_share_to_others_quota": 100,
                    "acl_limit_under_per_vpc": 100,
                    "oss_bucket_count_limit": 100,
                    "total_traffic_session_limit": 10,
                    "peakbandwidth_guaranteed_percentage": 20,
                    "{physical.s5.xlarge3}volume_limit_each_vm_os": 8,
                    "load_balancer_limit": 1,
                    "disk_backup_amount_limit": 0,
                    "max_duration_of_other_network_ip": "1Y",
                    "xssd1_volume_size_lower_limit": 20,
                    "cnssl_physicsLine_dnat_limit": 20,
                    "fast_ssd_volume_size_lower_limit": 1,
                    "sdwan_acl_rule_limit": 50,
                    "add_policy_host_group_num": 20,
                    "min_capacity_of_cbr_repo": 100,
                    "max_buckets_of_oss": 10,
                    "nic_relate_security_group_limit": 10,
                    "IngressBandwidth-CT": 50,
                    "load_balancer_pg_limit_os": 20,
                    "max_snat_dnat_num_private_small": 20,
                    "volume_size_lower_limit": 10,
                    "hpfs_data_flow_count_limit": 10,
                    "vpc_create_vip_limit": 100,
                    "load_balance_limit_each_scaling_group": 10,
                    "add_back_end_host_group_num": 100,
                    "ecm_template_limit": 20,
                    "ch_cnp_vpc_instance_bind_limit": 1,
                    "min_num_of_share_bandwidth_per_user_95_charge": 200,
                    "total_group_monitor_limit": 10,
                    "min_bandwidth_of_other_network_create_ip": 1,
                    "rules_limit_of_per_protocol_port_list": 200,
                    "snapshot_limit": 30,
                    "ch_create_limit": 10,
                    "oss_back_to_origin_rules_limit": 10,
                    "total_volume_snap_limit": 2000,
                    "vpce_limit_per_vpc": 50,
                    "network_limit_each_vpc_os": 5,
                    "max_duration_of_csbs_repo_creation": "3Y",
                    "max_dnat_num_private_xlarge": 250,
                    "ch_netmanagement_cda_limit": 5,
                    "max_capacity_of_bks_repo": 1024000,
                    "liteecm_create_snapshot_max_num": 3,
                    "sdwan_qos_rule_limt": 4,
                    "min_capacity_of_bks_repo": 100,
                    "csgNum": 16,
                    "hpfs_fileset_count_limit": 10,
                    "volume_snap_limit": 40,
                    "site_limit_each_time": 1000,
                    "max_num_of_share_bandwidth_per_user_95_charge": 1000,
                    "max_bandwidth_of_ipv6_creation_for_time": 300,
                    "total_record_dns_limit": 500,
                    "CWAI_basic_group_limit": 10,
                    "share_ebs_attach_count": 16,
                    "max_snat_dnat_num_private_medium": 50,
                    "scaling_config_limit": 100,
                    "volume_snap_total_limit": 50,
                    "other_network_ip_limit_each_time": 10,
                    "cnssl_edge_vpc_limit": 5,
                    "sdwan_qos_limit": 50,
                    "max_duration_of_disk_product_creation": "5Y",
                    "zsync_evaluate_task_limit": 5,
                    "elb_cidr_ip_count_limit": 50,
                    "cnssl_site_limit": 1000,
                    "max_duration_of_vpn_creation": "1Y",
                    "volume_size_limit": 204800,
                    "l2gw_limit": 10,
                    "monitor_board_limit": 20,
                    "vpn_connection_count_limit": 100,
                    "asrp_limit": 16,
                    "ssl_vpn_server_limit": 20,
                    "elb_cidr_policy_limit": 20,
                    "scaling_group_limit": 10,
                    "ssl_vpn_client_limit": 20,
                    "load_balancer_policy_limit_per_listener": 40,
                    "csbs_backup_policy_limit": 20,
                    "min_capacity_of_csbs_repo": 100,
                    "public_ip_v6_limit": 10,
                    "ssl_vpn_gate_count_limit": 20,
                    "max_duration_of_hpfs_product_creation": "3Y",
                    "sdwan_limit_each_dnat": 10,
                    "cnssl_physicsLine_route_limit": 50,
                    "xssd0_volume_size_lower_limit": 10,
                    "total_elb_gslb_policy_limit": 30,
                    "max_num_of_vip_per_vm": 10,
                    "ch_route_policy_prefix_limit": 32,
                    "network_mirror_filter_out_rule_limit": 10,
                    "sdwan_acl_limit": 50,
                    "resource_group_limit": 10,
                    "sfs_oceanfs_cross_domain_count_limit": 5,
                    "sdwan_edge_static_router_limit": 50,
                    "max_bandwidth_of_elastic_ip_creation_for_time_and_flow": 300,
                    "cnssl_edge_route_limit": 50,
                    "bks_backup_policy_repository_limit": 10,
                    "cda_port_bandwidth_max_limit": 100000,
                    "network_cards_limit": 10,
                    "max_count_of_nic_per_pm": 9,
                    "pm_mem_total_limit_per_platform": 50000,
                    "ch_netmanagement_sdwan_limit": 1,
                    "vpn_user_gate_count_limit": 100,
                    "add_cross_vpc_ip_limit": 100,
                    "max_duration_of_host_creation": "3Y",
                    "ch_netmanagement_vpn_limit": 5,
                    "vpce_server_limit_per_vpc": 50,
                    "xssd0_volume_size_lower_limit_new": 1,
                    "max_bandwidth_of_elastic_ip_creation_for_time_and_broadband": 300,
                    "p2p_connection_count_limit": 50,
                    "vpc_nat_limit": 50,
                    "{test.yqy}0626!@#$%": 5,
                    "sfs_fs_volume_limit": 50,
                    "volume_limit_each_vm": 5,
                    "cbr_repo_limit": 10,
                    "prefix_list_bind_limit": 100,
                    "cda_dedgw_vpc_bind_dedgw_limit_az": 32,
                    "sfs_fs_mount_point_count_limit": 20,
                    "create_ims_root_limit": 1024,
                    "max_xssd_volume_size_limit": 65536,
                    "xssd2_volume_size_lower_limit": 512,
                    "rules_limit_of_per_security_group": 1000,
                    "max_duration_of_bks_repo_creation": "3Y",
                    "member_eni_create_limit": 200,
                    "sfs_single_fs_volume_limit": 32,
                    "vm_limit_each_load_balancer": 100,
                    "bfdSessionLimit": 100,
                    "csbs_backup_amount_limit_os": 0,
                    "public_ip_limit": 10,
                    "max_duration_of_oceanfs_product_creation": "3Y",
                    "sdwan_limit": 20,
                    "cnssl_route_ip_limit": 50,
                    "sdwan_qos_rule_group_limt": 50,
                    "{physical.s5.2xlarge1}volume_limit_each_vm_os": 8,
                    "cda_dedgw_vpc_bind_dedgw_limit": 1,
                    "sfs_fs_count_limit": 10,
                    "CreateVolumeNumberQuota": 50,
                    "ssd_generic_volume_size_lower_limit": 1,
                    "route_limit_per_table": 50,
                    "flowlog_inst_limit": 10,
                    "max_dnat_num": 100,
                    "cda_order_guaranteed_percentage_limit": 30,
                    "create_ims_root_limi": 1024,
                    "network_limit_each_vpc": 3,
                    "monitoring_item_limit": 5,
                    "cda_dst_cdir_limit": 20,
                    "max_duration_of_network_creation": "3Y",
                    "remote_sec_limit_of_per_security_group": 100,
                    "public_ip_v6_os_limit": 10,
                    "sdwan_limit_each_cpe_client": 80,
                    "ch_redundant_group_member_limit": 2,
                    "max_num_of_share_bandwidth_per_user_for_time": 1000,
                    "sfs_permission_rule_count_limit": 400,
                    "max_snat_dnat_num_private_large": 200,
                    "ch_vpc_instance_bind_limit": 5,
                    "address_limit": 20,
                    "sdwan_limit_each_edge": 100,
                    "PathAnalyzerReportNum": 100,
                    "max_snat_dnat_num_private_xlarge": 500,
                    "max_num_of_pm_per_vip": 10,
                    "ch_policy_map_limit": 20,
                    "cbr_vault_limit": 10,
                    "total_elb_gslb_ippool_limit": 30,
                    "subscription_task_limit": 10,
                    "csbs_backup_capacity_limit_os": 0,
                    "network_acl_limit_os": 100,
                    "rule_limit_of_direction_out_per_acl_cs": 10,
                    "total_record_privatenat_limit": 5,
                    "max_count_of_nic_per_vm": 5,
                    "volume_limit_each_vm_os": 8,
                    "max_num_of_share_bandwidth_per_user_for_bw": 1000,
                    "snap_policy_bind_volume": 200,
                    "sata_volume_size_lower_limit": 1,
                    "fastSsd_ebs_attach_count": 8,
                    "max_bandwidth_of_other_network_create_ip": 300,
                    "liteecm_datadisk_num": 5,
                    "csbs_backup_capacity_limit": 0,
                    "ch_order_bandwidth_num_limit": 1,
                    "sfs_single_hpfs_volume_limit": 20480,
                    "total_volume_limit": 1000,
                    "max_nat_eip_num": 20,
                    "max_snat_bind_eip_num": 5,
                    "other_network_public_ip_limit": 10,
                    "max_capacity_of_cbr_repo": 1024000,
                    "ch_reconsitution_accredit_limit": 5,
                    "max_capacity_of_csbs_repo": 1024000,
                    "storage_limit": 327687,
                    "address_limit_each_time": 10,
                    "network_mirror_session_has_source_limit": 10,
                    "total_intranet_dns_limit": 10,
                    "zsync_migration_task_limit": 5,
                    "pm_limit_per_platform": 100,
                    "memory_limit": 409600,
                    "{physical.s5se.xlarge1}volume_limit_each_vm_os": 14,
                    "csbs_backup_policy_instance_limit": 20,
                    "ch_limit": 10,
                    "CWAI_extend_group_limit": 10,
                    "sfs_oceanfs_volume_limit": 500,
                    "image_region_copy_capacity_limit": 500,
                    "ch_create_route_num_limit": 500,
                    "dhcp_limit": 10,
                    "sas_volume_size_lower_limit": 1,
                    "pm_create_num_limit_per_time": 50,
                    "ssd_volume_size_lower_limit": 1,
                    "xssd_volume_snap_total_limit": 2000,
                    "vpn_target_router_limit": 20,
                    "sys_host_mount_limit": 5,
                    "security_group_limit_under_per_vpc": 100,
                    "liteecm_create_snapshot_max_num_user": 15,
                    "ch_netmanagement_vpc_limit": 10,
                    "sfs_permission_group_count_limit": 20,
                    "share_bandwidth_count_per_user_limit": 5,
                    "max_num_of_vip_per_pm": 10,
                    "rule_limit_of_direction_out_per_acl_os": 250,
                    "max_bandwidth_of_other_network_create_share_bandwidth": 1000,
                    "elb_cert_limit": 10,
                    "public_ip_limit_each_time": 10,
                    "total_volume_snap_policy_limit": 20,
                    "load_balancer_limit_os": 1,
                    "snapshot_limit_per_cloud_server": 10,
                    "vm_limit_per_group": 16,
                    "ch_redundant_group_limit": 5,
                    "vcpu_limit": 200,
                    "self_customized_alerm_model_limit": 50,
                    "sfs_hpfs_count_limit": 20,
                    "ch_create_route_limit": 20,
                    "ch_netmanagement_accountvpc_limit": 5,
                    "security_groups_limit": 100,
                    "test1": 2,
                    "csbs_repository_bound_to_policy_limit": 1,
                    "bks_repository_bound_to_policy_limit": 1,
                    "ch_order_bandwidth_limit_v2_max": 10000,
                    "add_extended_domain_name_certificate": 3,
                    "sdwan_direct_connect_limit": 50,
                    "sfs_oceanfs_mount_point_count_limit": 20,
                    "load_balancer_limit_each_ip_os": 10,
                    "max_bandwidth_of_elastic_ip_for_time_and_flow_by_bgp": 300,
                    "vpc_limit_os": 5,
                    "cnssl_physicsLine_app_vpc_limit": 5,
                    "cnssl_edge_subnet_limit": 50,
                    "hasImgExpMultiProcess": 1,
                    "vm_group_limit": 256,
                    "cda_gateway_count_limit": 20,
                    "vpc_limit": 10,
                    "load_balancer_limit_each_ip": 3,
                    "network_mirror_dst_bind_session_limit": 10,
                    "volume_limit_each_time": 100,
                    "ip_count_per_share_bandwidth": 20,
                    "ch_order_bandwidth_limit_v2": 2000,
                    "cda_physpcl_line_count_limit": 20,
                    "testKey777": 1,
                    "max_duration_of_other_network_share_bandwidth": "1Y",
                    "key_pair_limit": 100,
                    "disk_backup_capacity_limit": 0,
                    "bks_repo_limit": 10,
                    "site_limit": 1000,
                    "ch_create_trafficStrategy_limit": 10,
                    "max_snat_num_private_xlarge": 250,
                    "cnssl_physicsLine_snat_limit": 20,
                    "routing_table_limit": 100,
                    "max_duration_of_nat_creation": "3Y",
                    "csbs_backup_amount_limit": 0,
                    "max_snat_bind_natip_num": 5,
                    "network_mirror_filter_in_rule_limit": 10,
                    "monitor_panel_limit": 24,
                    "gateway_host_group_limit": 20,
                    "netCard_bind_sec_limit": 10,
                    "max_num_of_share_bandwidth_per_user": 1000,
                    "rule_limit_of_direction_in_per_acl_os": 250,
                    "max_snat_num_private_large": 100,
                    "p2p_router_count_limit_per_batch": 20,
                    "max_snat_num_private_medium": 25,
                    "secretMaxBandWidth": 200,
                    "snapshot_policy_limit": 20,
                    "max_bandwidth_of_elastic_ip_creation_for_time": 300,
                    "max_dnat_num_private_medium": 25,
                    "resource_limit_label_count": 10,
                    "protocol_port_list_limit": 100,
                    "max_bandwidth_of_elastic_ip_creation_os": 300,
                    "max_dnat_num_private_small": 10,
                    "sdwan_edge_mpls_ip_limit": 32,
                    "monitor_alerm_rules_limit": 20,
                    "sdwan_limit_each_site": 1000,
                    "vpc_router_limit_per_table": 50,
                    "other_network_create_share_bandwidth_limit": 5,
                    "vpn_connection_target_count_limit": 5,
                    "max_num_of_vm_per_vip": 10,
                    "{physical.s4.2xlarge1}volume_limit_each_vm_os": 60,
                    "snapshot_limit_os": 30,
                    "vm_limit_each_time": 50,
                    "max_duration_of_share_bandwidth_creation": "3Y",
                    "max_dnat_num_private_large": 100,
                    "vpcIpv6CidrsLimit": 5,
                    "cbr_ecs_limit": 20,
                    "scaling_rule_limit": 10,
                    "sfs_single_oceanfs_volume_limit": 1024,
                    "security_group_rules_limit": 5000,
                    "vpn_gate_count_limit": 20,
                    "pm_cpu_total_limit_per_platform": 8000,
                    "max_tamper_proof_limit_1": 3,
                    "sdwan_limit_each_vpc": 10,
                    "csbs_repo_limit": 10,
                    "trans_ip_limit": 50,
                    "sfs_single_exclusive_fs_volume_limit": 320,
                    "mage_region_copy_capacity_limit": 500,
                    "max_duration_of_host_new_creation": "5Y",
                    "ssl_vpn_target_count_limit": 5,
                    "xssd_volume_snap_limit": 1000,
                    "max_capacity_of_sys_disk_creation_os": 2048,
                    "monitor_view_limit": 30,
                    "ch_netmanagement_cloud_computer_limit": 5,
                    "total_traffic_mirror_limit": 10,
                    "sfs_oceanfs_count_limit": 10,
                    "prefix_single_limit": 200,
                    "min_bandwidth_of_other_network_create_share_bandwidth": 1,
                    "rule_limit_of_direction_in_per_acl_cs": 10,
                    "cda_line_count_limit": 20,
                    "vpc_next_jump_limit": 32,
                    "gateway_load_balance_limit": 20,
                    "sfs_hpfs_mount_point_count_limit": 10,
                    "p2p_router_count_limit_per_connection": 100,
                    "vm_limit": 50,
                    "ch_cda_subnet_limit": 50
                }
            },
            "errorCode": "",
            "message": "",
            "description": "",
            "statusCode": 800
        }
        with patch.object(self.client, 'get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            api = self.apis.ctecsquerycustomerquotasinregionv41api
            response = api.do(self.credential, self.client, self.endpoint, request)

            # 验证结果
            self.assertIsInstance(response, CtecsQueryCustomerQuotasInRegionV41Response)
            self.assertEqual(response.statusCode, 800)
            self.assertIsNotNone(response.returnObj)
            self.assertEqual(response.returnObj.global_quota.global_public_ip_limit, 20)
            self.assertEqual(response.returnObj.quotas.vm_limit, 50)

    def test_failed_request(self):
        """测试失败的API请求"""
        request = CtecsQueryCustomerQuotasInRegionV41Request(regionID='invalid_region_id')

        # Mock失败响应
        mock_response = {
            "message": "region info empty",
            "description": "资源池信息为空",
            "error": "Unknown.RegionInfo.Empty",
            "errorCode": "Unknown.RegionInfo.Empty",
            "returnObj": None,
            "statusCode": 900
        }

        with patch.object(self.client, 'get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            api = self.apis.ctecsquerycustomerquotasinregionv41api
            response = api.do(self.credential, self.client, self.endpoint, request)

            # 验证错误响应
            self.assertEqual(response.statusCode, 900)
            self.assertEqual(response.errorCode, 'Unknown.RegionInfo.Empty')
            self.assertEqual(response.message, 'region info empty')
            self.assertEqual(response.description, '资源池信息为空')
            self.assertEqual(response.error, 'Unknown.RegionInfo.Empty')
            self.assertIsNone(response.returnObj)

    def test_invalid_credentials(self):
        """测试无效凭证"""
        invalid_credential = Credential('invalid_ak', 'invalid_sk')
        request = CtecsQueryCustomerQuotasInRegionV41Request(regionID='81f7728662dd11ec810800155d307d5b')

        try:
            api = CtecsQueryCustomerQuotasInRegionV41Api()
            api.set_endpoint(self.endpoint)
            response = api.do(invalid_credential, self.client, self.endpoint, request)
            self.assertIsNotNone(response)  # 验证响应不为空
            print(f'Response: {response}')  # 打印响应内容
        except CtyunRequestException as e:
            pass

    def test_request_validation(self):
        """测试请求参数验证"""
        with self.assertRaises(TypeError):
            # 缺少必填参数regionID
            CtecsQueryCustomerQuotasInRegionV41Request()

        # 测试有效的请求参数
        valid_request = CtecsQueryCustomerQuotasInRegionV41Request(regionID='valid_region_id')
        self.assertEqual(valid_request.regionID, 'valid_region_id')

    def test_empty_response_handling(self):
        """测试空响应处理"""
        with self.assertRaises(ValueError):
            CtecsQueryCustomerQuotasInRegionV41Response.from_json({})

    def test_api_instance(self):
        """验证API实例是否正确初始化"""
        self.assertIsNotNone(self.apis)
        self.assertIsNotNone(self.apis.ctecsquerysummaryinregionv41api)

        # 验证API方法是否可用
        api = self.apis.ctecsquerysummaryinregionv41api
        self.assertTrue(callable(api.do))
        self.assertTrue(hasattr(api, 'set_endpoint'))


if __name__ == '__main__':
    unittest.main()
