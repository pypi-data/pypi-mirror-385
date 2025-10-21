from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcCreateRouteTableRulesRouteRulesRequest:
    nextHopID: str  # 下一跳设备 id
    nextHopType: str  # vpcpeering / havip / bm / vm / natgw/ igw6 / dc / ticc / vpngw / enic
    destination: str  # 无类别域间路由
    ipVersion: Any  # 4 标识 ipv4, 6 标识 ipv6
    description: Optional[str] = None # 规则描述,支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:'{},./;'[,]·！@#￥%……&*（） —— -+={},《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128 = None


@dataclass_json
@dataclass
class CtvpcCreateRouteTableRulesRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 区域id
    routeTableID: str  # 路由表 id
    routeRules: List[CtvpcCreateRouteTableRulesRouteRulesRequest]  # 路由表规则列表



@dataclass_json
@dataclass
class CtvpcCreateRouteTableRulesResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[List[Optional[str]]]  # [route-rule-xxxx]



# 创建路由表规则
class CtvpcCreateRouteTableRulesApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcCreateRouteTableRulesRequest) -> CtvpcCreateRouteTableRulesResponse:
        url = endpoint + "/v4/vpc/route-table/create-rules"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtvpcCreateRouteTableRulesResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
