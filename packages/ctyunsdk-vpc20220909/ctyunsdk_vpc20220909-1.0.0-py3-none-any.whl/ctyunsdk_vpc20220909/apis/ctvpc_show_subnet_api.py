from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcShowSubnetRequest:
    regionID: str  # 资源池 ID
    subnetID: str  # subnet 的 ID



@dataclass_json
@dataclass
class CtvpcShowSubnetReturnObjResponse:
    """接口业务数据"""
    subnetID: Optional[str]  # subnet ID
    name: Optional[str]  # 名称
    description: Optional[str]  # 描述
    vpcID: Optional[str]  # VpcID
    availabilityZones: Optional[List[Optional[str]]]  # 子网所在的可用区名
    routeTableID: Optional[str]  # 子网路由表 ID
    networkAclID: Optional[str]  # 子网 aclID
    CIDR: Optional[str]  # 子网网段，掩码范围为 16-28 位
    gatewayIP: Optional[str]  # 子网网关
    dhcpIP: Optional[str]  # dhcpIP
    start: Optional[str]  # 子网网段起始 IP
    end: Optional[str]  # 子网网段结束 IP
    availableIPCount: Any  # 子网内可用 IPv4 数目
    ipv6Enabled: Any  # 是否配置了ipv6网段，1 表示开启，0 表示未开启
    enableIpv6: Optional[bool]  # 是否开启 ipv6
    ipv6CIDR: Optional[str]  # 子网 Ipv6 网段，掩码范围为 16-28 位
    ipv6Start: Optional[str]  # 子网内可用的起始 IPv6 地址
    ipv6End: Optional[str]  # 子网内可用的结束 IPv6 地址
    ipv6GatewayIP: Optional[str]  # v6 网关地址
    dnsList: Optional[List[Optional[str]]]  # DNS 服务器地址:默认为空；必须为正确的 IPv4 格式；重新触发 DHCP 后生效，最大数组长度为 4
    systemDnsList: Optional[List[Optional[str]]]  # 系统自带DNS服务器地址
    ntpList: Optional[List[Optional[str]]]  # NTP 服务器地址: 默认为空，必须为正确的域名或 IPv4 格式；重新触发 DHCP 后生效，最大数组长度为 4
    type: Any  # 子网类型 :当前仅支持：0（普通子网）, 1（裸金属子网）
    createAt: Optional[str]  # 创建时间
    updateAt: Optional[str]  # 更新时间
    projectID: Optional[str]  # 企业项目


@dataclass_json
@dataclass
class CtvpcShowSubnetResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcShowSubnetReturnObjResponse]  # 接口业务数据



# 查询用户专有网络 VPC 下子网详情。
class CtvpcShowSubnetApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcShowSubnetRequest) -> CtvpcShowSubnetResponse:
        url = endpoint + "/v4/vpc/query-subnet"
        params = {'regionID':request.regionID, 'subnetID':request.subnetID}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtvpcShowSubnetResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
