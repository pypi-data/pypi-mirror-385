from typing import List, Optional, Dict, Any
from ctyunsdk_eip20220909.core.client import CtyunClient
from ctyunsdk_eip20220909.core.credential import Credential
from ctyunsdk_eip20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcShowEipRequest:
    regionID: str  # 资源池 ID
    eipID: str  # 弹性公网IP的ID


@dataclass_json
@dataclass
class CtvpcShowEipReturnObjResponse:
    """返回结果"""
    ID: Optional[str] = None  # eip ID
    name: Optional[str] = None  # eip 名称
    description: Optional[str] = None  # 描述
    eipAddress: Optional[str] = None  # eip 地址
    associationID: Optional[str] = None  # 当前绑定的实例的 ID
    associationType: Optional[
        str] = None  # 当前绑定的实例类型: LOADBALANCER / INSTANCE / PORTFORWARDING / VIP / PHYSICALINSTANCE
    privateIpAddress: Optional[str] = None  # 交换机网段内的一个 IP 地址
    bandwidth: Optional[Any] = None  # 带宽峰值大小，单位 Mb
    status: Optional[
        str] = None  # 1.ACTIVE 2.DOWN 3.ERROR 4.UPDATING 5.BANDING_OR_UNBANGDING 6.DELETING 7.DELETED 8.EXPIRED
    tags: Optional[str] = None  # EIP 的标签集合
    createdAt: Optional[str] = None  # 创建时间
    updatedAt: Optional[str] = None  # 更新时间
    bandwidthID: Optional[str] = None  # 绑定的共享带宽 ID
    bandwidthType: Optional[str] = None  # eip带宽规格：standalone / upflowc
    enableSecondLevelMonitor: Optional[bool] = None  # 是否开启秒级监控
    expiredAt: Optional[str] = None  # 到期时间
    lineType: Optional[str] = None  # 线路类型
    projectID: Optional[str] = None  # 项目ID
    portID: Optional[str] = None  # 绑定的网卡 id
    isPackaged: Optional[bool] = None  # 表示是否与 vm 一起订购
    billingMethod: Optional[str] = None  # 计费类型：periodic 包周期，on_demand 按需


@dataclass_json
@dataclass
class CtvpcShowEipResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str] = None  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str] = None  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str] = None  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcShowEipReturnObjResponse] = None  # 返回结果


# 调用此接口可查看EIP详情。
class CtvpcShowEipApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)

    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint

    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str,
           request: CtvpcShowEipRequest) -> CtvpcShowEipResponse:
        url = endpoint + "/v4/eip/show"
        params = {'regionID': request.regionID, 'eipID': request.eipID}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtvpcShowEipResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
