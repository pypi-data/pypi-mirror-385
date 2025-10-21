from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcModifySgIngressRuleRequest:
    regionID: str  # 区域id
    securityGroupID: str  # 安全组ID。
    securityGroupRuleID: str  # 安全组规则ID。
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    priority: Any  # 优先级:1~100，取值越小优先级越大
    remoteType: Any  # 远端类型，0 表示 destCidrIp，1 表示 remoteSecurityGroupID, 2 表示 prefixlistID，默认为 0
    description: Optional[str] = None # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:{},./;'[]·~！@#￥%……&*（） —— -+={}\《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128 = None
    action: Optional[str] = None # 拒绝策略:允许-accept 拒绝-drop = None
    protocol: Optional[str] = None # 协议: ANY、TCP、UDP、ICMP(v4) = None
    remoteSecurityGroupID: Optional[str] = None # 远端安全组id = None
    destCidrIp: Optional[str] = None # cidr = None
    prefixListID: Optional[str] = None # 前缀列表 = None



@dataclass_json
@dataclass
class CtvpcModifySgIngressRuleResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS



# 修改安全组入方向规则的描述信息。该接口只能修改入方向描述信息。如果您需要修改安全组规则的策略、端口范围等信息，请在管理控制台修改。
class CtvpcModifySgIngressRuleApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcModifySgIngressRuleRequest) -> CtvpcModifySgIngressRuleResponse:
        url = endpoint + "/v4/vpc/modify-security-group-ingress"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtvpcModifySgIngressRuleResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
