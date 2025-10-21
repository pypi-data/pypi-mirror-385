from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcShowPortRequest:
    regionID: str  # 资源池ID
    networkInterfaceID: str  # 虚拟网卡id



@dataclass_json
@dataclass
class CtvpcShowPortReturnObjAssociatedEipResponse:
    """关联的eip信息"""
    id: Optional[str] = None  # eip id
    name: Optional[str] = None  # eip名称


@dataclass_json
@dataclass
class CtvpcShowPortReturnObjResponse:
    """接口业务数据"""
    networkInterfaceName: Optional[str]  # 虚拟网名称
    networkInterfaceID: Optional[str]  # 虚拟网id
    vpcID: Optional[str]  # 所属vpc
    subnetID: Optional[str]  # 所属子网id
    role: Any  # 网卡类型: 0 主网卡， 1 弹性网卡
    macAddress: Optional[str]  # mac地址
    primaryPrivateIp: Optional[str]  # 主ip
    ipv6Addresses: Optional[List[Optional[str]]]  # ipv6地址
    instanceID: Optional[str]  # 关联的设备id
    instanceType: Optional[str]  # 设备类型 VM, BM, Other
    description: Optional[str]  # 描述
    securityGroupIds: Optional[List[Optional[str]]]  # 安全组ID列表
    secondaryPrivateIps: Optional[List[Optional[str]]]  # 辅助私网IP
    adminStatus: Optional[str]  # 是否启用DOWN, UP
    createdAt: Optional[str]  # 创建时间
    updatedAt: Optional[str]  # 更新时间
    associatedEip: Optional[CtvpcShowPortReturnObjAssociatedEipResponse]  # 关联的eip信息


@dataclass_json
@dataclass
class CtvpcShowPortResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcShowPortReturnObjResponse]  # 接口业务数据



# 查询网卡信息
class CtvpcShowPortApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcShowPortRequest) -> CtvpcShowPortResponse:
        url = endpoint + "/v4/ports/show"
        params = {'regionID':request.regionID, 'networkInterfaceID':request.networkInterfaceID}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            print("show port res:", response.json())
            return CtvpcShowPortResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
