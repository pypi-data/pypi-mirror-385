from typing import Optional
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.ctyunsdk_vpc20220909.core.credential import Credential

from .ctvpc_associate_secondary_cidrs_to_vpc_api import CtvpcAssociateSecondaryCidrsToVpcApi
from .ctvpc_disassociate_secondary_cidrs_from_vpc_api import CtvpcDisassociateSecondaryCidrsFromVpcApi
from .ctvpc_update_vpc_attribute_api import CtvpcUpdateVpcAttributeApi
from .ctvpc_update_i_pv6_status_for_vpc_api import CtvpcUpdateIPv6StatusForVpcApi
from .ctvpc_update_subnet_i_pv6_status_api import CtvpcUpdateSubnetIPv6StatusApi
from .ctvpc_create_vpc1_api import CtvpcCreateVpc1Api
from .ctvpc_delete_vpc_api import CtvpcDeleteVpcApi
from .ctvpc_replace_subnet_acl_api import CtvpcReplaceSubnetAclApi
from .ctvpc_replace_subnet_route_table_api import CtvpcReplaceSubnetRouteTableApi
from .ctvpc_disassociate_subnet_acl_api import CtvpcDisassociateSubnetAclApi
from .ctvpc_new_vpc_list_api import CtvpcNewVpcListApi
from .ctvpc_list_subnet_used_i_ps_api import CtvpcListSubnetUsedIPsApi
from .ctvpc_show_vpc_api import CtvpcShowVpcApi
from .ctvpc_list_vpc_api import CtvpcListVpcApi
from .ctvpc_show_subnet_api import CtvpcShowSubnetApi
from .ctvpc_up_date_subnet_api import CtvpcUpDateSubnetApi
from .ctvpc_vpc_create_subnet_api import CtvpcVpcCreateSubnetApi
from .ctvpc_new_subnet_list_api import CtvpcNewSubnetListApi
from .ctvpc_list_subnet_api import CtvpcListSubnetApi
from .ctvpc_create_havip_api import CtvpcCreateHavipApi
from .ctvpc_delete_havip_api import CtvpcDeleteHavipApi
from .ctvpc_list_havip_api import CtvpcListHavipApi
from .ctvpc_bind_havip_api import CtvpcBindHavipApi
from .ctvpc_modify_sg_ingress_rule_api import CtvpcModifySgIngressRuleApi
from .ctvpc_modify_sg_engress_rule_api import CtvpcModifySgEngressRuleApi
from .ctvpc_update_security_group_attribute_api import CtvpcUpdateSecurityGroupAttributeApi
from .ctvpc_create_sg_egress_rule_api import CtvpcCreateSgEgressRuleApi
from .ctvpc_create_sg_ingress_rule_api import CtvpcCreateSgIngressRuleApi
from .ctvpc_revoke_sg_engress_rule_api import CtvpcRevokeSgEngressRuleApi
from .ctvpc_revoke_sg_ingress_rule_api import CtvpcRevokeSgIngressRuleApi
from .ctvpc_sg_batch_attach_ports_api import CtvpcSgBatchAttachPortsApi
from .ctvpc_sg_batch_detach_ports_api import CtvpcSgBatchDetachPortsApi
from .ctvpc_batch_join_security_group_api import CtvpcBatchJoinSecurityGroupApi
from .ctvpc_new_query_security_groups_api import CtvpcNewQuerySecurityGroupsApi
from .ctvpc_show_security_group_api import CtvpcShowSecurityGroupApi
from .ctvpc_join_security_group_api import CtvpcJoinSecurityGroupApi
from .ctvpc_get_sg_associate_vms_api import CtvpcGetSgAssociateVmsApi
from .ctvpc_leave_security_group_api import CtvpcLeaveSecurityGroupApi
from .ctvpc_vpc_create_security_group_api import CtvpcVpcCreateSecurityGroupApi
from .ctvpc_show_havip_api import CtvpcShowHavipApi
from .ctvpc_unbind_havip_api import CtvpcUnbindHavipApi
from .ctvpc_vpc_delete_security_group_api import CtvpcVpcDeleteSecurityGroupApi
from .ctvpc_modify_route_rule_api import CtvpcModifyRouteRuleApi
from .ctvpc_update_route_table_attribute_api import CtvpcUpdateRouteTableAttributeApi
from .ctvpc_create_route_rule_api import CtvpcCreateRouteRuleApi
from .ctvpc_create_route_table_api import CtvpcCreateRouteTableApi
from .ctvpc_delete_route_rule_api import CtvpcDeleteRouteRuleApi
from .ctvpc_delete_route_table_api import CtvpcDeleteRouteTableApi
from .ctvpc_new_route_table_list_api import CtvpcNewRouteTableListApi
from .ctvpc_new_route_rules_list_api import CtvpcNewRouteRulesListApi
from .ctvpc_list_route_table_api import CtvpcListRouteTableApi
from .ctvpc_list_route_table_rules_api import CtvpcListRouteTableRulesApi
from .ctvpc_show_route_table_api import CtvpcShowRouteTableApi
from .ctvpc_port_replace_subnet_api import CtvpcPortReplaceSubnetApi
from .ctvpc_update_port_api import CtvpcUpdatePortApi
from .ctvpc_create_port_api import CtvpcCreatePortApi
from .ctvpc_delete_port_api import CtvpcDeletePortApi
from .ctvpc_assign_i_pv6_to_port_api import CtvpcAssignIPv6ToPortApi
from .ctvpc_unassign_i_pv6_from_port_api import CtvpcUnassignIPv6FromPortApi
from .ctvpc_batch_assign_i_pv6_to_port_api import CtvpcBatchAssignIPv6ToPortApi
from .ctvpc_batch_unassign_i_pv6_from_port_api import CtvpcBatchUnassignIPv6FromPortApi
from .ctvpc_new_ports_list_api import CtvpcNewPortsListApi
from .ctvpc_port_replace_v_p_c_api import CtvpcPortReplaceVPCApi
from .ctvpc_show_port_api import CtvpcShowPortApi
from .ctvpc_check_port_status_api import CtvpcCheckPortStatusApi
from .ctvpc_batch_check_port_status_api import CtvpcBatchCheckPortStatusApi
from .ctvpc_assign_secondary_private_i_ps_to_port_api import CtvpcAssignSecondaryPrivateIPsToPortApi
from .ctvpc_attach_port_api import CtvpcAttachPortApi
from .ctvpc_detach_port_api import CtvpcDetachPortApi
from .ctvpc_unassign_secondary_private_i_ps_from_port_api import CtvpcUnassignSecondaryPrivateIPsFromPortApi
from .ctvpc_list_acl_rule_api import CtvpcListAclRuleApi
from .ctvpc_list_acl_api import CtvpcListAclApi
from .ctvpc_show_acl_api import CtvpcShowAclApi
from .ctvpc_update_acl_attribute_api import CtvpcUpdateAclAttributeApi
from .ctvpc_update_acl_rule_attribute_api import CtvpcUpdateAclRuleAttributeApi
from .ctvpc_create_acl_api import CtvpcCreateAclApi
from .ctvpc_create_acl_rule_api import CtvpcCreateAclRuleApi
from .ctvpc_delete_acl_api import CtvpcDeleteAclApi
from .ctvpc_delete_acl_rule_api import CtvpcDeleteAclRuleApi
from .ctvpc_new_a_c_l_list_api import CtvpcNewACLListApi
from .ctvpc_vpc_list_port_api import CtvpcVpcListPortApi
from .ctvpc_create_route_table_rules_api import CtvpcCreateRouteTableRulesApi
from .ctvpc_update_route_table_rules_attribute_api import CtvpcUpdateRouteTableRulesAttributeApi
from .ctvpc_delete_route_table_rules_api import CtvpcDeleteRouteTableRulesApi
from .ctvpc_show_sg_rule_api import CtvpcShowSgRuleApi
from .ctvpc_sg_rule_pre_check_api import CtvpcSgRulePreCheckApi
from .ctvpc_vpc_delete_subnet_api import CtvpcVpcDeleteSubnetApi
from .ctvpc_associate_vpc_ipv6_cidrs_api import CtvpcAssociateVpcIpv6CidrsApi
from .ctvpc_disassociate_ipv6_cidrs_api import CtvpcDisassociateIpv6CidrsApi
from .ctvpc_list_ipv6_cidr_api import CtvpcListIpv6CidrApi

ENDPOINT_NAME = "ctvpc"

class Apis:
    _ctvpcassociatesecondarycidrstovpcapi: CtvpcAssociateSecondaryCidrsToVpcApi
    _ctvpcdisassociatesecondarycidrsfromvpcapi: CtvpcDisassociateSecondaryCidrsFromVpcApi
    _ctvpcupdatevpcattributeapi: CtvpcUpdateVpcAttributeApi
    _ctvpcupdateipv6statusforvpcapi: CtvpcUpdateIPv6StatusForVpcApi
    _ctvpcupdatesubnetipv6statusapi: CtvpcUpdateSubnetIPv6StatusApi
    _ctvpccreatevpc1api: CtvpcCreateVpc1Api
    _ctvpcdeletevpcapi: CtvpcDeleteVpcApi
    _ctvpcreplacesubnetaclapi: CtvpcReplaceSubnetAclApi
    _ctvpcreplacesubnetroutetableapi: CtvpcReplaceSubnetRouteTableApi
    _ctvpcdisassociatesubnetaclapi: CtvpcDisassociateSubnetAclApi
    _ctvpcnewvpclistapi: CtvpcNewVpcListApi
    _ctvpclistsubnetusedipsapi: CtvpcListSubnetUsedIPsApi
    _ctvpcshowvpcapi: CtvpcShowVpcApi
    _ctvpclistvpcapi: CtvpcListVpcApi
    _ctvpcshowsubnetapi: CtvpcShowSubnetApi
    _ctvpcupdatesubnetapi: CtvpcUpDateSubnetApi
    _ctvpcvpccreatesubnetapi: CtvpcVpcCreateSubnetApi
    _ctvpcnewsubnetlistapi: CtvpcNewSubnetListApi
    _ctvpclistsubnetapi: CtvpcListSubnetApi
    _ctvpccreatehavipapi: CtvpcCreateHavipApi
    _ctvpcdeletehavipapi: CtvpcDeleteHavipApi
    _ctvpclisthavipapi: CtvpcListHavipApi
    _ctvpcbindhavipapi: CtvpcBindHavipApi
    _ctvpcmodifysgingressruleapi: CtvpcModifySgIngressRuleApi
    _ctvpcmodifysgengressruleapi: CtvpcModifySgEngressRuleApi
    _ctvpcupdatesecuritygroupattributeapi: CtvpcUpdateSecurityGroupAttributeApi
    _ctvpccreatesgegressruleapi: CtvpcCreateSgEgressRuleApi
    _ctvpccreatesgingressruleapi: CtvpcCreateSgIngressRuleApi
    _ctvpcrevokesgengressruleapi: CtvpcRevokeSgEngressRuleApi
    _ctvpcrevokesgingressruleapi: CtvpcRevokeSgIngressRuleApi
    _ctvpcsgbatchattachportsapi: CtvpcSgBatchAttachPortsApi
    _ctvpcsgbatchdetachportsapi: CtvpcSgBatchDetachPortsApi
    _ctvpcbatchjoinsecuritygroupapi: CtvpcBatchJoinSecurityGroupApi
    _ctvpcnewquerysecuritygroupsapi: CtvpcNewQuerySecurityGroupsApi
    _ctvpcshowsecuritygroupapi: CtvpcShowSecurityGroupApi
    _ctvpcjoinsecuritygroupapi: CtvpcJoinSecurityGroupApi
    _ctvpcgetsgassociatevmsapi: CtvpcGetSgAssociateVmsApi
    _ctvpcleavesecuritygroupapi: CtvpcLeaveSecurityGroupApi
    _ctvpcvpccreatesecuritygroupapi: CtvpcVpcCreateSecurityGroupApi
    _ctvpcshowhavipapi: CtvpcShowHavipApi
    _ctvpcunbindhavipapi: CtvpcUnbindHavipApi
    _ctvpcvpcdeletesecuritygroupapi: CtvpcVpcDeleteSecurityGroupApi
    _ctvpcmodifyrouteruleapi: CtvpcModifyRouteRuleApi
    _ctvpcupdateroutetableattributeapi: CtvpcUpdateRouteTableAttributeApi
    _ctvpccreaterouteruleapi: CtvpcCreateRouteRuleApi
    _ctvpccreateroutetableapi: CtvpcCreateRouteTableApi
    _ctvpcdeleterouteruleapi: CtvpcDeleteRouteRuleApi
    _ctvpcdeleteroutetableapi: CtvpcDeleteRouteTableApi
    _ctvpcnewroutetablelistapi: CtvpcNewRouteTableListApi
    _ctvpcnewrouteruleslistapi: CtvpcNewRouteRulesListApi
    _ctvpclistroutetableapi: CtvpcListRouteTableApi
    _ctvpclistroutetablerulesapi: CtvpcListRouteTableRulesApi
    _ctvpcshowroutetableapi: CtvpcShowRouteTableApi
    _ctvpcportreplacesubnetapi: CtvpcPortReplaceSubnetApi
    _ctvpcupdateportapi: CtvpcUpdatePortApi
    _ctvpccreateportapi: CtvpcCreatePortApi
    _ctvpcdeleteportapi: CtvpcDeletePortApi
    _ctvpcassignipv6toportapi: CtvpcAssignIPv6ToPortApi
    _ctvpcunassignipv6fromportapi: CtvpcUnassignIPv6FromPortApi
    _ctvpcbatchassignipv6toportapi: CtvpcBatchAssignIPv6ToPortApi
    _ctvpcbatchunassignipv6fromportapi: CtvpcBatchUnassignIPv6FromPortApi
    _ctvpcnewportslistapi: CtvpcNewPortsListApi
    _ctvpcportreplacevpcapi: CtvpcPortReplaceVPCApi
    _ctvpcshowportapi: CtvpcShowPortApi
    _ctvpccheckportstatusapi: CtvpcCheckPortStatusApi
    _ctvpcbatchcheckportstatusapi: CtvpcBatchCheckPortStatusApi
    _ctvpcassignsecondaryprivateipstoportapi: CtvpcAssignSecondaryPrivateIPsToPortApi
    _ctvpcattachportapi: CtvpcAttachPortApi
    _ctvpcdetachportapi: CtvpcDetachPortApi
    _ctvpcunassignsecondaryprivateipsfromportapi: CtvpcUnassignSecondaryPrivateIPsFromPortApi
    _ctvpclistaclruleapi: CtvpcListAclRuleApi
    _ctvpclistaclapi: CtvpcListAclApi
    _ctvpcshowaclapi: CtvpcShowAclApi
    _ctvpcupdateaclattributeapi: CtvpcUpdateAclAttributeApi
    _ctvpcupdateaclruleattributeapi: CtvpcUpdateAclRuleAttributeApi
    _ctvpccreateaclapi: CtvpcCreateAclApi
    _ctvpccreateaclruleapi: CtvpcCreateAclRuleApi
    _ctvpcdeleteaclapi: CtvpcDeleteAclApi
    _ctvpcdeleteaclruleapi: CtvpcDeleteAclRuleApi
    _ctvpcnewacllistapi: CtvpcNewACLListApi
    _ctvpcvpclistportapi: CtvpcVpcListPortApi
    _ctvpccreateroutetablerulesapi: CtvpcCreateRouteTableRulesApi
    _ctvpcupdateroutetablerulesattributeapi: CtvpcUpdateRouteTableRulesAttributeApi
    _ctvpcdeleteroutetablerulesapi: CtvpcDeleteRouteTableRulesApi
    _ctvpcvpcdeletesubnetapi: CtvpcVpcDeleteSubnetApi
    _ctvpcassociatevpcipv6cidrsapi: CtvpcAssociateVpcIpv6CidrsApi
    _ctvpcdisassociateipv6cidrsapi: CtvpcDisassociateIpv6CidrsApi
    _ctvpclistipv6cidrapi: CtvpcListIpv6CidrApi

    def __init__(self, endpoint_url: str, client: Optional[CtyunClient] = None):
        self.client = client or CtyunClient()
        self.endpoint = endpoint_url
    
        self._ctvpcassociatesecondarycidrstovpcapi = CtvpcAssociateSecondaryCidrsToVpcApi(self.client)
        self._ctvpcassociatesecondarycidrstovpcapi.set_endpoint(self.endpoint)
        self._ctvpcdisassociatesecondarycidrsfromvpcapi = CtvpcDisassociateSecondaryCidrsFromVpcApi(self.client)
        self._ctvpcdisassociatesecondarycidrsfromvpcapi.set_endpoint(self.endpoint)
        self._ctvpcupdatevpcattributeapi = CtvpcUpdateVpcAttributeApi(self.client)
        self._ctvpcupdatevpcattributeapi.set_endpoint(self.endpoint)
        self._ctvpcupdateipv6statusforvpcapi = CtvpcUpdateIPv6StatusForVpcApi(self.client)
        self._ctvpcupdateipv6statusforvpcapi.set_endpoint(self.endpoint)
        self._ctvpcupdatesubnetipv6statusapi = CtvpcUpdateSubnetIPv6StatusApi(self.client)
        self._ctvpcupdatesubnetipv6statusapi.set_endpoint(self.endpoint)
        self._ctvpccreatevpc1api = CtvpcCreateVpc1Api(self.client)
        self._ctvpccreatevpc1api.set_endpoint(self.endpoint)
        self._ctvpcdeletevpcapi = CtvpcDeleteVpcApi(self.client)
        self._ctvpcdeletevpcapi.set_endpoint(self.endpoint)
        self._ctvpcreplacesubnetaclapi = CtvpcReplaceSubnetAclApi(self.client)
        self._ctvpcreplacesubnetaclapi.set_endpoint(self.endpoint)
        self._ctvpcreplacesubnetroutetableapi = CtvpcReplaceSubnetRouteTableApi(self.client)
        self._ctvpcreplacesubnetroutetableapi.set_endpoint(self.endpoint)
        self._ctvpcdisassociatesubnetaclapi = CtvpcDisassociateSubnetAclApi(self.client)
        self._ctvpcdisassociatesubnetaclapi.set_endpoint(self.endpoint)
        self._ctvpcnewvpclistapi = CtvpcNewVpcListApi(self.client)
        self._ctvpcnewvpclistapi.set_endpoint(self.endpoint)
        self._ctvpclistsubnetusedipsapi = CtvpcListSubnetUsedIPsApi(self.client)
        self._ctvpclistsubnetusedipsapi.set_endpoint(self.endpoint)
        self._ctvpcshowvpcapi = CtvpcShowVpcApi(self.client)
        self._ctvpcshowvpcapi.set_endpoint(self.endpoint)
        self._ctvpclistvpcapi = CtvpcListVpcApi(self.client)
        self._ctvpclistvpcapi.set_endpoint(self.endpoint)
        self._ctvpcshowsubnetapi = CtvpcShowSubnetApi(self.client)
        self._ctvpcshowsubnetapi.set_endpoint(self.endpoint)
        self._ctvpcupdatesubnetapi = CtvpcUpDateSubnetApi(self.client)
        self._ctvpcupdatesubnetapi.set_endpoint(self.endpoint)
        self._ctvpcvpccreatesubnetapi = CtvpcVpcCreateSubnetApi(self.client)
        self._ctvpcvpccreatesubnetapi.set_endpoint(self.endpoint)
        self._ctvpcnewsubnetlistapi = CtvpcNewSubnetListApi(self.client)
        self._ctvpcnewsubnetlistapi.set_endpoint(self.endpoint)
        self._ctvpclistsubnetapi = CtvpcListSubnetApi(self.client)
        self._ctvpclistsubnetapi.set_endpoint(self.endpoint)
        self._ctvpccreatehavipapi = CtvpcCreateHavipApi(self.client)
        self._ctvpccreatehavipapi.set_endpoint(self.endpoint)
        self._ctvpcdeletehavipapi = CtvpcDeleteHavipApi(self.client)
        self._ctvpcdeletehavipapi.set_endpoint(self.endpoint)
        self._ctvpclisthavipapi = CtvpcListHavipApi(self.client)
        self._ctvpclisthavipapi.set_endpoint(self.endpoint)
        self._ctvpcbindhavipapi = CtvpcBindHavipApi(self.client)
        self._ctvpcbindhavipapi.set_endpoint(self.endpoint)
        self._ctvpcmodifysgingressruleapi = CtvpcModifySgIngressRuleApi(self.client)
        self._ctvpcmodifysgingressruleapi.set_endpoint(self.endpoint)
        self._ctvpcmodifysgengressruleapi = CtvpcModifySgEngressRuleApi(self.client)
        self._ctvpcmodifysgengressruleapi.set_endpoint(self.endpoint)
        self._ctvpcupdatesecuritygroupattributeapi = CtvpcUpdateSecurityGroupAttributeApi(self.client)
        self._ctvpcupdatesecuritygroupattributeapi.set_endpoint(self.endpoint)
        self._ctvpccreatesgegressruleapi = CtvpcCreateSgEgressRuleApi(self.client)
        self._ctvpccreatesgegressruleapi.set_endpoint(self.endpoint)
        self._ctvpccreatesgingressruleapi = CtvpcCreateSgIngressRuleApi(self.client)
        self._ctvpccreatesgingressruleapi.set_endpoint(self.endpoint)
        self._ctvpcrevokesgengressruleapi = CtvpcRevokeSgEngressRuleApi(self.client)
        self._ctvpcrevokesgengressruleapi.set_endpoint(self.endpoint)
        self._ctvpcrevokesgingressruleapi = CtvpcRevokeSgIngressRuleApi(self.client)
        self._ctvpcrevokesgingressruleapi.set_endpoint(self.endpoint)
        self._ctvpcsgbatchattachportsapi = CtvpcSgBatchAttachPortsApi(self.client)
        self._ctvpcsgbatchattachportsapi.set_endpoint(self.endpoint)
        self._ctvpcsgbatchdetachportsapi = CtvpcSgBatchDetachPortsApi(self.client)
        self._ctvpcsgbatchdetachportsapi.set_endpoint(self.endpoint)
        self._ctvpcbatchjoinsecuritygroupapi = CtvpcBatchJoinSecurityGroupApi(self.client)
        self._ctvpcbatchjoinsecuritygroupapi.set_endpoint(self.endpoint)
        self._ctvpcnewquerysecuritygroupsapi = CtvpcNewQuerySecurityGroupsApi(self.client)
        self._ctvpcnewquerysecuritygroupsapi.set_endpoint(self.endpoint)
        self._ctvpcshowsecuritygroupapi = CtvpcShowSecurityGroupApi(self.client)
        self._ctvpcshowsecuritygroupapi.set_endpoint(self.endpoint)
        self._ctvpcjoinsecuritygroupapi = CtvpcJoinSecurityGroupApi(self.client)
        self._ctvpcjoinsecuritygroupapi.set_endpoint(self.endpoint)
        self._ctvpcgetsgassociatevmsapi = CtvpcGetSgAssociateVmsApi(self.client)
        self._ctvpcgetsgassociatevmsapi.set_endpoint(self.endpoint)
        self._ctvpcleavesecuritygroupapi = CtvpcLeaveSecurityGroupApi(self.client)
        self._ctvpcleavesecuritygroupapi.set_endpoint(self.endpoint)
        self._ctvpcvpccreatesecuritygroupapi = CtvpcVpcCreateSecurityGroupApi(self.client)
        self._ctvpcvpccreatesecuritygroupapi.set_endpoint(self.endpoint)
        self._ctvpcshowhavipapi = CtvpcShowHavipApi(self.client)
        self._ctvpcshowhavipapi.set_endpoint(self.endpoint)
        self._ctvpcunbindhavipapi = CtvpcUnbindHavipApi(self.client)
        self._ctvpcunbindhavipapi.set_endpoint(self.endpoint)
        self._ctvpcvpcdeletesecuritygroupapi = CtvpcVpcDeleteSecurityGroupApi(self.client)
        self._ctvpcvpcdeletesecuritygroupapi.set_endpoint(self.endpoint)
        self._ctvpcmodifyrouteruleapi = CtvpcModifyRouteRuleApi(self.client)
        self._ctvpcmodifyrouteruleapi.set_endpoint(self.endpoint)
        self._ctvpcupdateroutetableattributeapi = CtvpcUpdateRouteTableAttributeApi(self.client)
        self._ctvpcupdateroutetableattributeapi.set_endpoint(self.endpoint)
        self._ctvpccreaterouteruleapi = CtvpcCreateRouteRuleApi(self.client)
        self._ctvpccreaterouteruleapi.set_endpoint(self.endpoint)
        self._ctvpccreateroutetableapi = CtvpcCreateRouteTableApi(self.client)
        self._ctvpccreateroutetableapi.set_endpoint(self.endpoint)
        self._ctvpcdeleterouteruleapi = CtvpcDeleteRouteRuleApi(self.client)
        self._ctvpcdeleterouteruleapi.set_endpoint(self.endpoint)
        self._ctvpcdeleteroutetableapi = CtvpcDeleteRouteTableApi(self.client)
        self._ctvpcdeleteroutetableapi.set_endpoint(self.endpoint)
        self._ctvpcnewroutetablelistapi = CtvpcNewRouteTableListApi(self.client)
        self._ctvpcnewroutetablelistapi.set_endpoint(self.endpoint)
        self._ctvpcnewrouteruleslistapi = CtvpcNewRouteRulesListApi(self.client)
        self._ctvpcnewrouteruleslistapi.set_endpoint(self.endpoint)
        self._ctvpclistroutetableapi = CtvpcListRouteTableApi(self.client)
        self._ctvpclistroutetableapi.set_endpoint(self.endpoint)
        self._ctvpclistroutetablerulesapi = CtvpcListRouteTableRulesApi(self.client)
        self._ctvpclistroutetablerulesapi.set_endpoint(self.endpoint)
        self._ctvpcshowroutetableapi = CtvpcShowRouteTableApi(self.client)
        self._ctvpcshowroutetableapi.set_endpoint(self.endpoint)
        self._ctvpcportreplacesubnetapi = CtvpcPortReplaceSubnetApi(self.client)
        self._ctvpcportreplacesubnetapi.set_endpoint(self.endpoint)
        self._ctvpcupdateportapi = CtvpcUpdatePortApi(self.client)
        self._ctvpcupdateportapi.set_endpoint(self.endpoint)
        self._ctvpccreateportapi = CtvpcCreatePortApi(self.client)
        self._ctvpccreateportapi.set_endpoint(self.endpoint)
        self._ctvpcdeleteportapi = CtvpcDeletePortApi(self.client)
        self._ctvpcdeleteportapi.set_endpoint(self.endpoint)
        self._ctvpcassignipv6toportapi = CtvpcAssignIPv6ToPortApi(self.client)
        self._ctvpcassignipv6toportapi.set_endpoint(self.endpoint)
        self._ctvpcunassignipv6fromportapi = CtvpcUnassignIPv6FromPortApi(self.client)
        self._ctvpcunassignipv6fromportapi.set_endpoint(self.endpoint)
        self._ctvpcbatchassignipv6toportapi = CtvpcBatchAssignIPv6ToPortApi(self.client)
        self._ctvpcbatchassignipv6toportapi.set_endpoint(self.endpoint)
        self._ctvpcbatchunassignipv6fromportapi = CtvpcBatchUnassignIPv6FromPortApi(self.client)
        self._ctvpcbatchunassignipv6fromportapi.set_endpoint(self.endpoint)
        self._ctvpcnewportslistapi = CtvpcNewPortsListApi(self.client)
        self._ctvpcnewportslistapi.set_endpoint(self.endpoint)
        self._ctvpcportreplacevpcapi = CtvpcPortReplaceVPCApi(self.client)
        self._ctvpcportreplacevpcapi.set_endpoint(self.endpoint)
        self._ctvpcshowportapi = CtvpcShowPortApi(self.client)
        self._ctvpcshowportapi.set_endpoint(self.endpoint)
        self._ctvpccheckportstatusapi = CtvpcCheckPortStatusApi(self.client)
        self._ctvpccheckportstatusapi.set_endpoint(self.endpoint)
        self._ctvpcbatchcheckportstatusapi = CtvpcBatchCheckPortStatusApi(self.client)
        self._ctvpcbatchcheckportstatusapi.set_endpoint(self.endpoint)
        self._ctvpcassignsecondaryprivateipstoportapi = CtvpcAssignSecondaryPrivateIPsToPortApi(self.client)
        self._ctvpcassignsecondaryprivateipstoportapi.set_endpoint(self.endpoint)
        self._ctvpcattachportapi = CtvpcAttachPortApi(self.client)
        self._ctvpcattachportapi.set_endpoint(self.endpoint)
        self._ctvpcdetachportapi = CtvpcDetachPortApi(self.client)
        self._ctvpcdetachportapi.set_endpoint(self.endpoint)
        self._ctvpcunassignsecondaryprivateipsfromportapi = CtvpcUnassignSecondaryPrivateIPsFromPortApi(self.client)
        self._ctvpcunassignsecondaryprivateipsfromportapi.set_endpoint(self.endpoint)
        self._ctvpclistaclruleapi = CtvpcListAclRuleApi(self.client)
        self._ctvpclistaclruleapi.set_endpoint(self.endpoint)
        self._ctvpclistaclapi = CtvpcListAclApi(self.client)
        self._ctvpclistaclapi.set_endpoint(self.endpoint)
        self._ctvpcshowaclapi = CtvpcShowAclApi(self.client)
        self._ctvpcshowaclapi.set_endpoint(self.endpoint)
        self._ctvpcupdateaclattributeapi = CtvpcUpdateAclAttributeApi(self.client)
        self._ctvpcupdateaclattributeapi.set_endpoint(self.endpoint)
        self._ctvpcupdateaclruleattributeapi = CtvpcUpdateAclRuleAttributeApi(self.client)
        self._ctvpcupdateaclruleattributeapi.set_endpoint(self.endpoint)
        self._ctvpccreateaclapi = CtvpcCreateAclApi(self.client)
        self._ctvpccreateaclapi.set_endpoint(self.endpoint)
        self._ctvpccreateaclruleapi = CtvpcCreateAclRuleApi(self.client)
        self._ctvpccreateaclruleapi.set_endpoint(self.endpoint)
        self._ctvpcdeleteaclapi = CtvpcDeleteAclApi(self.client)
        self._ctvpcdeleteaclapi.set_endpoint(self.endpoint)
        self._ctvpcdeleteaclruleapi = CtvpcDeleteAclRuleApi(self.client)
        self._ctvpcdeleteaclruleapi.set_endpoint(self.endpoint)
        self._ctvpcnewacllistapi = CtvpcNewACLListApi(self.client)
        self._ctvpcnewacllistapi.set_endpoint(self.endpoint)
        self._ctvpcvpclistportapi = CtvpcVpcListPortApi(self.client)
        self._ctvpcvpclistportapi.set_endpoint(self.endpoint)
        self._ctvpccreateroutetablerulesapi = CtvpcCreateRouteTableRulesApi(self.client)
        self._ctvpccreateroutetablerulesapi.set_endpoint(self.endpoint)
        self._ctvpcupdateroutetablerulesattributeapi = CtvpcUpdateRouteTableRulesAttributeApi(self.client)
        self._ctvpcupdateroutetablerulesattributeapi.set_endpoint(self.endpoint)
        self._ctvpcdeleteroutetablerulesapi = CtvpcDeleteRouteTableRulesApi(self.client)
        self._ctvpcdeleteroutetablerulesapi.set_endpoint(self.endpoint)
        self._ctvpcvpcdeletesubnetapi = CtvpcVpcDeleteSubnetApi(self.client)
        self._ctvpcvpcdeletesubnetapi.set_endpoint(self.endpoint)
        self._ctvpcassociatevpcipv6cidrsapi = CtvpcAssociateVpcIpv6CidrsApi(self.client)
        self._ctvpcassociatevpcipv6cidrsapi.set_endpoint(self.endpoint)
        self._ctvpcdisassociateipv6cidrsapi = CtvpcDisassociateIpv6CidrsApi(self.client)
        self._ctvpcdisassociateipv6cidrsapi.set_endpoint(self.endpoint)
        self._ctvpclistipv6cidrapi = CtvpcListIpv6CidrApi(self.client)
        self._ctvpclistipv6cidrapi.set_endpoint(self.endpoint)
    
    @property  # noqa
    def ctvpcassociatesecondarycidrstovpcapi(self) -> CtvpcAssociateSecondaryCidrsToVpcApi:  # noqa
        return self._ctvpcassociatesecondarycidrstovpcapi
        
    @property  # noqa
    def ctvpcdisassociatesecondarycidrsfromvpcapi(self) -> CtvpcDisassociateSecondaryCidrsFromVpcApi:  # noqa
        return self._ctvpcdisassociatesecondarycidrsfromvpcapi
        
    @property  # noqa
    def ctvpcupdatevpcattributeapi(self) -> CtvpcUpdateVpcAttributeApi:  # noqa
        return self._ctvpcupdatevpcattributeapi
        
    @property  # noqa
    def ctvpcupdateipv6statusforvpcapi(self) -> CtvpcUpdateIPv6StatusForVpcApi:  # noqa
        return self._ctvpcupdateipv6statusforvpcapi
        
    @property  # noqa
    def ctvpcupdatesubnetipv6statusapi(self) -> CtvpcUpdateSubnetIPv6StatusApi:  # noqa
        return self._ctvpcupdatesubnetipv6statusapi
        
    @property  # noqa
    def ctvpccreatevpc1api(self) -> CtvpcCreateVpc1Api:  # noqa
        return self._ctvpccreatevpc1api
        
    @property  # noqa
    def ctvpcdeletevpcapi(self) -> CtvpcDeleteVpcApi:  # noqa
        return self._ctvpcdeletevpcapi
        
    @property  # noqa
    def ctvpcreplacesubnetaclapi(self) -> CtvpcReplaceSubnetAclApi:  # noqa
        return self._ctvpcreplacesubnetaclapi
        
    @property  # noqa
    def ctvpcreplacesubnetroutetableapi(self) -> CtvpcReplaceSubnetRouteTableApi:  # noqa
        return self._ctvpcreplacesubnetroutetableapi
        
    @property  # noqa
    def ctvpcdisassociatesubnetaclapi(self) -> CtvpcDisassociateSubnetAclApi:  # noqa
        return self._ctvpcdisassociatesubnetaclapi
        
    @property  # noqa
    def ctvpcnewvpclistapi(self) -> CtvpcNewVpcListApi:  # noqa
        return self._ctvpcnewvpclistapi
        
    @property  # noqa
    def ctvpclistsubnetusedipsapi(self) -> CtvpcListSubnetUsedIPsApi:  # noqa
        return self._ctvpclistsubnetusedipsapi
        
    @property  # noqa
    def ctvpcshowvpcapi(self) -> CtvpcShowVpcApi:  # noqa
        return self._ctvpcshowvpcapi
        
    @property  # noqa
    def ctvpclistvpcapi(self) -> CtvpcListVpcApi:  # noqa
        return self._ctvpclistvpcapi
        
    @property  # noqa
    def ctvpcshowsubnetapi(self) -> CtvpcShowSubnetApi:  # noqa
        return self._ctvpcshowsubnetapi
        
    @property  # noqa
    def ctvpcupdatesubnetapi(self) -> CtvpcUpDateSubnetApi:  # noqa
        return self._ctvpcupdatesubnetapi
        
    @property  # noqa
    def ctvpcvpccreatesubnetapi(self) -> CtvpcVpcCreateSubnetApi:  # noqa
        return self._ctvpcvpccreatesubnetapi
        
    @property  # noqa
    def ctvpcnewsubnetlistapi(self) -> CtvpcNewSubnetListApi:  # noqa
        return self._ctvpcnewsubnetlistapi
        
    @property  # noqa
    def ctvpclistsubnetapi(self) -> CtvpcListSubnetApi:  # noqa
        return self._ctvpclistsubnetapi
        
    @property  # noqa
    def ctvpccreatehavipapi(self) -> CtvpcCreateHavipApi:  # noqa
        return self._ctvpccreatehavipapi
        
    @property  # noqa
    def ctvpcdeletehavipapi(self) -> CtvpcDeleteHavipApi:  # noqa
        return self._ctvpcdeletehavipapi
        
    @property  # noqa
    def ctvpclisthavipapi(self) -> CtvpcListHavipApi:  # noqa
        return self._ctvpclisthavipapi
        
    @property  # noqa
    def ctvpcbindhavipapi(self) -> CtvpcBindHavipApi:  # noqa
        return self._ctvpcbindhavipapi
        
    @property  # noqa
    def ctvpcmodifysgingressruleapi(self) -> CtvpcModifySgIngressRuleApi:  # noqa
        return self._ctvpcmodifysgingressruleapi
        
    @property  # noqa
    def ctvpcmodifysgengressruleapi(self) -> CtvpcModifySgEngressRuleApi:  # noqa
        return self._ctvpcmodifysgengressruleapi
        
    @property  # noqa
    def ctvpcupdatesecuritygroupattributeapi(self) -> CtvpcUpdateSecurityGroupAttributeApi:  # noqa
        return self._ctvpcupdatesecuritygroupattributeapi
        
    @property  # noqa
    def ctvpccreatesgegressruleapi(self) -> CtvpcCreateSgEgressRuleApi:  # noqa
        return self._ctvpccreatesgegressruleapi
        
    @property  # noqa
    def ctvpccreatesgingressruleapi(self) -> CtvpcCreateSgIngressRuleApi:  # noqa
        return self._ctvpccreatesgingressruleapi
        
    @property  # noqa
    def ctvpcrevokesgengressruleapi(self) -> CtvpcRevokeSgEngressRuleApi:  # noqa
        return self._ctvpcrevokesgengressruleapi
        
    @property  # noqa
    def ctvpcrevokesgingressruleapi(self) -> CtvpcRevokeSgIngressRuleApi:  # noqa
        return self._ctvpcrevokesgingressruleapi
        
    @property  # noqa
    def ctvpcsgbatchattachportsapi(self) -> CtvpcSgBatchAttachPortsApi:  # noqa
        return self._ctvpcsgbatchattachportsapi
        
    @property  # noqa
    def ctvpcsgbatchdetachportsapi(self) -> CtvpcSgBatchDetachPortsApi:  # noqa
        return self._ctvpcsgbatchdetachportsapi
        
    @property  # noqa
    def ctvpcbatchjoinsecuritygroupapi(self) -> CtvpcBatchJoinSecurityGroupApi:  # noqa
        return self._ctvpcbatchjoinsecuritygroupapi
        
    @property  # noqa
    def ctvpcnewquerysecuritygroupsapi(self) -> CtvpcNewQuerySecurityGroupsApi:  # noqa
        return self._ctvpcnewquerysecuritygroupsapi
        
    @property  # noqa
    def ctvpcshowsecuritygroupapi(self) -> CtvpcShowSecurityGroupApi:  # noqa
        return self._ctvpcshowsecuritygroupapi
        
    @property  # noqa
    def ctvpcjoinsecuritygroupapi(self) -> CtvpcJoinSecurityGroupApi:  # noqa
        return self._ctvpcjoinsecuritygroupapi
        
    @property  # noqa
    def ctvpcgetsgassociatevmsapi(self) -> CtvpcGetSgAssociateVmsApi:  # noqa
        return self._ctvpcgetsgassociatevmsapi
        
    @property  # noqa
    def ctvpcleavesecuritygroupapi(self) -> CtvpcLeaveSecurityGroupApi:  # noqa
        return self._ctvpcleavesecuritygroupapi
        
    @property  # noqa
    def ctvpcvpccreatesecuritygroupapi(self) -> CtvpcVpcCreateSecurityGroupApi:  # noqa
        return self._ctvpcvpccreatesecuritygroupapi
        
    @property  # noqa
    def ctvpcshowhavipapi(self) -> CtvpcShowHavipApi:  # noqa
        return self._ctvpcshowhavipapi
        
    @property  # noqa
    def ctvpcunbindhavipapi(self) -> CtvpcUnbindHavipApi:  # noqa
        return self._ctvpcunbindhavipapi
        
    @property  # noqa
    def ctvpcvpcdeletesecuritygroupapi(self) -> CtvpcVpcDeleteSecurityGroupApi:  # noqa
        return self._ctvpcvpcdeletesecuritygroupapi
        
    @property  # noqa
    def ctvpcmodifyrouteruleapi(self) -> CtvpcModifyRouteRuleApi:  # noqa
        return self._ctvpcmodifyrouteruleapi
        
    @property  # noqa
    def ctvpcupdateroutetableattributeapi(self) -> CtvpcUpdateRouteTableAttributeApi:  # noqa
        return self._ctvpcupdateroutetableattributeapi
        
    @property  # noqa
    def ctvpccreaterouteruleapi(self) -> CtvpcCreateRouteRuleApi:  # noqa
        return self._ctvpccreaterouteruleapi
        
    @property  # noqa
    def ctvpccreateroutetableapi(self) -> CtvpcCreateRouteTableApi:  # noqa
        return self._ctvpccreateroutetableapi
        
    @property  # noqa
    def ctvpcdeleterouteruleapi(self) -> CtvpcDeleteRouteRuleApi:  # noqa
        return self._ctvpcdeleterouteruleapi
        
    @property  # noqa
    def ctvpcdeleteroutetableapi(self) -> CtvpcDeleteRouteTableApi:  # noqa
        return self._ctvpcdeleteroutetableapi
        
    @property  # noqa
    def ctvpcnewroutetablelistapi(self) -> CtvpcNewRouteTableListApi:  # noqa
        return self._ctvpcnewroutetablelistapi
        
    @property  # noqa
    def ctvpcnewrouteruleslistapi(self) -> CtvpcNewRouteRulesListApi:  # noqa
        return self._ctvpcnewrouteruleslistapi
        
    @property  # noqa
    def ctvpclistroutetableapi(self) -> CtvpcListRouteTableApi:  # noqa
        return self._ctvpclistroutetableapi
        
    @property  # noqa
    def ctvpclistroutetablerulesapi(self) -> CtvpcListRouteTableRulesApi:  # noqa
        return self._ctvpclistroutetablerulesapi
        
    @property  # noqa
    def ctvpcshowroutetableapi(self) -> CtvpcShowRouteTableApi:  # noqa
        return self._ctvpcshowroutetableapi
        
    @property  # noqa
    def ctvpcportreplacesubnetapi(self) -> CtvpcPortReplaceSubnetApi:  # noqa
        return self._ctvpcportreplacesubnetapi
        
    @property  # noqa
    def ctvpcupdateportapi(self) -> CtvpcUpdatePortApi:  # noqa
        return self._ctvpcupdateportapi
        
    @property  # noqa
    def ctvpccreateportapi(self) -> CtvpcCreatePortApi:  # noqa
        return self._ctvpccreateportapi
        
    @property  # noqa
    def ctvpcdeleteportapi(self) -> CtvpcDeletePortApi:  # noqa
        return self._ctvpcdeleteportapi
        
    @property  # noqa
    def ctvpcassignipv6toportapi(self) -> CtvpcAssignIPv6ToPortApi:  # noqa
        return self._ctvpcassignipv6toportapi
        
    @property  # noqa
    def ctvpcunassignipv6fromportapi(self) -> CtvpcUnassignIPv6FromPortApi:  # noqa
        return self._ctvpcunassignipv6fromportapi
        
    @property  # noqa
    def ctvpcbatchassignipv6toportapi(self) -> CtvpcBatchAssignIPv6ToPortApi:  # noqa
        return self._ctvpcbatchassignipv6toportapi
        
    @property  # noqa
    def ctvpcbatchunassignipv6fromportapi(self) -> CtvpcBatchUnassignIPv6FromPortApi:  # noqa
        return self._ctvpcbatchunassignipv6fromportapi
        
    @property  # noqa
    def ctvpcnewportslistapi(self) -> CtvpcNewPortsListApi:  # noqa
        return self._ctvpcnewportslistapi
        
    @property  # noqa
    def ctvpcportreplacevpcapi(self) -> CtvpcPortReplaceVPCApi:  # noqa
        return self._ctvpcportreplacevpcapi
        
    @property  # noqa
    def ctvpcshowportapi(self) -> CtvpcShowPortApi:  # noqa
        return self._ctvpcshowportapi
        
    @property  # noqa
    def ctvpccheckportstatusapi(self) -> CtvpcCheckPortStatusApi:  # noqa
        return self._ctvpccheckportstatusapi
        
    @property  # noqa
    def ctvpcbatchcheckportstatusapi(self) -> CtvpcBatchCheckPortStatusApi:  # noqa
        return self._ctvpcbatchcheckportstatusapi
        
    @property  # noqa
    def ctvpcassignsecondaryprivateipstoportapi(self) -> CtvpcAssignSecondaryPrivateIPsToPortApi:  # noqa
        return self._ctvpcassignsecondaryprivateipstoportapi
        
    @property  # noqa
    def ctvpcattachportapi(self) -> CtvpcAttachPortApi:  # noqa
        return self._ctvpcattachportapi
        
    @property  # noqa
    def ctvpcdetachportapi(self) -> CtvpcDetachPortApi:  # noqa
        return self._ctvpcdetachportapi
        
    @property  # noqa
    def ctvpcunassignsecondaryprivateipsfromportapi(self) -> CtvpcUnassignSecondaryPrivateIPsFromPortApi:  # noqa
        return self._ctvpcunassignsecondaryprivateipsfromportapi
        
    @property  # noqa
    def ctvpclistaclruleapi(self) -> CtvpcListAclRuleApi:  # noqa
        return self._ctvpclistaclruleapi
        
    @property  # noqa
    def ctvpclistaclapi(self) -> CtvpcListAclApi:  # noqa
        return self._ctvpclistaclapi
        
    @property  # noqa
    def ctvpcshowaclapi(self) -> CtvpcShowAclApi:  # noqa
        return self._ctvpcshowaclapi
        
    @property  # noqa
    def ctvpcupdateaclattributeapi(self) -> CtvpcUpdateAclAttributeApi:  # noqa
        return self._ctvpcupdateaclattributeapi
        
    @property  # noqa
    def ctvpcupdateaclruleattributeapi(self) -> CtvpcUpdateAclRuleAttributeApi:  # noqa
        return self._ctvpcupdateaclruleattributeapi
        
    @property  # noqa
    def ctvpccreateaclapi(self) -> CtvpcCreateAclApi:  # noqa
        return self._ctvpccreateaclapi
        
    @property  # noqa
    def ctvpccreateaclruleapi(self) -> CtvpcCreateAclRuleApi:  # noqa
        return self._ctvpccreateaclruleapi
        
    @property  # noqa
    def ctvpcdeleteaclapi(self) -> CtvpcDeleteAclApi:  # noqa
        return self._ctvpcdeleteaclapi
        
    @property  # noqa
    def ctvpcdeleteaclruleapi(self) -> CtvpcDeleteAclRuleApi:  # noqa
        return self._ctvpcdeleteaclruleapi
        
    @property  # noqa
    def ctvpcnewacllistapi(self) -> CtvpcNewACLListApi:  # noqa
        return self._ctvpcnewacllistapi
        
    @property  # noqa
    def ctvpcvpclistportapi(self) -> CtvpcVpcListPortApi:  # noqa
        return self._ctvpcvpclistportapi
        
    @property  # noqa
    def ctvpccreateroutetablerulesapi(self) -> CtvpcCreateRouteTableRulesApi:  # noqa
        return self._ctvpccreateroutetablerulesapi
        
    @property  # noqa
    def ctvpcupdateroutetablerulesattributeapi(self) -> CtvpcUpdateRouteTableRulesAttributeApi:  # noqa
        return self._ctvpcupdateroutetablerulesattributeapi
        
    @property  # noqa
    def ctvpcdeleteroutetablerulesapi(self) -> CtvpcDeleteRouteTableRulesApi:  # noqa
        return self._ctvpcdeleteroutetablerulesapi
        
    @property  # noqa
    def ctvpcvpcdeletesubnetapi(self) -> CtvpcVpcDeleteSubnetApi:  # noqa
        return self._ctvpcvpcdeletesubnetapi
        
    @property  # noqa
    def ctvpcassociatevpcipv6cidrsapi(self) -> CtvpcAssociateVpcIpv6CidrsApi:  # noqa
        return self._ctvpcassociatevpcipv6cidrsapi
        
    @property  # noqa
    def ctvpcdisassociateipv6cidrsapi(self) -> CtvpcDisassociateIpv6CidrsApi:  # noqa
        return self._ctvpcdisassociateipv6cidrsapi
        
    @property  # noqa
    def ctvpclistipv6cidrapi(self) -> CtvpcListIpv6CidrApi:  # noqa
        return self._ctvpclistipv6cidrapi
        
