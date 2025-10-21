from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcListIpv6CidrRequest:
    regionID: str  # 区域ID



@dataclass_json
@dataclass
class CtvpcListIpv6CidrReturnObjResponse:
    regionID: Optional[str]  # 资源池 ID
    ipv6CidrBlock: Optional[str]  # ipv6 cidr, 当 addressPoolType 为 ctyun 时，该字段不显示
    ipv6SegmentPoolID: Optional[str]  # ipv6 地址段 id
    addressPoolType: Optional[str]  # 地址段类型: custom / ctyun
    isp: Optional[str]  # isp
    vpcIpv6PrefixLen: Any  # vpc ipv6 CIDR前缀长度
    subnetIpv6PrefixLen: Any  # subnet ipv6 CIDR前缀长度
    availableBlockCount: Any  # 可用数量
    adminStatus: Any  # 状态


@dataclass_json
@dataclass
class CtvpcListIpv6CidrResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    requestID: Optional[str]  # 请求 id
    returnObj: Optional[List[Optional[CtvpcListIpv6CidrReturnObjResponse]]]  # 业务数据



# 获取ipv6地址段
class CtvpcListIpv6CidrApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcListIpv6CidrRequest) -> CtvpcListIpv6CidrResponse:
        url = endpoint + "/v4/ipv6/list-cidrs"
        params = {'regionID':request.regionID}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtvpcListIpv6CidrResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
