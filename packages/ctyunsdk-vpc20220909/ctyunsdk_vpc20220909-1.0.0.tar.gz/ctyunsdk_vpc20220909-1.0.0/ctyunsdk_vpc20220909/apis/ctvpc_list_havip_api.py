from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcListHavipFiltersRequest:
    key: str  # 筛选字段的key，支持：haVipID，vpcID，subnetID
    value: str  # 筛选字段对应key的value


@dataclass_json
@dataclass
class CtvpcListHavipRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 资源池ID
    projectID: Optional[str] = None # 企业项目ID，默认为'0' = None
    filters: Optional[List[Optional[CtvpcListHavipFiltersRequest]]] = None # 筛选条件,filters为一个表，{key:haVipID(vpcID,subnetID),value:xxx(筛选字段对应key的value)},具体见请求体body示例 = None



@dataclass_json
@dataclass
class CtvpcListHavipReturnObjNetworkInfoResponse:
    eipID: Optional[str]  # 弹性 IP ID


@dataclass_json
@dataclass
class CtvpcListHavipReturnObjInstanceInfoResponse:
    instanceName: Optional[str]  # 实例名
    id: Optional[str]  # 实例 ID
    privateIp: Optional[str]  # 实例私有 IP
    privateIpv6: Optional[str]  # 实例的 IPv6 地址, 可以为空字符串
    publicIp: Optional[str]  # 实例公网 IP


@dataclass_json
@dataclass
class CtvpcListHavipReturnObjResponse:
    id: Optional[str]  # 高可用虚IP的ID
    ipv4: Optional[str]  # IPv4地址
    ipv6: Optional[str]  # ipv6 地址
    vpcID: Optional[str]  # 虚拟私有云的的id
    subnetID: Optional[str]  # 子网id
    instanceInfo: Optional[List[Optional[CtvpcListHavipReturnObjInstanceInfoResponse]]]  # 绑定实例相关信息
    networkInfo: Optional[List[Optional[CtvpcListHavipReturnObjNetworkInfoResponse]]]  # 绑定弹性 IP 相关信息


@dataclass_json
@dataclass
class CtvpcListHavipResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[List[Optional[CtvpcListHavipReturnObjResponse]]]  # 接口业务数据



# 查询高可用虚IP列表
class CtvpcListHavipApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcListHavipRequest) -> CtvpcListHavipResponse:
        url = endpoint + "/v4/vpc/havip/list"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtvpcListHavipResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
