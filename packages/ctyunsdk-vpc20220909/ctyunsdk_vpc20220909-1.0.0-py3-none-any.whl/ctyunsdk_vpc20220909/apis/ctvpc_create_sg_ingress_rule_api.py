from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcCreateSgIngressRuleSecurityGroupRulesRequest:
    direction: str  # 入方向
    remoteType: Any  # remote 类型，0 表示使用 cidr，1 表示使用远端安全组，默认为 0 
    action: str  # 拒绝策略:允许-accept 拒绝-drop
    priority: Any  # 优先级:1~100，取值越小优先级越大
    protocol: str  # 协议: ANY、TCP、UDP、ICMP(v4)
    ethertype: str  # IP类型:IPv4、IPv6
    destCidrIp: str  # 远端地址:0.0.0.0/0
    remoteSecurityGroupID: Optional[str] = None # 远端安全组 id = None
    description: Optional[str] = None # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:"{},./;'[\]·！@#￥%……&*（） —— -+={}\《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128 = None
    range: Optional[str] = None # 安全组开放的传输层协议相关的源端端口范围 = None


@dataclass_json
@dataclass
class CtvpcCreateSgIngressRuleRequest:
    regionID: str  # 区域id
    securityGroupID: str  # 安全组ID。
    securityGroupRules: List[CtvpcCreateSgIngressRuleSecurityGroupRulesRequest]  # 规则信息
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64



@dataclass_json
@dataclass
class CtvpcCreateSgIngressRuleReturnObjResponse:
    """业务数据"""
    sgRuleIDs: Optional[List[Optional[str]]]  # 安全组规则 id 列表


@dataclass_json
@dataclass
class CtvpcCreateSgIngressRuleResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcCreateSgIngressRuleReturnObjResponse]  # 业务数据



# 创建安全组入向规则。
class CtvpcCreateSgIngressRuleApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcCreateSgIngressRuleRequest) -> CtvpcCreateSgIngressRuleResponse:
        url = endpoint + "/v4/vpc/create-security-group-ingress"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtvpcCreateSgIngressRuleResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
