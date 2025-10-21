from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcListSubnetUsedIPsRequest:
    regionID: str  # 资源池 ID
    subnetID: str  # 子网 ID
    pageNumber: Optional[Any] = None  # 列表的页码，默认值为 1。
    pageNo: Optional[Any] = None  # 列表的页码，默认值为 1, 推荐使用该字段, pageNumber 后续会废弃
    pageSize: Optional[Any] = None  # 分页查询时每页的行数，最大值为 50，默认值为 10。
    ip: Optional[str] = None # 子网内的 IP 地址 = None



@dataclass_json
@dataclass
class CtvpcListSubnetUsedIPsReturnObjUsedIPsResponse:
    ipv4Address: Optional[str]  # ipv4 地址
    ipv6Address: Optional[str]  # ipv6 地址
    useDesc: Optional[str]  # 用途中文描述:云主机, 裸金属, 高可用虚 IP, SNAT, 负载均衡, 预占内网 IP, 内网网关接口, system
    use: Optional[str]  # 用途英文描述
    secondaryPrivateIpv4: Optional[List[Optional[str]]]  # 扩展ipv4地址
    secondaryPrivateIpv6: Optional[List[Optional[str]]]  # 扩展ipv6地址


@dataclass_json
@dataclass
class CtvpcListSubnetUsedIPsReturnObjResponse:
    """接口业务数据"""
    usedIPs: Optional[List[Optional[CtvpcListSubnetUsedIPsReturnObjUsedIPsResponse]]]  # 已使用的 IP 数组
    totalCount: Any  # 列表条目数
    currentCount: Any  # 分页查询时每页的行数。
    totalPage: Any  # 总页数


@dataclass_json
@dataclass
class CtvpcListSubnetUsedIPsResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcListSubnetUsedIPsReturnObjResponse]  # 接口业务数据



# 查看某个子网已使用IP
class CtvpcListSubnetUsedIPsApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcListSubnetUsedIPsRequest) -> CtvpcListSubnetUsedIPsResponse:
        url = endpoint + "/v4/vpc/list-used-ips"
        params = {'regionID':request.regionID, 'subnetID':request.subnetID, 'ip':request.ip, 'pageNumber':request.pageNumber, 'pageNo':request.pageNo, 'pageSize':request.pageSize}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtvpcListSubnetUsedIPsResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
