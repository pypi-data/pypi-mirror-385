from typing import Optional
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential

from .ctelb_check_server_cert_api import CtelbCheckServerCertApi
from .ctelb_check_ca_cert_api import CtelbCheckCaCertApi
from .ctelb_list_domain_cert_links_api import CtelbListDomainCertLinksApi
from .ctelb_update_domain_cert_links_api import CtelbUpdateDomainCertLinksApi
from .ctelb_delete_domain_cert_links_api import CtelbDeleteDomainCertLinksApi
from .ctelb_create_domain_cert_link_api import CtelbCreateDomainCertLinkApi
from .ctelb_refund_pgelb_api import CtelbRefundPgelbApi
from .ctelb_update_listener_response_timeout_api import CtelbUpdateListenerResponseTimeoutApi
from .ctelb_update_listener_qps_api import CtelbUpdateListenerQpsApi
from .ctelb_update_listener_nat64_api import CtelbUpdateListenerNat64Api
from .ctelb_update_listener_idle_timeout_api import CtelbUpdateListenerIdleTimeoutApi
from .ctelb_update_listener_estab_timeout_api import CtelbUpdateListenerEstabTimeoutApi
from .ctelb_update_listener_cps_api import CtelbUpdateListenerCpsApi
from .ctelb_elb_unbind_labels_api import CtelbElbUnbindLabelsApi
from .ctelb_elb_bind_labels_api import CtelbElbBindLabelsApi
from .ctelb_list_elb_labels_api import CtelbListElbLabelsApi
from .ctelb_upgrade_to_pgelb_api import CtelbUpgradeToPgelbApi
from .ctelb_query_renew_pgelb_price_api import CtelbQueryRenewPgelbPriceApi
from .ctelb_renew_pgelb_api import CtelbRenewPgelbApi
from .ctelb_query_modify_pgelb_spec_price_api import CtelbQueryModifyPgelbSpecPriceApi
from .ctelb_modify_pgelb_spec_api import CtelbModifyPgelbSpecApi
from .ctelb_query_create_pgelb_price_api import CtelbQueryCreatePgelbPriceApi
from .ctelb_delete_load_balancer_api import CtelbDeleteLoadBalancerApi
from .ctelb_update_load_balancer_api import CtelbUpdateLoadBalancerApi
from .ctelb_show_load_balancer_api import CtelbShowLoadBalancerApi
from .ctelb_list_load_balancer_api import CtelbListLoadBalancerApi
from .ctelb_associate_eip_to_load_balancer_api import CtelbAssociateEipToLoadBalancerApi
from .ctelb_disassociate_eip_from_load_balancer_api import CtelbDisassociateEipFromLoadBalancerApi
from .ctelb_create_listener_api import CtelbCreateListenerApi
from .ctelb_update_listener_api import CtelbUpdateListenerApi
from .ctelb_delete_listener_api import CtelbDeleteListenerApi
from .ctelb_show_listener_api import CtelbShowListenerApi
from .ctelb_list_listener_api import CtelbListListenerApi
from .ctelb_start_listener_api import CtelbStartListenerApi
from .ctelb_stop_listener_api import CtelbStopListenerApi
from .ctelb_create_health_check_api import CtelbCreateHealthCheckApi
from .ctelb_create_certificate_api import CtelbCreateCertificateApi
from .ctelb_update_health_check_api import CtelbUpdateHealthCheckApi
from .ctelb_delete_health_check_api import CtelbDeleteHealthCheckApi
from .ctelb_list_health_check_api import CtelbListHealthCheckApi
from .ctelb_delete_certificate_api import CtelbDeleteCertificateApi
from .ctelb_show_certificate_api import CtelbShowCertificateApi
from .ctelb_list_certificate_api import CtelbListCertificateApi
from .ctelb_create_access_control_api import CtelbCreateAccessControlApi
from .ctelb_delete_access_control_api import CtelbDeleteAccessControlApi
from .ctelb_update_access_control_api import CtelbUpdateAccessControlApi
from .ctelb_list_access_control_api import CtelbListAccessControlApi
from .ctelb_delete_rule_api import CtelbDeleteRuleApi
from .ctelb_create_rule_api import CtelbCreateRuleApi
from .ctelb_update_rule_api import CtelbUpdateRuleApi
from .ctelb_show_rule_api import CtelbShowRuleApi
from .ctelb_list_query_api import CtelbListQueryApi
from .ctelb_query_sla_api import CtelbQuerySlaApi
from .ctelb_query_elb_reatime_metric_api import CtelbQueryElbReatimeMetricApi
from .ctelb_show_health_check_api import CtelbShowHealthCheckApi
from .ctelb_show_access_control_api import CtelbShowAccessControlApi
from .ctelb_disable_elb_ipv6_api import CtelbDisableElbIpv6Api
from .ctelb_enable_elb_ipv6_api import CtelbEnableElbIpv6Api
from .ctelb_update_certificate_api import CtelbUpdateCertificateApi
from .ctelb_query_elb_history_metric_api import CtelbQueryElbHistoryMetricApi
from .ctelb_async_create_loadbalance_api import CtelbAsyncCreateLoadbalanceApi
from .ctelb_async_create_certificate_api import CtelbAsyncCreateCertificateApi
from .ctelb_list_vm_pool_api import CtelbListVmPoolApi
from .ctelb_async_create_listener_api import CtelbAsyncCreateListenerApi
from .ctelb_update_listener_attr_api import CtelbUpdateListenerAttrApi
from .ctelb_async_create_policy_api import CtelbAsyncCreatePolicyApi
from .ctelb_new_query_elb_history_monitor_api import CtelbNewQueryElbHistoryMonitorApi
from .ctelb_update_policy_attr_api import CtelbUpdatePolicyAttrApi
from .ctelb_new_query_elb_reatime_monitor_api import CtelbNewQueryElbReatimeMonitorApi
from .ctelb_remove_vm_api import CtelbRemoveVmApi
from .ctelb_list_vm_api import CtelbListVmApi
from .ctelb_async_create_target_api import CtelbAsyncCreateTargetApi
from .ctelb_list_target_api import CtelbListTargetApi
from .ctelb_show_target_api import CtelbShowTargetApi
from .ctelb_update_target_api import CtelbUpdateTargetApi
from .ctelb_delete_target_api import CtelbDeleteTargetApi
from .ctelb_create_target_api import CtelbCreateTargetApi
from .ctelb_list_target_group_api import CtelbListTargetGroupApi
from .ctelb_show_target_group_api import CtelbShowTargetGroupApi
from .ctelb_delete_target_group_api import CtelbDeleteTargetGroupApi
from .ctelb_update_target_group_api import CtelbUpdateTargetGroupApi
from .ctelb_create_target_group_api import CtelbCreateTargetGroupApi
from .ctelb_update_vm_pool_attr_api import CtelbUpdateVmPoolAttrApi
from .ctelb_gwlb_create_api import CtelbGwlbCreateApi
from .ctelb_gwlb_update_api import CtelbGwlbUpdateApi
from .ctelb_gwlb_delete_api import CtelbGwlbDeleteApi
from .ctelb_gwlb_disable_delete_protection_api import CtelbGwlbDisableDeleteProtectionApi
from .ctelb_gwlb_disable_ipv6_api import CtelbGwlbDisableIpv6Api
from .ctelb_gwlb_enable_ipv6_api import CtelbGwlbEnableIpv6Api
from .ctelb_gwlb_enable_delete_protection_api import CtelbGwlbEnableDeleteProtectionApi
from .ctelb_gwlb_show_api import CtelbGwlbShowApi
from .ctelb_gwlb_list_api import CtelbGwlbListApi
from .ctelb_iplistener_create_api import CtelbIplistenerCreateApi
from .ctelb_iplistener_update_api import CtelbIplistenerUpdateApi
from .ctelb_iplistener_delete_api import CtelbIplistenerDeleteApi
from .ctelb_iplistener_show_api import CtelbIplistenerShowApi
from .ctelb_iplistener_list_api import CtelbIplistenerListApi
from .ctelb_gwlb_create_target_api import CtelbGwlbCreateTargetApi
from .ctelb_gwlb_update_target_api import CtelbGwlbUpdateTargetApi
from .ctelb_gwlb_delete_target_api import CtelbGwlbDeleteTargetApi
from .ctelb_gwlb_show_target_api import CtelbGwlbShowTargetApi
from .ctelb_gwlb_list_target_api import CtelbGwlbListTargetApi
from .ctelb_gwlb_create_target_group_api import CtelbGwlbCreateTargetGroupApi
from .ctelb_gwlb_update_target_group_api import CtelbGwlbUpdateTargetGroupApi
from .ctelb_gwlb_delete_target_group_api import CtelbGwlbDeleteTargetGroupApi
from .ctelb_gwlb_show_target_group_api import CtelbGwlbShowTargetGroupApi
from .ctelb_gwlb_list_target_group_api import CtelbGwlbListTargetGroupApi
from .ctelb_elb_disable_idc_api import CtelbElbDisableIDCApi
from .ctelb_elb_enable_idc_api import CtelbElbEnableIDCApi
from .ctelb_elb_modify_access_log_api import CtelbElbModifyAccessLogApi
from .ctelb_elb_delete_access_log_api import CtelbElbDeleteAccessLogApi
from .ctelb_elb_create_access_log_api import CtelbElbCreateAccessLogApi
from .ctelb_create_pgelb_api import CtelbCreatePgelbApi
from .ctelb_create_load_balancer_api import CtelbCreateLoadBalancerApi

ENDPOINT_NAME = "ctelb"

class Apis:
    _ctelbcheckservercertapi: CtelbCheckServerCertApi
    _ctelbcheckcacertapi: CtelbCheckCaCertApi
    _ctelblistdomaincertlinksapi: CtelbListDomainCertLinksApi
    _ctelbupdatedomaincertlinksapi: CtelbUpdateDomainCertLinksApi
    _ctelbdeletedomaincertlinksapi: CtelbDeleteDomainCertLinksApi
    _ctelbcreatedomaincertlinkapi: CtelbCreateDomainCertLinkApi
    _ctelbrefundpgelbapi: CtelbRefundPgelbApi
    _ctelbupdatelistenerresponsetimeoutapi: CtelbUpdateListenerResponseTimeoutApi
    _ctelbupdatelistenerqpsapi: CtelbUpdateListenerQpsApi
    _ctelbupdatelistenernat64api: CtelbUpdateListenerNat64Api
    _ctelbupdatelisteneridletimeoutapi: CtelbUpdateListenerIdleTimeoutApi
    _ctelbupdatelistenerestabtimeoutapi: CtelbUpdateListenerEstabTimeoutApi
    _ctelbupdatelistenercpsapi: CtelbUpdateListenerCpsApi
    _ctelbelbunbindlabelsapi: CtelbElbUnbindLabelsApi
    _ctelbelbbindlabelsapi: CtelbElbBindLabelsApi
    _ctelblistelblabelsapi: CtelbListElbLabelsApi
    _ctelbupgradetopgelbapi: CtelbUpgradeToPgelbApi
    _ctelbqueryrenewpgelbpriceapi: CtelbQueryRenewPgelbPriceApi
    _ctelbrenewpgelbapi: CtelbRenewPgelbApi
    _ctelbquerymodifypgelbspecpriceapi: CtelbQueryModifyPgelbSpecPriceApi
    _ctelbmodifypgelbspecapi: CtelbModifyPgelbSpecApi
    _ctelbquerycreatepgelbpriceapi: CtelbQueryCreatePgelbPriceApi
    _ctelbdeleteloadbalancerapi: CtelbDeleteLoadBalancerApi
    _ctelbupdateloadbalancerapi: CtelbUpdateLoadBalancerApi
    _ctelbshowloadbalancerapi: CtelbShowLoadBalancerApi
    _ctelblistloadbalancerapi: CtelbListLoadBalancerApi
    _ctelbassociateeiptoloadbalancerapi: CtelbAssociateEipToLoadBalancerApi
    _ctelbdisassociateeipfromloadbalancerapi: CtelbDisassociateEipFromLoadBalancerApi
    _ctelbcreatelistenerapi: CtelbCreateListenerApi
    _ctelbupdatelistenerapi: CtelbUpdateListenerApi
    _ctelbdeletelistenerapi: CtelbDeleteListenerApi
    _ctelbshowlistenerapi: CtelbShowListenerApi
    _ctelblistlistenerapi: CtelbListListenerApi
    _ctelbstartlistenerapi: CtelbStartListenerApi
    _ctelbstoplistenerapi: CtelbStopListenerApi
    _ctelbcreatehealthcheckapi: CtelbCreateHealthCheckApi
    _ctelbcreatecertificateapi: CtelbCreateCertificateApi
    _ctelbupdatehealthcheckapi: CtelbUpdateHealthCheckApi
    _ctelbdeletehealthcheckapi: CtelbDeleteHealthCheckApi
    _ctelblisthealthcheckapi: CtelbListHealthCheckApi
    _ctelbdeletecertificateapi: CtelbDeleteCertificateApi
    _ctelbshowcertificateapi: CtelbShowCertificateApi
    _ctelblistcertificateapi: CtelbListCertificateApi
    _ctelbcreateaccesscontrolapi: CtelbCreateAccessControlApi
    _ctelbdeleteaccesscontrolapi: CtelbDeleteAccessControlApi
    _ctelbupdateaccesscontrolapi: CtelbUpdateAccessControlApi
    _ctelblistaccesscontrolapi: CtelbListAccessControlApi
    _ctelbdeleteruleapi: CtelbDeleteRuleApi
    _ctelbcreateruleapi: CtelbCreateRuleApi
    _ctelbupdateruleapi: CtelbUpdateRuleApi
    _ctelbshowruleapi: CtelbShowRuleApi
    _ctelblistqueryapi: CtelbListQueryApi
    _ctelbqueryslaapi: CtelbQuerySlaApi
    _ctelbqueryelbreatimemetricapi: CtelbQueryElbReatimeMetricApi
    _ctelbshowhealthcheckapi: CtelbShowHealthCheckApi
    _ctelbshowaccesscontrolapi: CtelbShowAccessControlApi
    _ctelbdisableelbipv6api: CtelbDisableElbIpv6Api
    _ctelbenableelbipv6api: CtelbEnableElbIpv6Api
    _ctelbupdatecertificateapi: CtelbUpdateCertificateApi
    _ctelbqueryelbhistorymetricapi: CtelbQueryElbHistoryMetricApi
    _ctelbasynccreateloadbalanceapi: CtelbAsyncCreateLoadbalanceApi
    _ctelbasynccreatecertificateapi: CtelbAsyncCreateCertificateApi
    _ctelblistvmpoolapi: CtelbListVmPoolApi
    _ctelbasynccreatelistenerapi: CtelbAsyncCreateListenerApi
    _ctelbupdatelistenerattrapi: CtelbUpdateListenerAttrApi
    _ctelbasynccreatepolicyapi: CtelbAsyncCreatePolicyApi
    _ctelbnewqueryelbhistorymonitorapi: CtelbNewQueryElbHistoryMonitorApi
    _ctelbupdatepolicyattrapi: CtelbUpdatePolicyAttrApi
    _ctelbnewqueryelbreatimemonitorapi: CtelbNewQueryElbReatimeMonitorApi
    _ctelbremovevmapi: CtelbRemoveVmApi
    _ctelblistvmapi: CtelbListVmApi
    _ctelbasynccreatetargetapi: CtelbAsyncCreateTargetApi
    _ctelblisttargetapi: CtelbListTargetApi
    _ctelbshowtargetapi: CtelbShowTargetApi
    _ctelbupdatetargetapi: CtelbUpdateTargetApi
    _ctelbdeletetargetapi: CtelbDeleteTargetApi
    _ctelbcreatetargetapi: CtelbCreateTargetApi
    _ctelblisttargetgroupapi: CtelbListTargetGroupApi
    _ctelbshowtargetgroupapi: CtelbShowTargetGroupApi
    _ctelbdeletetargetgroupapi: CtelbDeleteTargetGroupApi
    _ctelbupdatetargetgroupapi: CtelbUpdateTargetGroupApi
    _ctelbcreatetargetgroupapi: CtelbCreateTargetGroupApi
    _ctelbupdatevmpoolattrapi: CtelbUpdateVmPoolAttrApi
    _ctelbgwlbcreateapi: CtelbGwlbCreateApi
    _ctelbgwlbupdateapi: CtelbGwlbUpdateApi
    _ctelbgwlbdeleteapi: CtelbGwlbDeleteApi
    _ctelbgwlbdisabledeleteprotectionapi: CtelbGwlbDisableDeleteProtectionApi
    _ctelbgwlbdisableipv6api: CtelbGwlbDisableIpv6Api
    _ctelbgwlbenableipv6api: CtelbGwlbEnableIpv6Api
    _ctelbgwlbenabledeleteprotectionapi: CtelbGwlbEnableDeleteProtectionApi
    _ctelbgwlbshowapi: CtelbGwlbShowApi
    _ctelbgwlblistapi: CtelbGwlbListApi
    _ctelbiplistenercreateapi: CtelbIplistenerCreateApi
    _ctelbiplistenerupdateapi: CtelbIplistenerUpdateApi
    _ctelbiplistenerdeleteapi: CtelbIplistenerDeleteApi
    _ctelbiplistenershowapi: CtelbIplistenerShowApi
    _ctelbiplistenerlistapi: CtelbIplistenerListApi
    _ctelbgwlbcreatetargetapi: CtelbGwlbCreateTargetApi
    _ctelbgwlbupdatetargetapi: CtelbGwlbUpdateTargetApi
    _ctelbgwlbdeletetargetapi: CtelbGwlbDeleteTargetApi
    _ctelbgwlbshowtargetapi: CtelbGwlbShowTargetApi
    _ctelbgwlblisttargetapi: CtelbGwlbListTargetApi
    _ctelbgwlbcreatetargetgroupapi: CtelbGwlbCreateTargetGroupApi
    _ctelbgwlbupdatetargetgroupapi: CtelbGwlbUpdateTargetGroupApi
    _ctelbgwlbdeletetargetgroupapi: CtelbGwlbDeleteTargetGroupApi
    _ctelbgwlbshowtargetgroupapi: CtelbGwlbShowTargetGroupApi
    _ctelbgwlblisttargetgroupapi: CtelbGwlbListTargetGroupApi
    _ctelbelbdisableidcapi: CtelbElbDisableIDCApi
    _ctelbelbenableidcapi: CtelbElbEnableIDCApi
    _ctelbelbmodifyaccesslogapi: CtelbElbModifyAccessLogApi
    _ctelbelbdeleteaccesslogapi: CtelbElbDeleteAccessLogApi
    _ctelbelbcreateaccesslogapi: CtelbElbCreateAccessLogApi
    _ctelbcreatepgelbapi: CtelbCreatePgelbApi
    _ctelbcreateloadbalancerapi: CtelbCreateLoadBalancerApi
    
    def __init__(self, endpoint_url: str, client: Optional[CtyunClient] = None):
        self.client = client or CtyunClient()
        self.endpoint = endpoint_url
    
        self._ctelbcheckservercertapi = CtelbCheckServerCertApi(self.client)
        self._ctelbcheckservercertapi.set_endpoint(self.endpoint)
        self._ctelbcheckcacertapi = CtelbCheckCaCertApi(self.client)
        self._ctelbcheckcacertapi.set_endpoint(self.endpoint)
        self._ctelblistdomaincertlinksapi = CtelbListDomainCertLinksApi(self.client)
        self._ctelblistdomaincertlinksapi.set_endpoint(self.endpoint)
        self._ctelbupdatedomaincertlinksapi = CtelbUpdateDomainCertLinksApi(self.client)
        self._ctelbupdatedomaincertlinksapi.set_endpoint(self.endpoint)
        self._ctelbdeletedomaincertlinksapi = CtelbDeleteDomainCertLinksApi(self.client)
        self._ctelbdeletedomaincertlinksapi.set_endpoint(self.endpoint)
        self._ctelbcreatedomaincertlinkapi = CtelbCreateDomainCertLinkApi(self.client)
        self._ctelbcreatedomaincertlinkapi.set_endpoint(self.endpoint)
        self._ctelbrefundpgelbapi = CtelbRefundPgelbApi(self.client)
        self._ctelbrefundpgelbapi.set_endpoint(self.endpoint)
        self._ctelbupdatelistenerresponsetimeoutapi = CtelbUpdateListenerResponseTimeoutApi(self.client)
        self._ctelbupdatelistenerresponsetimeoutapi.set_endpoint(self.endpoint)
        self._ctelbupdatelistenerqpsapi = CtelbUpdateListenerQpsApi(self.client)
        self._ctelbupdatelistenerqpsapi.set_endpoint(self.endpoint)
        self._ctelbupdatelistenernat64api = CtelbUpdateListenerNat64Api(self.client)
        self._ctelbupdatelistenernat64api.set_endpoint(self.endpoint)
        self._ctelbupdatelisteneridletimeoutapi = CtelbUpdateListenerIdleTimeoutApi(self.client)
        self._ctelbupdatelisteneridletimeoutapi.set_endpoint(self.endpoint)
        self._ctelbupdatelistenerestabtimeoutapi = CtelbUpdateListenerEstabTimeoutApi(self.client)
        self._ctelbupdatelistenerestabtimeoutapi.set_endpoint(self.endpoint)
        self._ctelbupdatelistenercpsapi = CtelbUpdateListenerCpsApi(self.client)
        self._ctelbupdatelistenercpsapi.set_endpoint(self.endpoint)
        self._ctelbelbunbindlabelsapi = CtelbElbUnbindLabelsApi(self.client)
        self._ctelbelbunbindlabelsapi.set_endpoint(self.endpoint)
        self._ctelbelbbindlabelsapi = CtelbElbBindLabelsApi(self.client)
        self._ctelbelbbindlabelsapi.set_endpoint(self.endpoint)
        self._ctelblistelblabelsapi = CtelbListElbLabelsApi(self.client)
        self._ctelblistelblabelsapi.set_endpoint(self.endpoint)
        self._ctelbupgradetopgelbapi = CtelbUpgradeToPgelbApi(self.client)
        self._ctelbupgradetopgelbapi.set_endpoint(self.endpoint)
        self._ctelbqueryrenewpgelbpriceapi = CtelbQueryRenewPgelbPriceApi(self.client)
        self._ctelbqueryrenewpgelbpriceapi.set_endpoint(self.endpoint)
        self._ctelbrenewpgelbapi = CtelbRenewPgelbApi(self.client)
        self._ctelbrenewpgelbapi.set_endpoint(self.endpoint)
        self._ctelbquerymodifypgelbspecpriceapi = CtelbQueryModifyPgelbSpecPriceApi(self.client)
        self._ctelbquerymodifypgelbspecpriceapi.set_endpoint(self.endpoint)
        self._ctelbmodifypgelbspecapi = CtelbModifyPgelbSpecApi(self.client)
        self._ctelbmodifypgelbspecapi.set_endpoint(self.endpoint)
        self._ctelbquerycreatepgelbpriceapi = CtelbQueryCreatePgelbPriceApi(self.client)
        self._ctelbquerycreatepgelbpriceapi.set_endpoint(self.endpoint)
        self._ctelbdeleteloadbalancerapi = CtelbDeleteLoadBalancerApi(self.client)
        self._ctelbdeleteloadbalancerapi.set_endpoint(self.endpoint)
        self._ctelbupdateloadbalancerapi = CtelbUpdateLoadBalancerApi(self.client)
        self._ctelbupdateloadbalancerapi.set_endpoint(self.endpoint)
        self._ctelbshowloadbalancerapi = CtelbShowLoadBalancerApi(self.client)
        self._ctelbshowloadbalancerapi.set_endpoint(self.endpoint)
        self._ctelblistloadbalancerapi = CtelbListLoadBalancerApi(self.client)
        self._ctelblistloadbalancerapi.set_endpoint(self.endpoint)
        self._ctelbassociateeiptoloadbalancerapi = CtelbAssociateEipToLoadBalancerApi(self.client)
        self._ctelbassociateeiptoloadbalancerapi.set_endpoint(self.endpoint)
        self._ctelbdisassociateeipfromloadbalancerapi = CtelbDisassociateEipFromLoadBalancerApi(self.client)
        self._ctelbdisassociateeipfromloadbalancerapi.set_endpoint(self.endpoint)
        self._ctelbcreatelistenerapi = CtelbCreateListenerApi(self.client)
        self._ctelbcreatelistenerapi.set_endpoint(self.endpoint)
        self._ctelbupdatelistenerapi = CtelbUpdateListenerApi(self.client)
        self._ctelbupdatelistenerapi.set_endpoint(self.endpoint)
        self._ctelbdeletelistenerapi = CtelbDeleteListenerApi(self.client)
        self._ctelbdeletelistenerapi.set_endpoint(self.endpoint)
        self._ctelbshowlistenerapi = CtelbShowListenerApi(self.client)
        self._ctelbshowlistenerapi.set_endpoint(self.endpoint)
        self._ctelblistlistenerapi = CtelbListListenerApi(self.client)
        self._ctelblistlistenerapi.set_endpoint(self.endpoint)
        self._ctelbstartlistenerapi = CtelbStartListenerApi(self.client)
        self._ctelbstartlistenerapi.set_endpoint(self.endpoint)
        self._ctelbstoplistenerapi = CtelbStopListenerApi(self.client)
        self._ctelbstoplistenerapi.set_endpoint(self.endpoint)
        self._ctelbcreatehealthcheckapi = CtelbCreateHealthCheckApi(self.client)
        self._ctelbcreatehealthcheckapi.set_endpoint(self.endpoint)
        self._ctelbcreatecertificateapi = CtelbCreateCertificateApi(self.client)
        self._ctelbcreatecertificateapi.set_endpoint(self.endpoint)
        self._ctelbupdatehealthcheckapi = CtelbUpdateHealthCheckApi(self.client)
        self._ctelbupdatehealthcheckapi.set_endpoint(self.endpoint)
        self._ctelbdeletehealthcheckapi = CtelbDeleteHealthCheckApi(self.client)
        self._ctelbdeletehealthcheckapi.set_endpoint(self.endpoint)
        self._ctelblisthealthcheckapi = CtelbListHealthCheckApi(self.client)
        self._ctelblisthealthcheckapi.set_endpoint(self.endpoint)
        self._ctelbdeletecertificateapi = CtelbDeleteCertificateApi(self.client)
        self._ctelbdeletecertificateapi.set_endpoint(self.endpoint)
        self._ctelbshowcertificateapi = CtelbShowCertificateApi(self.client)
        self._ctelbshowcertificateapi.set_endpoint(self.endpoint)
        self._ctelblistcertificateapi = CtelbListCertificateApi(self.client)
        self._ctelblistcertificateapi.set_endpoint(self.endpoint)
        self._ctelbcreateaccesscontrolapi = CtelbCreateAccessControlApi(self.client)
        self._ctelbcreateaccesscontrolapi.set_endpoint(self.endpoint)
        self._ctelbdeleteaccesscontrolapi = CtelbDeleteAccessControlApi(self.client)
        self._ctelbdeleteaccesscontrolapi.set_endpoint(self.endpoint)
        self._ctelbupdateaccesscontrolapi = CtelbUpdateAccessControlApi(self.client)
        self._ctelbupdateaccesscontrolapi.set_endpoint(self.endpoint)
        self._ctelblistaccesscontrolapi = CtelbListAccessControlApi(self.client)
        self._ctelblistaccesscontrolapi.set_endpoint(self.endpoint)
        self._ctelbdeleteruleapi = CtelbDeleteRuleApi(self.client)
        self._ctelbdeleteruleapi.set_endpoint(self.endpoint)
        self._ctelbcreateruleapi = CtelbCreateRuleApi(self.client)
        self._ctelbcreateruleapi.set_endpoint(self.endpoint)
        self._ctelbupdateruleapi = CtelbUpdateRuleApi(self.client)
        self._ctelbupdateruleapi.set_endpoint(self.endpoint)
        self._ctelbshowruleapi = CtelbShowRuleApi(self.client)
        self._ctelbshowruleapi.set_endpoint(self.endpoint)
        self._ctelblistqueryapi = CtelbListQueryApi(self.client)
        self._ctelblistqueryapi.set_endpoint(self.endpoint)
        self._ctelbqueryslaapi = CtelbQuerySlaApi(self.client)
        self._ctelbqueryslaapi.set_endpoint(self.endpoint)
        self._ctelbqueryelbreatimemetricapi = CtelbQueryElbReatimeMetricApi(self.client)
        self._ctelbqueryelbreatimemetricapi.set_endpoint(self.endpoint)
        self._ctelbshowhealthcheckapi = CtelbShowHealthCheckApi(self.client)
        self._ctelbshowhealthcheckapi.set_endpoint(self.endpoint)
        self._ctelbshowaccesscontrolapi = CtelbShowAccessControlApi(self.client)
        self._ctelbshowaccesscontrolapi.set_endpoint(self.endpoint)
        self._ctelbdisableelbipv6api = CtelbDisableElbIpv6Api(self.client)
        self._ctelbdisableelbipv6api.set_endpoint(self.endpoint)
        self._ctelbenableelbipv6api = CtelbEnableElbIpv6Api(self.client)
        self._ctelbenableelbipv6api.set_endpoint(self.endpoint)
        self._ctelbupdatecertificateapi = CtelbUpdateCertificateApi(self.client)
        self._ctelbupdatecertificateapi.set_endpoint(self.endpoint)
        self._ctelbqueryelbhistorymetricapi = CtelbQueryElbHistoryMetricApi(self.client)
        self._ctelbqueryelbhistorymetricapi.set_endpoint(self.endpoint)
        self._ctelbasynccreateloadbalanceapi = CtelbAsyncCreateLoadbalanceApi(self.client)
        self._ctelbasynccreateloadbalanceapi.set_endpoint(self.endpoint)
        self._ctelbasynccreatecertificateapi = CtelbAsyncCreateCertificateApi(self.client)
        self._ctelbasynccreatecertificateapi.set_endpoint(self.endpoint)
        self._ctelblistvmpoolapi = CtelbListVmPoolApi(self.client)
        self._ctelblistvmpoolapi.set_endpoint(self.endpoint)
        self._ctelbasynccreatelistenerapi = CtelbAsyncCreateListenerApi(self.client)
        self._ctelbasynccreatelistenerapi.set_endpoint(self.endpoint)
        self._ctelbupdatelistenerattrapi = CtelbUpdateListenerAttrApi(self.client)
        self._ctelbupdatelistenerattrapi.set_endpoint(self.endpoint)
        self._ctelbasynccreatepolicyapi = CtelbAsyncCreatePolicyApi(self.client)
        self._ctelbasynccreatepolicyapi.set_endpoint(self.endpoint)
        self._ctelbnewqueryelbhistorymonitorapi = CtelbNewQueryElbHistoryMonitorApi(self.client)
        self._ctelbnewqueryelbhistorymonitorapi.set_endpoint(self.endpoint)
        self._ctelbupdatepolicyattrapi = CtelbUpdatePolicyAttrApi(self.client)
        self._ctelbupdatepolicyattrapi.set_endpoint(self.endpoint)
        self._ctelbnewqueryelbreatimemonitorapi = CtelbNewQueryElbReatimeMonitorApi(self.client)
        self._ctelbnewqueryelbreatimemonitorapi.set_endpoint(self.endpoint)
        self._ctelbremovevmapi = CtelbRemoveVmApi(self.client)
        self._ctelbremovevmapi.set_endpoint(self.endpoint)
        self._ctelblistvmapi = CtelbListVmApi(self.client)
        self._ctelblistvmapi.set_endpoint(self.endpoint)
        self._ctelbasynccreatetargetapi = CtelbAsyncCreateTargetApi(self.client)
        self._ctelbasynccreatetargetapi.set_endpoint(self.endpoint)
        self._ctelblisttargetapi = CtelbListTargetApi(self.client)
        self._ctelblisttargetapi.set_endpoint(self.endpoint)
        self._ctelbshowtargetapi = CtelbShowTargetApi(self.client)
        self._ctelbshowtargetapi.set_endpoint(self.endpoint)
        self._ctelbupdatetargetapi = CtelbUpdateTargetApi(self.client)
        self._ctelbupdatetargetapi.set_endpoint(self.endpoint)
        self._ctelbdeletetargetapi = CtelbDeleteTargetApi(self.client)
        self._ctelbdeletetargetapi.set_endpoint(self.endpoint)
        self._ctelbcreatetargetapi = CtelbCreateTargetApi(self.client)
        self._ctelbcreatetargetapi.set_endpoint(self.endpoint)
        self._ctelblisttargetgroupapi = CtelbListTargetGroupApi(self.client)
        self._ctelblisttargetgroupapi.set_endpoint(self.endpoint)
        self._ctelbshowtargetgroupapi = CtelbShowTargetGroupApi(self.client)
        self._ctelbshowtargetgroupapi.set_endpoint(self.endpoint)
        self._ctelbdeletetargetgroupapi = CtelbDeleteTargetGroupApi(self.client)
        self._ctelbdeletetargetgroupapi.set_endpoint(self.endpoint)
        self._ctelbupdatetargetgroupapi = CtelbUpdateTargetGroupApi(self.client)
        self._ctelbupdatetargetgroupapi.set_endpoint(self.endpoint)
        self._ctelbcreatetargetgroupapi = CtelbCreateTargetGroupApi(self.client)
        self._ctelbcreatetargetgroupapi.set_endpoint(self.endpoint)
        self._ctelbupdatevmpoolattrapi = CtelbUpdateVmPoolAttrApi(self.client)
        self._ctelbupdatevmpoolattrapi.set_endpoint(self.endpoint)
        self._ctelbgwlbcreateapi = CtelbGwlbCreateApi(self.client)
        self._ctelbgwlbcreateapi.set_endpoint(self.endpoint)
        self._ctelbgwlbupdateapi = CtelbGwlbUpdateApi(self.client)
        self._ctelbgwlbupdateapi.set_endpoint(self.endpoint)
        self._ctelbgwlbdeleteapi = CtelbGwlbDeleteApi(self.client)
        self._ctelbgwlbdeleteapi.set_endpoint(self.endpoint)
        self._ctelbgwlbdisabledeleteprotectionapi = CtelbGwlbDisableDeleteProtectionApi(self.client)
        self._ctelbgwlbdisabledeleteprotectionapi.set_endpoint(self.endpoint)
        self._ctelbgwlbdisableipv6api = CtelbGwlbDisableIpv6Api(self.client)
        self._ctelbgwlbdisableipv6api.set_endpoint(self.endpoint)
        self._ctelbgwlbenableipv6api = CtelbGwlbEnableIpv6Api(self.client)
        self._ctelbgwlbenableipv6api.set_endpoint(self.endpoint)
        self._ctelbgwlbenabledeleteprotectionapi = CtelbGwlbEnableDeleteProtectionApi(self.client)
        self._ctelbgwlbenabledeleteprotectionapi.set_endpoint(self.endpoint)
        self._ctelbgwlbshowapi = CtelbGwlbShowApi(self.client)
        self._ctelbgwlbshowapi.set_endpoint(self.endpoint)
        self._ctelbgwlblistapi = CtelbGwlbListApi(self.client)
        self._ctelbgwlblistapi.set_endpoint(self.endpoint)
        self._ctelbiplistenercreateapi = CtelbIplistenerCreateApi(self.client)
        self._ctelbiplistenercreateapi.set_endpoint(self.endpoint)
        self._ctelbiplistenerupdateapi = CtelbIplistenerUpdateApi(self.client)
        self._ctelbiplistenerupdateapi.set_endpoint(self.endpoint)
        self._ctelbiplistenerdeleteapi = CtelbIplistenerDeleteApi(self.client)
        self._ctelbiplistenerdeleteapi.set_endpoint(self.endpoint)
        self._ctelbiplistenershowapi = CtelbIplistenerShowApi(self.client)
        self._ctelbiplistenershowapi.set_endpoint(self.endpoint)
        self._ctelbiplistenerlistapi = CtelbIplistenerListApi(self.client)
        self._ctelbiplistenerlistapi.set_endpoint(self.endpoint)
        self._ctelbgwlbcreatetargetapi = CtelbGwlbCreateTargetApi(self.client)
        self._ctelbgwlbcreatetargetapi.set_endpoint(self.endpoint)
        self._ctelbgwlbupdatetargetapi = CtelbGwlbUpdateTargetApi(self.client)
        self._ctelbgwlbupdatetargetapi.set_endpoint(self.endpoint)
        self._ctelbgwlbdeletetargetapi = CtelbGwlbDeleteTargetApi(self.client)
        self._ctelbgwlbdeletetargetapi.set_endpoint(self.endpoint)
        self._ctelbgwlbshowtargetapi = CtelbGwlbShowTargetApi(self.client)
        self._ctelbgwlbshowtargetapi.set_endpoint(self.endpoint)
        self._ctelbgwlblisttargetapi = CtelbGwlbListTargetApi(self.client)
        self._ctelbgwlblisttargetapi.set_endpoint(self.endpoint)
        self._ctelbgwlbcreatetargetgroupapi = CtelbGwlbCreateTargetGroupApi(self.client)
        self._ctelbgwlbcreatetargetgroupapi.set_endpoint(self.endpoint)
        self._ctelbgwlbupdatetargetgroupapi = CtelbGwlbUpdateTargetGroupApi(self.client)
        self._ctelbgwlbupdatetargetgroupapi.set_endpoint(self.endpoint)
        self._ctelbgwlbdeletetargetgroupapi = CtelbGwlbDeleteTargetGroupApi(self.client)
        self._ctelbgwlbdeletetargetgroupapi.set_endpoint(self.endpoint)
        self._ctelbgwlbshowtargetgroupapi = CtelbGwlbShowTargetGroupApi(self.client)
        self._ctelbgwlbshowtargetgroupapi.set_endpoint(self.endpoint)
        self._ctelbgwlblisttargetgroupapi = CtelbGwlbListTargetGroupApi(self.client)
        self._ctelbgwlblisttargetgroupapi.set_endpoint(self.endpoint)
        self._ctelbelbdisableidcapi = CtelbElbDisableIDCApi(self.client)
        self._ctelbelbdisableidcapi.set_endpoint(self.endpoint)
        self._ctelbelbenableidcapi = CtelbElbEnableIDCApi(self.client)
        self._ctelbelbenableidcapi.set_endpoint(self.endpoint)
        self._ctelbelbmodifyaccesslogapi = CtelbElbModifyAccessLogApi(self.client)
        self._ctelbelbmodifyaccesslogapi.set_endpoint(self.endpoint)
        self._ctelbelbdeleteaccesslogapi = CtelbElbDeleteAccessLogApi(self.client)
        self._ctelbelbdeleteaccesslogapi.set_endpoint(self.endpoint)
        self._ctelbelbcreateaccesslogapi = CtelbElbCreateAccessLogApi(self.client)
        self._ctelbelbcreateaccesslogapi.set_endpoint(self.endpoint)
        self._ctelbcreatepgelbapi = CtelbCreatePgelbApi(self.client)
        self._ctelbcreatepgelbapi.set_endpoint(self.endpoint)
        self._ctelbcreateloadbalancerapi = CtelbCreateLoadBalancerApi(self.client)
        self._ctelbcreateloadbalancerapi.set_endpoint(self.endpoint)
    
    @property  # noqa
    def ctelbcheckservercertapi(self) -> CtelbCheckServerCertApi:  # noqa
        return self._ctelbcheckservercertapi
        
    @property  # noqa
    def ctelbcheckcacertapi(self) -> CtelbCheckCaCertApi:  # noqa
        return self._ctelbcheckcacertapi
        
    @property  # noqa
    def ctelblistdomaincertlinksapi(self) -> CtelbListDomainCertLinksApi:  # noqa
        return self._ctelblistdomaincertlinksapi
        
    @property  # noqa
    def ctelbupdatedomaincertlinksapi(self) -> CtelbUpdateDomainCertLinksApi:  # noqa
        return self._ctelbupdatedomaincertlinksapi
        
    @property  # noqa
    def ctelbdeletedomaincertlinksapi(self) -> CtelbDeleteDomainCertLinksApi:  # noqa
        return self._ctelbdeletedomaincertlinksapi
        
    @property  # noqa
    def ctelbcreatedomaincertlinkapi(self) -> CtelbCreateDomainCertLinkApi:  # noqa
        return self._ctelbcreatedomaincertlinkapi
        
    @property  # noqa
    def ctelbrefundpgelbapi(self) -> CtelbRefundPgelbApi:  # noqa
        return self._ctelbrefundpgelbapi
        
    @property  # noqa
    def ctelbupdatelistenerresponsetimeoutapi(self) -> CtelbUpdateListenerResponseTimeoutApi:  # noqa
        return self._ctelbupdatelistenerresponsetimeoutapi
        
    @property  # noqa
    def ctelbupdatelistenerqpsapi(self) -> CtelbUpdateListenerQpsApi:  # noqa
        return self._ctelbupdatelistenerqpsapi
        
    @property  # noqa
    def ctelbupdatelistenernat64api(self) -> CtelbUpdateListenerNat64Api:  # noqa
        return self._ctelbupdatelistenernat64api
        
    @property  # noqa
    def ctelbupdatelisteneridletimeoutapi(self) -> CtelbUpdateListenerIdleTimeoutApi:  # noqa
        return self._ctelbupdatelisteneridletimeoutapi
        
    @property  # noqa
    def ctelbupdatelistenerestabtimeoutapi(self) -> CtelbUpdateListenerEstabTimeoutApi:  # noqa
        return self._ctelbupdatelistenerestabtimeoutapi
        
    @property  # noqa
    def ctelbupdatelistenercpsapi(self) -> CtelbUpdateListenerCpsApi:  # noqa
        return self._ctelbupdatelistenercpsapi
        
    @property  # noqa
    def ctelbelbunbindlabelsapi(self) -> CtelbElbUnbindLabelsApi:  # noqa
        return self._ctelbelbunbindlabelsapi
        
    @property  # noqa
    def ctelbelbbindlabelsapi(self) -> CtelbElbBindLabelsApi:  # noqa
        return self._ctelbelbbindlabelsapi
        
    @property  # noqa
    def ctelblistelblabelsapi(self) -> CtelbListElbLabelsApi:  # noqa
        return self._ctelblistelblabelsapi
        
    @property  # noqa
    def ctelbupgradetopgelbapi(self) -> CtelbUpgradeToPgelbApi:  # noqa
        return self._ctelbupgradetopgelbapi
        
    @property  # noqa
    def ctelbqueryrenewpgelbpriceapi(self) -> CtelbQueryRenewPgelbPriceApi:  # noqa
        return self._ctelbqueryrenewpgelbpriceapi
        
    @property  # noqa
    def ctelbrenewpgelbapi(self) -> CtelbRenewPgelbApi:  # noqa
        return self._ctelbrenewpgelbapi
        
    @property  # noqa
    def ctelbquerymodifypgelbspecpriceapi(self) -> CtelbQueryModifyPgelbSpecPriceApi:  # noqa
        return self._ctelbquerymodifypgelbspecpriceapi
        
    @property  # noqa
    def ctelbmodifypgelbspecapi(self) -> CtelbModifyPgelbSpecApi:  # noqa
        return self._ctelbmodifypgelbspecapi
        
    @property  # noqa
    def ctelbquerycreatepgelbpriceapi(self) -> CtelbQueryCreatePgelbPriceApi:  # noqa
        return self._ctelbquerycreatepgelbpriceapi
        
    @property  # noqa
    def ctelbdeleteloadbalancerapi(self) -> CtelbDeleteLoadBalancerApi:  # noqa
        return self._ctelbdeleteloadbalancerapi
        
    @property  # noqa
    def ctelbupdateloadbalancerapi(self) -> CtelbUpdateLoadBalancerApi:  # noqa
        return self._ctelbupdateloadbalancerapi
        
    @property  # noqa
    def ctelbshowloadbalancerapi(self) -> CtelbShowLoadBalancerApi:  # noqa
        return self._ctelbshowloadbalancerapi
        
    @property  # noqa
    def ctelblistloadbalancerapi(self) -> CtelbListLoadBalancerApi:  # noqa
        return self._ctelblistloadbalancerapi
        
    @property  # noqa
    def ctelbassociateeiptoloadbalancerapi(self) -> CtelbAssociateEipToLoadBalancerApi:  # noqa
        return self._ctelbassociateeiptoloadbalancerapi
        
    @property  # noqa
    def ctelbdisassociateeipfromloadbalancerapi(self) -> CtelbDisassociateEipFromLoadBalancerApi:  # noqa
        return self._ctelbdisassociateeipfromloadbalancerapi
        
    @property  # noqa
    def ctelbcreatelistenerapi(self) -> CtelbCreateListenerApi:  # noqa
        return self._ctelbcreatelistenerapi
        
    @property  # noqa
    def ctelbupdatelistenerapi(self) -> CtelbUpdateListenerApi:  # noqa
        return self._ctelbupdatelistenerapi
        
    @property  # noqa
    def ctelbdeletelistenerapi(self) -> CtelbDeleteListenerApi:  # noqa
        return self._ctelbdeletelistenerapi
        
    @property  # noqa
    def ctelbshowlistenerapi(self) -> CtelbShowListenerApi:  # noqa
        return self._ctelbshowlistenerapi
        
    @property  # noqa
    def ctelblistlistenerapi(self) -> CtelbListListenerApi:  # noqa
        return self._ctelblistlistenerapi
        
    @property  # noqa
    def ctelbstartlistenerapi(self) -> CtelbStartListenerApi:  # noqa
        return self._ctelbstartlistenerapi
        
    @property  # noqa
    def ctelbstoplistenerapi(self) -> CtelbStopListenerApi:  # noqa
        return self._ctelbstoplistenerapi
        
    @property  # noqa
    def ctelbcreatehealthcheckapi(self) -> CtelbCreateHealthCheckApi:  # noqa
        return self._ctelbcreatehealthcheckapi
        
    @property  # noqa
    def ctelbcreatecertificateapi(self) -> CtelbCreateCertificateApi:  # noqa
        return self._ctelbcreatecertificateapi
        
    @property  # noqa
    def ctelbupdatehealthcheckapi(self) -> CtelbUpdateHealthCheckApi:  # noqa
        return self._ctelbupdatehealthcheckapi
        
    @property  # noqa
    def ctelbdeletehealthcheckapi(self) -> CtelbDeleteHealthCheckApi:  # noqa
        return self._ctelbdeletehealthcheckapi
        
    @property  # noqa
    def ctelblisthealthcheckapi(self) -> CtelbListHealthCheckApi:  # noqa
        return self._ctelblisthealthcheckapi
        
    @property  # noqa
    def ctelbdeletecertificateapi(self) -> CtelbDeleteCertificateApi:  # noqa
        return self._ctelbdeletecertificateapi
        
    @property  # noqa
    def ctelbshowcertificateapi(self) -> CtelbShowCertificateApi:  # noqa
        return self._ctelbshowcertificateapi
        
    @property  # noqa
    def ctelblistcertificateapi(self) -> CtelbListCertificateApi:  # noqa
        return self._ctelblistcertificateapi
        
    @property  # noqa
    def ctelbcreateaccesscontrolapi(self) -> CtelbCreateAccessControlApi:  # noqa
        return self._ctelbcreateaccesscontrolapi
        
    @property  # noqa
    def ctelbdeleteaccesscontrolapi(self) -> CtelbDeleteAccessControlApi:  # noqa
        return self._ctelbdeleteaccesscontrolapi
        
    @property  # noqa
    def ctelbupdateaccesscontrolapi(self) -> CtelbUpdateAccessControlApi:  # noqa
        return self._ctelbupdateaccesscontrolapi
        
    @property  # noqa
    def ctelblistaccesscontrolapi(self) -> CtelbListAccessControlApi:  # noqa
        return self._ctelblistaccesscontrolapi
        
    @property  # noqa
    def ctelbdeleteruleapi(self) -> CtelbDeleteRuleApi:  # noqa
        return self._ctelbdeleteruleapi
        
    @property  # noqa
    def ctelbcreateruleapi(self) -> CtelbCreateRuleApi:  # noqa
        return self._ctelbcreateruleapi
        
    @property  # noqa
    def ctelbupdateruleapi(self) -> CtelbUpdateRuleApi:  # noqa
        return self._ctelbupdateruleapi
        
    @property  # noqa
    def ctelbshowruleapi(self) -> CtelbShowRuleApi:  # noqa
        return self._ctelbshowruleapi
        
    @property  # noqa
    def ctelblistqueryapi(self) -> CtelbListQueryApi:  # noqa
        return self._ctelblistqueryapi
        
    @property  # noqa
    def ctelbqueryslaapi(self) -> CtelbQuerySlaApi:  # noqa
        return self._ctelbqueryslaapi
        
    @property  # noqa
    def ctelbqueryelbreatimemetricapi(self) -> CtelbQueryElbReatimeMetricApi:  # noqa
        return self._ctelbqueryelbreatimemetricapi
        
    @property  # noqa
    def ctelbshowhealthcheckapi(self) -> CtelbShowHealthCheckApi:  # noqa
        return self._ctelbshowhealthcheckapi
        
    @property  # noqa
    def ctelbshowaccesscontrolapi(self) -> CtelbShowAccessControlApi:  # noqa
        return self._ctelbshowaccesscontrolapi
        
    @property  # noqa
    def ctelbdisableelbipv6api(self) -> CtelbDisableElbIpv6Api:  # noqa
        return self._ctelbdisableelbipv6api
        
    @property  # noqa
    def ctelbenableelbipv6api(self) -> CtelbEnableElbIpv6Api:  # noqa
        return self._ctelbenableelbipv6api
        
    @property  # noqa
    def ctelbupdatecertificateapi(self) -> CtelbUpdateCertificateApi:  # noqa
        return self._ctelbupdatecertificateapi
        
    @property  # noqa
    def ctelbqueryelbhistorymetricapi(self) -> CtelbQueryElbHistoryMetricApi:  # noqa
        return self._ctelbqueryelbhistorymetricapi
        
    @property  # noqa
    def ctelbasynccreateloadbalanceapi(self) -> CtelbAsyncCreateLoadbalanceApi:  # noqa
        return self._ctelbasynccreateloadbalanceapi
        
    @property  # noqa
    def ctelbasynccreatecertificateapi(self) -> CtelbAsyncCreateCertificateApi:  # noqa
        return self._ctelbasynccreatecertificateapi
        
    @property  # noqa
    def ctelblistvmpoolapi(self) -> CtelbListVmPoolApi:  # noqa
        return self._ctelblistvmpoolapi
        
    @property  # noqa
    def ctelbasynccreatelistenerapi(self) -> CtelbAsyncCreateListenerApi:  # noqa
        return self._ctelbasynccreatelistenerapi
        
    @property  # noqa
    def ctelbupdatelistenerattrapi(self) -> CtelbUpdateListenerAttrApi:  # noqa
        return self._ctelbupdatelistenerattrapi
        
    @property  # noqa
    def ctelbasynccreatepolicyapi(self) -> CtelbAsyncCreatePolicyApi:  # noqa
        return self._ctelbasynccreatepolicyapi
        
    @property  # noqa
    def ctelbnewqueryelbhistorymonitorapi(self) -> CtelbNewQueryElbHistoryMonitorApi:  # noqa
        return self._ctelbnewqueryelbhistorymonitorapi
        
    @property  # noqa
    def ctelbupdatepolicyattrapi(self) -> CtelbUpdatePolicyAttrApi:  # noqa
        return self._ctelbupdatepolicyattrapi
        
    @property  # noqa
    def ctelbnewqueryelbreatimemonitorapi(self) -> CtelbNewQueryElbReatimeMonitorApi:  # noqa
        return self._ctelbnewqueryelbreatimemonitorapi
        
    @property  # noqa
    def ctelbremovevmapi(self) -> CtelbRemoveVmApi:  # noqa
        return self._ctelbremovevmapi
        
    @property  # noqa
    def ctelblistvmapi(self) -> CtelbListVmApi:  # noqa
        return self._ctelblistvmapi
        
    @property  # noqa
    def ctelbasynccreatetargetapi(self) -> CtelbAsyncCreateTargetApi:  # noqa
        return self._ctelbasynccreatetargetapi
        
    @property  # noqa
    def ctelblisttargetapi(self) -> CtelbListTargetApi:  # noqa
        return self._ctelblisttargetapi
        
    @property  # noqa
    def ctelbshowtargetapi(self) -> CtelbShowTargetApi:  # noqa
        return self._ctelbshowtargetapi
        
    @property  # noqa
    def ctelbupdatetargetapi(self) -> CtelbUpdateTargetApi:  # noqa
        return self._ctelbupdatetargetapi
        
    @property  # noqa
    def ctelbdeletetargetapi(self) -> CtelbDeleteTargetApi:  # noqa
        return self._ctelbdeletetargetapi
        
    @property  # noqa
    def ctelbcreatetargetapi(self) -> CtelbCreateTargetApi:  # noqa
        return self._ctelbcreatetargetapi
        
    @property  # noqa
    def ctelblisttargetgroupapi(self) -> CtelbListTargetGroupApi:  # noqa
        return self._ctelblisttargetgroupapi
        
    @property  # noqa
    def ctelbshowtargetgroupapi(self) -> CtelbShowTargetGroupApi:  # noqa
        return self._ctelbshowtargetgroupapi
        
    @property  # noqa
    def ctelbdeletetargetgroupapi(self) -> CtelbDeleteTargetGroupApi:  # noqa
        return self._ctelbdeletetargetgroupapi
        
    @property  # noqa
    def ctelbupdatetargetgroupapi(self) -> CtelbUpdateTargetGroupApi:  # noqa
        return self._ctelbupdatetargetgroupapi
        
    @property  # noqa
    def ctelbcreatetargetgroupapi(self) -> CtelbCreateTargetGroupApi:  # noqa
        return self._ctelbcreatetargetgroupapi
        
    @property  # noqa
    def ctelbupdatevmpoolattrapi(self) -> CtelbUpdateVmPoolAttrApi:  # noqa
        return self._ctelbupdatevmpoolattrapi
        
    @property  # noqa
    def ctelbgwlbcreateapi(self) -> CtelbGwlbCreateApi:  # noqa
        return self._ctelbgwlbcreateapi
        
    @property  # noqa
    def ctelbgwlbupdateapi(self) -> CtelbGwlbUpdateApi:  # noqa
        return self._ctelbgwlbupdateapi
        
    @property  # noqa
    def ctelbgwlbdeleteapi(self) -> CtelbGwlbDeleteApi:  # noqa
        return self._ctelbgwlbdeleteapi
        
    @property  # noqa
    def ctelbgwlbdisabledeleteprotectionapi(self) -> CtelbGwlbDisableDeleteProtectionApi:  # noqa
        return self._ctelbgwlbdisabledeleteprotectionapi
        
    @property  # noqa
    def ctelbgwlbdisableipv6api(self) -> CtelbGwlbDisableIpv6Api:  # noqa
        return self._ctelbgwlbdisableipv6api
        
    @property  # noqa
    def ctelbgwlbenableipv6api(self) -> CtelbGwlbEnableIpv6Api:  # noqa
        return self._ctelbgwlbenableipv6api
        
    @property  # noqa
    def ctelbgwlbenabledeleteprotectionapi(self) -> CtelbGwlbEnableDeleteProtectionApi:  # noqa
        return self._ctelbgwlbenabledeleteprotectionapi
        
    @property  # noqa
    def ctelbgwlbshowapi(self) -> CtelbGwlbShowApi:  # noqa
        return self._ctelbgwlbshowapi
        
    @property  # noqa
    def ctelbgwlblistapi(self) -> CtelbGwlbListApi:  # noqa
        return self._ctelbgwlblistapi
        
    @property  # noqa
    def ctelbiplistenercreateapi(self) -> CtelbIplistenerCreateApi:  # noqa
        return self._ctelbiplistenercreateapi
        
    @property  # noqa
    def ctelbiplistenerupdateapi(self) -> CtelbIplistenerUpdateApi:  # noqa
        return self._ctelbiplistenerupdateapi
        
    @property  # noqa
    def ctelbiplistenerdeleteapi(self) -> CtelbIplistenerDeleteApi:  # noqa
        return self._ctelbiplistenerdeleteapi
        
    @property  # noqa
    def ctelbiplistenershowapi(self) -> CtelbIplistenerShowApi:  # noqa
        return self._ctelbiplistenershowapi
        
    @property  # noqa
    def ctelbiplistenerlistapi(self) -> CtelbIplistenerListApi:  # noqa
        return self._ctelbiplistenerlistapi
        
    @property  # noqa
    def ctelbgwlbcreatetargetapi(self) -> CtelbGwlbCreateTargetApi:  # noqa
        return self._ctelbgwlbcreatetargetapi
        
    @property  # noqa
    def ctelbgwlbupdatetargetapi(self) -> CtelbGwlbUpdateTargetApi:  # noqa
        return self._ctelbgwlbupdatetargetapi
        
    @property  # noqa
    def ctelbgwlbdeletetargetapi(self) -> CtelbGwlbDeleteTargetApi:  # noqa
        return self._ctelbgwlbdeletetargetapi
        
    @property  # noqa
    def ctelbgwlbshowtargetapi(self) -> CtelbGwlbShowTargetApi:  # noqa
        return self._ctelbgwlbshowtargetapi
        
    @property  # noqa
    def ctelbgwlblisttargetapi(self) -> CtelbGwlbListTargetApi:  # noqa
        return self._ctelbgwlblisttargetapi
        
    @property  # noqa
    def ctelbgwlbcreatetargetgroupapi(self) -> CtelbGwlbCreateTargetGroupApi:  # noqa
        return self._ctelbgwlbcreatetargetgroupapi
        
    @property  # noqa
    def ctelbgwlbupdatetargetgroupapi(self) -> CtelbGwlbUpdateTargetGroupApi:  # noqa
        return self._ctelbgwlbupdatetargetgroupapi
        
    @property  # noqa
    def ctelbgwlbdeletetargetgroupapi(self) -> CtelbGwlbDeleteTargetGroupApi:  # noqa
        return self._ctelbgwlbdeletetargetgroupapi
        
    @property  # noqa
    def ctelbgwlbshowtargetgroupapi(self) -> CtelbGwlbShowTargetGroupApi:  # noqa
        return self._ctelbgwlbshowtargetgroupapi
        
    @property  # noqa
    def ctelbgwlblisttargetgroupapi(self) -> CtelbGwlbListTargetGroupApi:  # noqa
        return self._ctelbgwlblisttargetgroupapi
        
    @property  # noqa
    def ctelbelbdisableidcapi(self) -> CtelbElbDisableIDCApi:  # noqa
        return self._ctelbelbdisableidcapi
        
    @property  # noqa
    def ctelbelbenableidcapi(self) -> CtelbElbEnableIDCApi:  # noqa
        return self._ctelbelbenableidcapi
        
    @property  # noqa
    def ctelbelbmodifyaccesslogapi(self) -> CtelbElbModifyAccessLogApi:  # noqa
        return self._ctelbelbmodifyaccesslogapi
        
    @property  # noqa
    def ctelbelbdeleteaccesslogapi(self) -> CtelbElbDeleteAccessLogApi:  # noqa
        return self._ctelbelbdeleteaccesslogapi
        
    @property  # noqa
    def ctelbelbcreateaccesslogapi(self) -> CtelbElbCreateAccessLogApi:  # noqa
        return self._ctelbelbcreateaccesslogapi
        
    @property  # noqa
    def ctelbcreatepgelbapi(self) -> CtelbCreatePgelbApi:  # noqa
        return self._ctelbcreatepgelbapi
        
    @property  # noqa
    def ctelbcreateloadbalancerapi(self) -> CtelbCreateLoadBalancerApi:  # noqa
        return self._ctelbcreateloadbalancerapi
        
