from typing import Optional
from ctyunsdk_bandwidth20220909.core.client import CtyunClient
from ctyunsdk_bandwidth20220909.core.credential import Credential

from .ctvpc_bandwidth_renew_api import CtvpcBandwidthRenewApi
from .ctvpc_bandwidth_query_renew_price_api import CtvpcBandwidthQueryRenewPriceApi
from .ctvpc_bandwidth_query_modify_price_api import CtvpcBandwidthQueryModifyPriceApi
from .ctvpc_bandwidth_query_create_price_api import CtvpcBandwidthQueryCreatePriceApi
from .ctvpc_new_bandwidth_list_api import CtvpcNewBandwidthListApi
from .ctvpc_disassociate_i_pv6_from_bandwidth_api import CtvpcDisassociateIPv6FromBandwidthApi
from .ctvpc_associate_i_pv6_to_bandwidth_api import CtvpcAssociateIPv6ToBandwidthApi
from .ctvpc_disassociate_eip_from_bandwidth_api import CtvpcDisassociateEipFromBandwidthApi
from .ctvpc_associate_eip_to_bandwidth_api import CtvpcAssociateEipToBandwidthApi
from .ctvpc_list_bandwidth_api import CtvpcListBandwidthApi
from .ctvpc_show_bandwidth_api import CtvpcShowBandwidthApi
from .ctvpc_update_bandwidth_attribute_api import CtvpcUpdateBandwidthAttributeApi
from .ctvpc_modify_bandwidth_spec_api import CtvpcModifyBandwidthSpecApi
from .ctvpc_delete_bandwidth_api import CtvpcDeleteBandwidthApi
from .ctvpc_create_bandwidth_api import CtvpcCreateBandwidthApi
from .ctvpc_bandwidth_egerss_bandwidth_utilization_api import CtvpcBandwidthEgerssBandwidthUtilizationApi
from .ctvpc_bandwidth_ingerss_bandwidth_utilization_api import CtvpcBandwidthIngerssBandwidthUtilizationApi
from .ctvpc_bandwidth_bandwidth_utilization_api import CtvpcBandwidthBandwidthUtilizationApi

ENDPOINT_NAME = "ctvpc"

class Apis:
    _ctvpcbandwidthrenewapi: CtvpcBandwidthRenewApi
    _ctvpcbandwidthqueryrenewpriceapi: CtvpcBandwidthQueryRenewPriceApi
    _ctvpcbandwidthquerymodifypriceapi: CtvpcBandwidthQueryModifyPriceApi
    _ctvpcbandwidthquerycreatepriceapi: CtvpcBandwidthQueryCreatePriceApi
    _ctvpcnewbandwidthlistapi: CtvpcNewBandwidthListApi
    _ctvpcdisassociateipv6frombandwidthapi: CtvpcDisassociateIPv6FromBandwidthApi
    _ctvpcassociateipv6tobandwidthapi: CtvpcAssociateIPv6ToBandwidthApi
    _ctvpcdisassociateeipfrombandwidthapi: CtvpcDisassociateEipFromBandwidthApi
    _ctvpcassociateeiptobandwidthapi: CtvpcAssociateEipToBandwidthApi
    _ctvpclistbandwidthapi: CtvpcListBandwidthApi
    _ctvpcshowbandwidthapi: CtvpcShowBandwidthApi
    _ctvpcupdatebandwidthattributeapi: CtvpcUpdateBandwidthAttributeApi
    _ctvpcmodifybandwidthspecapi: CtvpcModifyBandwidthSpecApi
    _ctvpcdeletebandwidthapi: CtvpcDeleteBandwidthApi
    _ctvpccreatebandwidthapi: CtvpcCreateBandwidthApi
    _ctvpcbandwidthegerssbandwidthutilizationapi: CtvpcBandwidthEgerssBandwidthUtilizationApi
    _ctvpcbandwidthingerssbandwidthutilizationapi: CtvpcBandwidthIngerssBandwidthUtilizationApi
    _ctvpcbandwidthbandwidthutilizationapi: CtvpcBandwidthBandwidthUtilizationApi
    
    def __init__(self, endpoint_url: str, client: Optional[CtyunClient] = None):
        self.client = client or CtyunClient()
        self.endpoint = endpoint_url

        self._ctvpceipquerycreatepriceapi.set_endpoint(self.endpoint)
        self._ctvpcbandwidthrenewapi = CtvpcBandwidthRenewApi(self.client)
        self._ctvpcbandwidthrenewapi.set_endpoint(self.endpoint)
        self._ctvpcbandwidthqueryrenewpriceapi = CtvpcBandwidthQueryRenewPriceApi(self.client)
        self._ctvpcbandwidthqueryrenewpriceapi.set_endpoint(self.endpoint)
        self._ctvpcbandwidthquerymodifypriceapi = CtvpcBandwidthQueryModifyPriceApi(self.client)
        self._ctvpcbandwidthquerymodifypriceapi.set_endpoint(self.endpoint)
        self._ctvpcbandwidthquerycreatepriceapi = CtvpcBandwidthQueryCreatePriceApi(self.client)
        self._ctvpcbandwidthquerycreatepriceapi.set_endpoint(self.endpoint)
        self._ctvpcdisassociateipv6frombandwidthapi = CtvpcDisassociateIPv6FromBandwidthApi(self.client)
        self._ctvpcdisassociateipv6frombandwidthapi.set_endpoint(self.endpoint)
        self._ctvpcassociateipv6tobandwidthapi = CtvpcAssociateIPv6ToBandwidthApi(self.client)
        self._ctvpcassociateipv6tobandwidthapi.set_endpoint(self.endpoint)
        self._ctvpcdisassociateeipfrombandwidthapi = CtvpcDisassociateEipFromBandwidthApi(self.client)
        self._ctvpcdisassociateeipfrombandwidthapi.set_endpoint(self.endpoint)
        self._ctvpcassociateeiptobandwidthapi = CtvpcAssociateEipToBandwidthApi(self.client)
        self._ctvpcassociateeiptobandwidthapi.set_endpoint(self.endpoint)
        self._ctvpclistbandwidthapi = CtvpcListBandwidthApi(self.client)
        self._ctvpclistbandwidthapi.set_endpoint(self.endpoint)
        self._ctvpcshowbandwidthapi = CtvpcShowBandwidthApi(self.client)
        self._ctvpcshowbandwidthapi.set_endpoint(self.endpoint)
        self._ctvpcupdatebandwidthattributeapi = CtvpcUpdateBandwidthAttributeApi(self.client)
        self._ctvpcupdatebandwidthattributeapi.set_endpoint(self.endpoint)
        self._ctvpcmodifybandwidthspecapi = CtvpcModifyBandwidthSpecApi(self.client)
        self._ctvpcmodifybandwidthspecapi.set_endpoint(self.endpoint)
        self._ctvpcdeletebandwidthapi = CtvpcDeleteBandwidthApi(self.client)
        self._ctvpcdeletebandwidthapi.set_endpoint(self.endpoint)
        self._ctvpccreatebandwidthapi = CtvpcCreateBandwidthApi(self.client)
        self._ctvpccreatebandwidthapi.set_endpoint(self.endpoint)
        self._ctvpcnewbandwidthlistapi = CtvpcNewBandwidthListApi(self.client)
        self._ctvpcnewbandwidthlistapi.set_endpoint(self.endpoint)
        self._ctvpcbandwidthegerssbandwidthutilizationapi = CtvpcBandwidthEgerssBandwidthUtilizationApi(self.client)
        self._ctvpcbandwidthegerssbandwidthutilizationapi.set_endpoint(self.endpoint)
        self._ctvpcbandwidthingerssbandwidthutilizationapi = CtvpcBandwidthIngerssBandwidthUtilizationApi(self.client)
        self._ctvpcbandwidthingerssbandwidthutilizationapi.set_endpoint(self.endpoint)
        self._ctvpcbandwidthbandwidthutilizationapi = CtvpcBandwidthBandwidthUtilizationApi(self.client)
        self._ctvpcbandwidthbandwidthutilizationapi.set_endpoint(self.endpoint)

    @property  # noqa
    def ctvpcbandwidthrenewapi(self) -> CtvpcBandwidthRenewApi:  # noqa
        return self._ctvpcbandwidthrenewapi
        
    @property  # noqa
    def ctvpcbandwidthqueryrenewpriceapi(self) -> CtvpcBandwidthQueryRenewPriceApi:  # noqa
        return self._ctvpcbandwidthqueryrenewpriceapi
        
    @property  # noqa
    def ctvpcbandwidthquerymodifypriceapi(self) -> CtvpcBandwidthQueryModifyPriceApi:  # noqa
        return self._ctvpcbandwidthquerymodifypriceapi
        
    @property  # noqa
    def ctvpcbandwidthquerycreatepriceapi(self) -> CtvpcBandwidthQueryCreatePriceApi:  # noqa
        return self._ctvpcbandwidthquerycreatepriceapi
        
    @property  # noqa
    def ctvpcdisassociateipv6frombandwidthapi(self) -> CtvpcDisassociateIPv6FromBandwidthApi:  # noqa
        return self._ctvpcdisassociateipv6frombandwidthapi
        
    @property  # noqa
    def ctvpcassociateipv6tobandwidthapi(self) -> CtvpcAssociateIPv6ToBandwidthApi:  # noqa
        return self._ctvpcassociateipv6tobandwidthapi
        
    @property  # noqa
    def ctvpcdisassociateeipfrombandwidthapi(self) -> CtvpcDisassociateEipFromBandwidthApi:  # noqa
        return self._ctvpcdisassociateeipfrombandwidthapi
        
    @property  # noqa
    def ctvpcassociateeiptobandwidthapi(self) -> CtvpcAssociateEipToBandwidthApi:  # noqa
        return self._ctvpcassociateeiptobandwidthapi
        
    @property  # noqa
    def ctvpclistbandwidthapi(self) -> CtvpcListBandwidthApi:  # noqa
        return self._ctvpclistbandwidthapi
        
    @property  # noqa
    def ctvpcshowbandwidthapi(self) -> CtvpcShowBandwidthApi:  # noqa
        return self._ctvpcshowbandwidthapi
        
    @property  # noqa
    def ctvpcupdatebandwidthattributeapi(self) -> CtvpcUpdateBandwidthAttributeApi:  # noqa
        return self._ctvpcupdatebandwidthattributeapi
        
    @property  # noqa
    def ctvpcmodifybandwidthspecapi(self) -> CtvpcModifyBandwidthSpecApi:  # noqa
        return self._ctvpcmodifybandwidthspecapi
        
    @property  # noqa
    def ctvpcdeletebandwidthapi(self) -> CtvpcDeleteBandwidthApi:  # noqa
        return self._ctvpcdeletebandwidthapi
        
    @property  # noqa
    def ctvpccreatebandwidthapi(self) -> CtvpcCreateBandwidthApi:  # noqa
        return self._ctvpccreatebandwidthapi

    @property  # noqa
    def ctvpcbandwidthegerssbandwidthutilizationapi(self) -> CtvpcBandwidthEgerssBandwidthUtilizationApi:  # noqa
        return self._ctvpcbandwidthegerssbandwidthutilizationapi
        
    @property  # noqa
    def ctvpcbandwidthingerssbandwidthutilizationapi(self) -> CtvpcBandwidthIngerssBandwidthUtilizationApi:  # noqa
        return self._ctvpcbandwidthingerssbandwidthutilizationapi
        
    @property  # noqa
    def ctvpcbandwidthbandwidthutilizationapi(self) -> CtvpcBandwidthBandwidthUtilizationApi:  # noqa
        return self._ctvpcbandwidthbandwidthutilizationapi

    @property  # noqa
    def ctvpcnewbandwidthlistapi(self) -> CtvpcNewBandwidthListApi:  # noqa
        return self._ctvpcnewbandwidthlistapi

        
