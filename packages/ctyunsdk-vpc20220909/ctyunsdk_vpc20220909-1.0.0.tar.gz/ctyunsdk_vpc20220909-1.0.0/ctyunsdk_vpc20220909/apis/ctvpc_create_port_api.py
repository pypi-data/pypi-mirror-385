from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcCreatePortRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 资源池ID
    subnetID: str  # 子网ID
    secondaryPrivateIpCount: Any  # 指定私有IP地址数量，让ECS为您自动创建IP地址
    primaryPrivateIp: Optional[str] = None # 弹性网卡的主私有IP地址 = None
    ipv6Addresses: Optional[List[Optional[str]]] = None # 为弹性网卡指定一个或多个IPv6地址 = None
    securityGroupIds: Optional[List[Optional[str]]] = None # 加入一个或多个安全组。安全组和弹性网卡必须在同一个专有网络VPC中，最多同时支持 10 个 = None
    secondaryPrivateIps: Optional[List[Optional[str]]] = None # 指定私有IP地址，不能和secondaryPrivateIpCount同时指定 = None
    name: Optional[str] = None # 支持拉丁字母、中文、数字，下划线，连字符，中文 / 英文字母开头，不能以 http: / https: 开头，长度 2 - 32 = None
    description: Optional[str] = None # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:{},./;'[]·！@#￥%……&*（） —— -+={}\《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128 = None



@dataclass_json
@dataclass
class CtvpcCreatePortReturnObjResponse:
    """返回结果"""
    vpcID: Optional[str]  # vpc的id
    subnetID: Optional[str]  # 子网id
    networkInterfaceID: Optional[str]  # 网卡id
    networkInterfaceName: Optional[str]  # 网卡名称
    macAddress: Optional[str]  # mac地址
    description: Optional[str]  # 网卡描述
    ipv6Address: Optional[List[Optional[str]]]  # IPv6地址列表
    securityGroupIds: Optional[List[Optional[str]]]  # 安全组ID列表
    secondaryPrivateIps: Optional[List[Optional[str]]]  # 二级IP地址列表
    privateIpAddress: Optional[str]  # 弹性网卡的主私有IP
    instanceOwnerID: Optional[str]  # 绑定的实例的所有者ID
    instanceType: Optional[str]  # 设备类型 VM, BM, Other
    instanceID: Optional[str]  # 绑定的实例ID
    createdAt: Optional[str]  # 创建时间
    updatedAt: Optional[str]  # 更新时间


@dataclass_json
@dataclass
class CtvpcCreatePortResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcCreatePortReturnObjResponse]  # 返回结果



# 创建弹性网卡
class CtvpcCreatePortApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcCreatePortRequest) -> CtvpcCreatePortResponse:
        url = endpoint + "/v4/ports/create"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtvpcCreatePortResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
