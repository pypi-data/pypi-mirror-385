from typing import List, Optional, Dict, Any
from ctyunsdk_eip20220909.core.client import CtyunClient
from ctyunsdk_eip20220909.core.credential import Credential
from ctyunsdk_eip20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcAssociateEipRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 资源池 ID
    eipID: str  # 绑定云产品实例的 EIP 的 ID
    associationID: str  # 绑定的实例的 ID
    associationType: Any  # 绑定的实例类型：1 ECS 云主机 VM，2 VIP, 3 BM


@dataclass_json
@dataclass
class CtvpcAssociateEipResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str] = None  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str] = None  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str] = None  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS


# 调用此接口可将弹性公网IP（Elastic IP Address，简称EIP）与相关云产品上绑定。
class CtvpcAssociateEipApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)

    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint

    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str,
           request: CtvpcAssociateEipRequest) -> CtvpcAssociateEipResponse:
        url = endpoint + "/v4/eip/associate"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict,
                                   credential=credential)
            return CtvpcAssociateEipResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
