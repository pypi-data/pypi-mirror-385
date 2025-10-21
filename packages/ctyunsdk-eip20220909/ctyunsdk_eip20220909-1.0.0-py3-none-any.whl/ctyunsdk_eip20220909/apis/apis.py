from typing import Optional
from ctyunsdk_eip20220909.core.client import CtyunClient
from ctyunsdk_eip20220909.core.credential import Credential

from .ctvpc_eip_query_modify_price_api import CtvpcEipQueryModifyPriceApi
from .ctvpc_eip_query_create_price_api import CtvpcEipQueryCreatePriceApi
from .ctvpc_attach_port_bm_api import CtvpcAttachPortBmApi
from .ctvpc_new_eip_list_api import CtvpcNewEipListApi
from .ctvpc_create_eip_with_ip_address_api import CtvpcCreateEipWithIpAddressApi
from .ctvpc_get_eip_filing_status_api import CtvpcGetEipFilingStatusApi
from .ctvpc_change_eip_name_api import CtvpcChangeEipNameApi
from .ctvpc_batch_check_eip_address_api import CtvpcBatchCheckEipAddressApi
from .ctvpc_show_eip_api import CtvpcShowEipApi
from .ctvpc_attach_eip_to_port_api import CtvpcAttachEipToPortApi
from .ctvpc_disassociate_eip_api import CtvpcDisassociateEipApi
from .ctvpc_modify_eip_spec_api import CtvpcModifyEipSpecApi
from .ctvpc_associate_eip_api import CtvpcAssociateEipApi
from .ctvpc_renew_eip_api import CtvpcRenewEipApi
from .ctvpc_create_eip_api import CtvpcCreateEipApi
from .ctvpc_delete_eip_api import CtvpcDeleteEipApi
from .ctvpc_list_eip_api import CtvpcListEipApi
from .ctvpc_eip_ingerss_bandwidth_utilization_api import CtvpcEipIngerssBandwidthUtilizationApi
from .ctvpc_eip_egerss_bandwidth_utilization_api import CtvpcEipEgerssBandwidthUtilizationApi
from .ctvpc_eip_bandwidth_utilization_api import CtvpcEipBandwidthUtilizationApi
from .ctvpc_check_eip_address_api import CtvpcCheckEipAddressApi
from .ctvpc_eip_query_renew_price_api import CtvpcEipQueryRenewPriceApi


ENDPOINT_NAME = "ctvpc"


class Apis:
    _ctvpceipquerymodifypriceapi: CtvpcEipQueryModifyPriceApi
    _ctvpceipquerycreatepriceapi: CtvpcEipQueryCreatePriceApi
    _ctvpcattachportbmapi: CtvpcAttachPortBmApi
    _ctvpcneweiplistapi: CtvpcNewEipListApi
    _ctvpccreateeipwithipaddressapi: CtvpcCreateEipWithIpAddressApi
    _ctvpcgeteipfilingstatusapi: CtvpcGetEipFilingStatusApi
    _ctvpcchangeeipnameapi: CtvpcChangeEipNameApi
    _ctvpcbatchcheckeipaddressapi: CtvpcBatchCheckEipAddressApi
    _ctvpcshoweipapi: CtvpcShowEipApi
    _ctvpcattacheiptoportapi: CtvpcAttachEipToPortApi
    _ctvpcdisassociateeipapi: CtvpcDisassociateEipApi
    _ctvpcmodifyeipspecapi: CtvpcModifyEipSpecApi
    _ctvpcassociateeipapi: CtvpcAssociateEipApi
    _ctvpcreneweipapi: CtvpcRenewEipApi
    _ctvpccreateeipapi: CtvpcCreateEipApi
    _ctvpcdeleteeipapi: CtvpcDeleteEipApi
    _ctvpclisteipapi: CtvpcListEipApi
    _ctvpceipingerssbandwidthutilizationapi: CtvpcEipIngerssBandwidthUtilizationApi
    _ctvpceipegerssbandwidthutilizationapi: CtvpcEipEgerssBandwidthUtilizationApi
    _ctvpceipbandwidthutilizationapi: CtvpcEipBandwidthUtilizationApi
    _ctvpccheckeipaddressapi: CtvpcCheckEipAddressApi
    _ctvpceipqueryrenewpriceapi: CtvpcEipQueryRenewPriceApi


    def __init__(self, endpoint_url: str, client: Optional[CtyunClient] = None):
        self.client = client or CtyunClient()
        self.endpoint = endpoint_url

        self._ctvpceipquerymodifypriceapi = CtvpcEipQueryModifyPriceApi(self.client)
        self._ctvpceipquerymodifypriceapi.set_endpoint(self.endpoint)
        self._ctvpceipquerycreatepriceapi = CtvpcEipQueryCreatePriceApi(self.client)
        self._ctvpceipquerycreatepriceapi.set_endpoint(self.endpoint)
        self._ctvpcattachportbmapi = CtvpcAttachPortBmApi(self.client)
        self._ctvpcattachportbmapi.set_endpoint(self.endpoint)
        self._ctvpcneweiplistapi = CtvpcNewEipListApi(self.client)
        self._ctvpcneweiplistapi.set_endpoint(self.endpoint)
        self._ctvpccreateeipwithipaddressapi = CtvpcCreateEipWithIpAddressApi(self.client)
        self._ctvpccreateeipwithipaddressapi.set_endpoint(self.endpoint)
        self._ctvpcgeteipfilingstatusapi = CtvpcGetEipFilingStatusApi(self.client)
        self._ctvpcgeteipfilingstatusapi.set_endpoint(self.endpoint)
        self._ctvpcchangeeipnameapi = CtvpcChangeEipNameApi(self.client)
        self._ctvpcchangeeipnameapi.set_endpoint(self.endpoint)
        self._ctvpcbatchcheckeipaddressapi = CtvpcBatchCheckEipAddressApi(self.client)
        self._ctvpcbatchcheckeipaddressapi.set_endpoint(self.endpoint)
        self._ctvpcshoweipapi = CtvpcShowEipApi(self.client)
        self._ctvpcshoweipapi.set_endpoint(self.endpoint)
        self._ctvpcattacheiptoportapi = CtvpcAttachEipToPortApi(self.client)
        self._ctvpcattacheiptoportapi.set_endpoint(self.endpoint)
        self._ctvpcdisassociateeipapi = CtvpcDisassociateEipApi(self.client)
        self._ctvpcdisassociateeipapi.set_endpoint(self.endpoint)
        self._ctvpcmodifyeipspecapi = CtvpcModifyEipSpecApi(self.client)
        self._ctvpcmodifyeipspecapi.set_endpoint(self.endpoint)
        self._ctvpcassociateeipapi = CtvpcAssociateEipApi(self.client)
        self._ctvpcassociateeipapi.set_endpoint(self.endpoint)
        self._ctvpcreneweipapi = CtvpcRenewEipApi(self.client)
        self._ctvpcreneweipapi.set_endpoint(self.endpoint)
        self._ctvpccreateeipapi = CtvpcCreateEipApi(self.client)
        self._ctvpccreateeipapi.set_endpoint(self.endpoint)
        self._ctvpcdeleteeipapi = CtvpcDeleteEipApi(self.client)
        self._ctvpcdeleteeipapi.set_endpoint(self.endpoint)
        self._ctvpclisteipapi = CtvpcListEipApi(self.client)
        self._ctvpclisteipapi.set_endpoint(self.endpoint)
        self._ctvpceipingerssbandwidthutilizationapi = CtvpcEipIngerssBandwidthUtilizationApi(self.client)
        self._ctvpceipingerssbandwidthutilizationapi.set_endpoint(self.endpoint)
        self._ctvpceipegerssbandwidthutilizationapi = CtvpcEipEgerssBandwidthUtilizationApi(self.client)
        self._ctvpceipegerssbandwidthutilizationapi.set_endpoint(self.endpoint)
        self._ctvpceipbandwidthutilizationapi = CtvpcEipBandwidthUtilizationApi(self.client)
        self._ctvpceipbandwidthutilizationapi.set_endpoint(self.endpoint)
        self._ctvpccheckeipaddressapi = CtvpcCheckEipAddressApi(self.client)
        self._ctvpccheckeipaddressapi.set_endpoint(self.endpoint)
        self._ctvpceipqueryrenewpriceapi = CtvpcEipQueryRenewPriceApi(self.client)
        self._ctvpceipqueryrenewpriceapi.set_endpoint(self.endpoint)

    @property  # noqa
    def ctvpceipquerymodifypriceapi(self) -> CtvpcEipQueryModifyPriceApi:  # noqa
        return self._ctvpceipquerymodifypriceapi

    @property  # noqa
    def ctvpceipquerycreatepriceapi(self) -> CtvpcEipQueryCreatePriceApi:  # noqa
        return self._ctvpceipquerycreatepriceapi

    @property  # noqa
    def ctvpcattachportbmapi(self) -> CtvpcAttachPortBmApi:  # noqa
        return self._ctvpcattachportbmapi

    @property  # noqa
    def ctvpcneweiplistapi(self) -> CtvpcNewEipListApi:  # noqa
        return self._ctvpcneweiplistapi

    @property  # noqa
    def ctvpccreateeipwithipaddressapi(self) -> CtvpcCreateEipWithIpAddressApi:  # noqa
        return self._ctvpccreateeipwithipaddressapi

    @property  # noqa
    def ctvpcgeteipfilingstatusapi(self) -> CtvpcGetEipFilingStatusApi:  # noqa
        return self._ctvpcgeteipfilingstatusapi

    @property  # noqa
    def ctvpcchangeeipnameapi(self) -> CtvpcChangeEipNameApi:  # noqa
        return self._ctvpcchangeeipnameapi

    @property  # noqa
    def ctvpcbatchcheckeipaddressapi(self) -> CtvpcBatchCheckEipAddressApi:  # noqa
        return self._ctvpcbatchcheckeipaddressapi

    @property  # noqa
    def ctvpcshoweipapi(self) -> CtvpcShowEipApi:  # noqa
        return self._ctvpcshoweipapi

    @property  # noqa
    def ctvpcattacheiptoportapi(self) -> CtvpcAttachEipToPortApi:  # noqa
        return self._ctvpcattacheiptoportapi

    @property  # noqa
    def ctvpcdisassociateeipapi(self) -> CtvpcDisassociateEipApi:  # noqa
        return self._ctvpcdisassociateeipapi

    @property  # noqa
    def ctvpcmodifyeipspecapi(self) -> CtvpcModifyEipSpecApi:  # noqa
        return self._ctvpcmodifyeipspecapi

    @property  # noqa
    def ctvpcassociateeipapi(self) -> CtvpcAssociateEipApi:  # noqa
        return self._ctvpcassociateeipapi

    @property  # noqa
    def ctvpcreneweipapi(self) -> CtvpcRenewEipApi:  # noqa
        return self._ctvpcreneweipapi

    @property  # noqa
    def ctvpccreateeipapi(self) -> CtvpcCreateEipApi:  # noqa
        return self._ctvpccreateeipapi

    @property  # noqa
    def ctvpcdeleteeipapi(self) -> CtvpcDeleteEipApi:  # noqa
        return self._ctvpcdeleteeipapi

    @property  # noqa
    def ctvpclisteipapi(self) -> CtvpcListEipApi:  # noqa
        return self._ctvpclisteipapi

    @property  # noqa
    def ctvpccheckeipaddressapi(self) -> CtvpcCheckEipAddressApi:  # noqa
        return self._ctvpccheckeipaddressapi

    @property  # noqa
    def ctvpceipqueryrenewpriceapi(self) -> CtvpcEipQueryRenewPriceApi:  # noqa
        return self._ctvpceipqueryrenewpriceapi
