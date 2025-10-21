from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcListAclRuleRequest:
    regionID: str  # 资源池ID
    aclID: str  # aclID



@dataclass_json
@dataclass
class CtvpcListAclRuleReturnObjOutRulesResponse:
    aclRuleID: Optional[str]  # aclRuleID
    direction: Optional[str]  # 类型,ingress, egress
    priority: Any  # 优先级
    protocol: Optional[str]  # all, icmp, tcp, udp, gre,  icmp6
    ipVersion: Optional[str]  # ipv4,  ipv6
    destinationPort: Optional[str]  # 开始和结束port以:隔开
    sourcePort: Optional[str]  # 开始和结束port以:隔开
    sourceIpAddress: Optional[str]  # 类型,ingress, egress
    destinationIpAddress: Optional[str]  # 类型,ingress, egress
    action: Optional[str]  # accept, drop
    enabled: Optional[str]  # disable, enable
    description: Optional[str]  # 描述


@dataclass_json
@dataclass
class CtvpcListAclRuleReturnObjInRulesResponse:
    aclRuleID: Optional[str]  # aclRuleID
    direction: Optional[str]  # 类型,ingress, egress
    priority: Any  # 优先级
    protocol: Optional[str]  # all, icmp, tcp, udp, gre,  icmp6
    ipVersion: Optional[str]  # ipv4,  ipv6
    destinationPort: Optional[str]  # 开始和结束port以:隔开
    sourcePort: Optional[str]  # 开始和结束port以:隔开
    sourceIpAddress: Optional[str]  # 类型,ingress, egress
    destinationIpAddress: Optional[str]  # 类型,ingress, egress
    action: Optional[str]  # accept, drop
    enabled: Optional[str]  # disable, enable
    description: Optional[str]  # 描述


@dataclass_json
@dataclass
class CtvpcListAclRuleReturnObjResponse:
    """接口业务数据"""
    aclID: Optional[str]  # id
    name: Optional[str]  # 名称
    description: Optional[str]  # 描述
    vpcID: Optional[str]  # VPC
    enabled: Optional[str]  # disable,enable
    inPolicyID: Optional[List[Optional[str]]]  # 入规则id数组
    outPolicyID: Optional[List[Optional[str]]]  # 出规则id数组
    inRules: Optional[List[Optional[CtvpcListAclRuleReturnObjInRulesResponse]]]  # 出规则id数组
    outRules: Optional[List[Optional[CtvpcListAclRuleReturnObjOutRulesResponse]]]  # 出规则id数组
    createdAt: Optional[str]  # 创建时间
    updatedAt: Optional[str]  # 更新时间
    subnetIDs: Optional[List[Optional[str]]]  # acl 绑定的子网 id


@dataclass_json
@dataclass
class CtvpcListAclRuleResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcListAclRuleReturnObjResponse]  # 接口业务数据



# 查看 Acl 规则列表
class CtvpcListAclRuleApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcListAclRuleRequest) -> CtvpcListAclRuleResponse:
        url = endpoint + "/v4/acl-rule/list"
        params = {'regionID':request.regionID, 'aclID':request.aclID}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtvpcListAclRuleResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
