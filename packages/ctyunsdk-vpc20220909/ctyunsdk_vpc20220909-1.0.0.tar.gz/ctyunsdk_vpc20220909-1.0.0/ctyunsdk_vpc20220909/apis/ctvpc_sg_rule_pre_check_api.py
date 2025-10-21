from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcSgRulePreCheckSecurityGroupRuleRequest:
    direction: str  # 入方向
    action: str  # 拒绝策略:允许-accept 拒绝-drop
    priority: Any  # 优先级:1~100，取值越小优先级越大
    protocol: str  # 协议: ANY、TCP、UDP、ICMP(v4)
    ethertype: str  # IP 类型:IPv4、IPv6
    destCidrIp: str  # 远端地址:0.0.0.0/0
    range: Optional[str] = None # 安全组开放的传输层协议相关的源端端口范围 = None
    """规则信息"""


@dataclass_json
@dataclass
class CtvpcSgRulePreCheckRequest:
    regionID: str  # 区域 id
    securityGroupID: str  # 安全组 ID。
    securityGroupRule: CtvpcSgRulePreCheckSecurityGroupRuleRequest  # 规则信息



@dataclass_json
@dataclass
class CtvpcSgRulePreCheckReturnObjResponse:
    """接口业务数据"""
    sgRuleID: Optional[str]  # 和哪个规则重复


@dataclass_json
@dataclass
class CtvpcSgRulePreCheckResponse:
    statusCode: Any  # 返回状态码（800 为成功，900 为失败）
    message: Optional[str]  # statusCode 为 900 时的错误信息; statusCode 为 800 时为 success, 英文
    description: Optional[str]  # statusCode 为 900 时的错误信息; statusCode 为 800 时为成功, 中文
    errorCode: Optional[str]  # statusCode 为 900 时为业务细分错误码，三段式：product.module.code; statusCode 为 800 时为 SUCCESS
    returnObj: Optional[CtvpcSgRulePreCheckReturnObjResponse]  # 接口业务数据



# 安全组规则检查
class CtvpcSgRulePreCheckApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcSgRulePreCheckRequest) -> CtvpcSgRulePreCheckResponse:
        url = endpoint + "/v4/vpc/pre-check-sg-rule"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtvpcSgRulePreCheckResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
