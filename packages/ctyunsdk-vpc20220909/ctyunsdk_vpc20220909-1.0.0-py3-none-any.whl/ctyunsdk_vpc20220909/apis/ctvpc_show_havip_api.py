from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcShowHavipRequest:
    regionID: str  # 资源池 ID
    haVipID: str  # 高可用虚 IP 的 ID



@dataclass_json
@dataclass
class CtvpcShowHavipReturnObjBindPortsResponse:
    portID: Optional[str] = None  # 网卡 ID
    role: Optional[str] = None  # keepalive 角色: master / slave
    createdAt: Optional[str] = None  # 创建时间


@dataclass_json
@dataclass
class CtvpcShowHavipReturnObjNetworkInfoResponse:
    eipID: Optional[str] = None  # 弹性 IP ID


@dataclass_json
@dataclass
class CtvpcShowHavipReturnObjInstanceInfoResponse:
    instanceName: Optional[str] = None  # 实例名
    id: Optional[str] = None  # 实例 ID
    privateIp: Optional[str] = None  # 实例私有 IP
    privateIpv6: Optional[str] = None  # 实例的 IPv6 地址, 可以为空字符串
    publicIp: Optional[str] = None  # 实例公网 IP


@dataclass_json
@dataclass
class CtvpcShowHavipReturnObjResponse:
    """接口业务数据"""
    id: Optional[str]  # 高可用虚 IP 的 ID
    ipv4: Optional[str]  # IPv4 地址
    ipv6: Optional[str]  # ipv6 地址
    vpcID: Optional[str]  # 虚拟私有云的的 id
    subnetID: Optional[str]  # 子网 id
    instanceInfo: Optional[List[Optional[CtvpcShowHavipReturnObjInstanceInfoResponse]]]  # 绑定实例相关信息
    networkInfo: Optional[List[Optional[CtvpcShowHavipReturnObjNetworkInfoResponse]]]  # 绑定弹性 IP 相关信息
    bindPorts: Optional[List[Optional[CtvpcShowHavipReturnObjBindPortsResponse]]]  # 绑定网卡信息


@dataclass_json
@dataclass
class CtvpcShowHavipResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcShowHavipReturnObjResponse]  # 接口业务数据



# 查看高可用虚 IP 详情
class CtvpcShowHavipApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcShowHavipRequest) -> CtvpcShowHavipResponse:
        url = endpoint + "/v4/vpc/havip/show"
        params = {'regionID':request.regionID, 'haVipID':request.haVipID}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtvpcShowHavipResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
