from typing import List, Optional, Dict, Any
from ctyunsdk_eip20220909.core.client import CtyunClient
from ctyunsdk_eip20220909.core.credential import Credential
from ctyunsdk_eip20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcNewEipListRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性。要求单个云平台账户内唯一
    regionID: str  # 资源池 ID
    projectID: Optional[str] = None  # 企业项目 ID，默认为"0"
    page: Optional[Any] = None  # 分页参数
    pageNo: Optional[Any] = None  # 列表的页码，默认值为 1, 推荐使用该字段, page 后续会废弃
    pageSize: Optional[Any] = None  # 每页数据量大小，取值 1-50
    ids: Optional[List[Optional[str]]] = None  # 是 Array 类型，里面的内容是 String
    status: Optional[str] = None  # eip状态 ACTIVE（已绑定）/ DOWN（未绑定）/ FREEZING（已冻结）/ EXPIRED（已过期），不传是查询所有状态的 EIP
    ipType: Optional[str] = None  # ip类型 ipv4 / ipv6
    eipType: Optional[str] = None  # eip类型 normal / cn2
    ip: Optional[str] = None  # 弹性 IP 的 ip 地址
    nexToken: Optional[str] = None  # 下一页游标
    maxResults: Optional[Any] = None  # 最大分页数


@dataclass_json
@dataclass
class CtvpcNewEipListReturnObjEipsResponse:
    ID: Optional[str] = None  # eip ID
    name: Optional[str] = None  # eip 名称
    description: Optional[str] = None  # 描述
    eipAddress: Optional[str] = None  # eip 地址
    associationID: Optional[str] = None  # 当前绑定的实例的 ID
    associationType: Optional[
        str] = None  # 当前绑定的实例类型: LOADBALANCER / INSTANCE / PORTFORWARDING / VIP / PHYSICALINSTANCE
    privateIpAddress: Optional[str] = None  # 交换机网段内的一个 IP 地址
    bandwidth: Optional[Any] = None  # 带宽峰值大小，单位 Mb
    bandwidthID: Optional[str] = None  # 绑定的共享带宽 ID
    bandwidthType: Optional[str] = None  # eip带宽规格：standalone / upflowc
    enableSecondLevelMonitor: Optional[bool] = None  # 是否开启秒级监控
    status: Optional[str] = None  # 1.ACTIVE 2.DOWN .EXPIRED
    tags: Optional[str] = None  # EIP 的标签集合
    lineType: Optional[str] = None  # 线路类型
    projectID: Optional[str] = None  # 项目ID
    portID: Optional[str] = None  # 绑定的网卡 id
    isPackaged: Optional[bool] = None  # 表示是否与 vm 一起订购
    billingMethod: Optional[str] = None  # 计费类型：periodic 包周期，on_demand 按需
    createdAt: Optional[str] = None  # 创建时间
    updatedAt: Optional[str] = None  # 更新时间
    expiredAt: Optional[str] = None  # 到期时间


@dataclass_json
@dataclass
class CtvpcNewEipListReturnObjResponse:
    """返回结果"""
    eips: Optional[List[Optional[CtvpcNewEipListReturnObjEipsResponse]]]  # 弹性 IP 列表
    totalCount: Any  # 列表条目数
    currentCount: Any  # 分页查询时每页的行数。
    totalPage: Any  # 总页数


@dataclass_json
@dataclass
class CtvpcNewEipListResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str] = None  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str] = None  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str] = None  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcNewEipListReturnObjResponse] = None  # 返回结果


# 调用此接口可查询指定地域已创建的弹性公网IP（Elastic IP Address，简称EIP）。
class CtvpcNewEipListApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)

    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint

    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str,
           request: CtvpcNewEipListRequest) -> CtvpcNewEipListResponse:
        url = endpoint + "/v4/eip/new-list"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict,
                                   credential=credential)
            return CtvpcNewEipListResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
