from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcShowSgRuleRequest:
    regionID: str  # 区域id
    securityGroupID: str  # 安全组 ID
    securityGroupRuleID: str  # 安全组规则 ID



@dataclass_json
@dataclass
class CtvpcShowSgRuleReturnObjResponse:
    """返回结果"""
    direction: Optional[str]  # 出方向-egress、入方向-ingress
    priority: Any  # 优先级:0~100
    ethertype: Optional[str]  # IP类型:IPv4、IPv6
    protocol: Optional[str]  # 协议: ANY、TCP、UDP、ICMP、ICMP6
    range: Optional[str]  # 接口范围/ICMP类型:1-65535
    destCidrIp: Optional[str]  # 远端地址:0.0.0.0/0
    description: Optional[str]  # 安全组规则描述信息。
    createTime: Optional[str]  # 创建时间，UTC时间。
    id: Optional[str]  # 唯一标识ID
    securityGroupID: Optional[str]  # 安全组ID
    action: Optional[str]  # 拒绝策略:允许-accept 拒绝-drop
    origin: Optional[str]  # 类型
    remoteSecurityGroupID: Optional[str]  # 远端安全组ID
    prefixListID: Optional[str]  # 前缀列表ID


@dataclass_json
@dataclass
class CtvpcShowSgRuleResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcShowSgRuleReturnObjResponse]  # 返回结果



# 安全组规则详情。
class CtvpcShowSgRuleApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcShowSgRuleRequest) -> CtvpcShowSgRuleResponse:
        url = endpoint + "/v4/vpc/describe-security-group-rule"
        params = {'regionID':request.regionID, 'securityGroupID':request.securityGroupID, 'securityGroupRuleID':request.securityGroupRuleID}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtvpcShowSgRuleResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
