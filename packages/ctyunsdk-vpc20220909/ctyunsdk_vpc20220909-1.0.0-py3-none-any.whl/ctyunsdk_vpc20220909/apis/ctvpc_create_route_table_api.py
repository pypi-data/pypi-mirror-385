from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcCreateRouteTableRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 区域id
    vpcID: str  # 关联的vpcID
    name: str  # 支持拉丁字母、中文、数字，下划线，连字符，中文 / 英文字母开头，不能以 http: / https: 开头，长度 2 - 32
    description: Optional[str] = None # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:{},./;'[]·！@#￥%……&*（） —— -+={},《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128 = None
    projectID: Optional[str] = None # 企业项目 ID，默认为0 = None



@dataclass_json
@dataclass
class CtvpcCreateRouteTableReturnObjResponse:
    """返回结果"""
    name: Optional[str]  # 路由表名字
    description: Optional[str]  # 路由表描述
    vpcID: Optional[str]  # 虚拟私有云 id
    id: Optional[str]  # 路由 id
    routeRulesCount: Any  # 路由表中的路由数
    createdAt: Optional[str]  # 创建时间
    updatedAt: Optional[str]  # 更新时间


@dataclass_json
@dataclass
class CtvpcCreateRouteTableResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcCreateRouteTableReturnObjResponse]  # 返回结果



# 创建路由表
class CtvpcCreateRouteTableApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcCreateRouteTableRequest) -> CtvpcCreateRouteTableResponse:
        url = endpoint + "/v4/vpc/route-table/create"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtvpcCreateRouteTableResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
