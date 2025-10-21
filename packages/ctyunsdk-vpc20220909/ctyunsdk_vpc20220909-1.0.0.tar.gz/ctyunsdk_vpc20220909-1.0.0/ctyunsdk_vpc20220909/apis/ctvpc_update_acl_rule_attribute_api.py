from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcUpdateAclRuleAttributeRulesRequest:
    aclRuleID: str  # aclRuleID
    direction: str  # 类型,ingress, egress
    priority: Any  # 优先级 1 - 32766，不填默认100
    protocol: str  # all, icmp, tcp, udp, gre,  icmp6
    ipVersion: str  # ipv4,  ipv6
    sourceIpAddress: str  # 源地址
    destinationIpAddress: str  # 目的地址
    action: str  # accept, drop
    enabled: str  # disable, enable
    destinationPort: Optional[str] = None # 开始和结束port以:隔开 = None
    sourcePort: Optional[str] = None # 开始和结束port以:隔开 = None
    description: Optional[str] = None # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:'{},./;'[,]·！@#￥%……&*（） —— -+={},《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128 = None


@dataclass_json
@dataclass
class CtvpcUpdateAclRuleAttributeRequest:
    regionID: str  # 资源池ID
    aclID: str  # aclID
    rules: List[CtvpcUpdateAclRuleAttributeRulesRequest]  # rule 规则数组
    clientToken: Optional[str] = None # 客户端存根，用于保证订单幂等性。要求单个云平台账户内唯一 = None



@dataclass_json
@dataclass
class CtvpcUpdateAclRuleAttributeReturnObjResponse:
    """接口业务数据"""
    aclID: Optional[str]  # aclID


@dataclass_json
@dataclass
class CtvpcUpdateAclRuleAttributeResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcUpdateAclRuleAttributeReturnObjResponse]  # 接口业务数据



# 修改 Acl 规则列表属性
class CtvpcUpdateAclRuleAttributeApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcUpdateAclRuleAttributeRequest) -> CtvpcUpdateAclRuleAttributeResponse:
        url = endpoint + "/v4/acl-rule/update"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtvpcUpdateAclRuleAttributeResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
