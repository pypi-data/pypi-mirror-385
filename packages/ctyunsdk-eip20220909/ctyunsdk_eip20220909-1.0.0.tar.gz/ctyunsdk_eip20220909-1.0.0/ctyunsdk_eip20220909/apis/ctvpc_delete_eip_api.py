from typing import List, Optional, Dict, Any
from ctyunsdk_eip20220909.core.client import CtyunClient
from ctyunsdk_eip20220909.core.credential import Credential
from ctyunsdk_eip20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcDeleteEipRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 资源池 ID
    eipID: str  # eip id


@dataclass_json
@dataclass
class CtvpcDeleteEipReturnObjResponse:
    """object"""
    masterOrderID: Optional[str] = None  # 订单id。
    masterOrderNO: Optional[str] = None  # 订单编号, 可以为 null。
    masterResourceStatus: Optional[
        str] = None  # 资源状态: started（启用） / renewed（续订） / refunded（退订） / destroyed（销毁） / failed（失败） / starting（正在启用） / changed（变配）/ expired（过期）/ unknown（未知）
    regionID: Optional[str] = None  # 可用区id。


@dataclass_json
@dataclass
class CtvpcDeleteEipResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str] = None  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    errorCode: Optional[str] = None  # 错误码
    description: Optional[str] = None  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    returnObj: Optional[CtvpcDeleteEipReturnObjResponse] = None  # object


# 调用此接口可删除 EIP。
class CtvpcDeleteEipApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)

    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint

    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str,
           request: CtvpcDeleteEipRequest) -> CtvpcDeleteEipResponse:
        url = endpoint + "/v4/eip/delete"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict,
                                   credential=credential)
            return CtvpcDeleteEipResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
