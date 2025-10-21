from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcAclCloneRequest:
    regionID: str  # 资源池ID
    destRegionID: str  # 目标资源池，仅支持从4.0资源池复制到4.0资源池
    srcAclID: str  # 源aclID
    vpcID: str  # 目标资源池得到的acl归属的vpc
    name: str  # 支持拉丁字母、中文、数字，下划线，连字符，中文 / 英文字母开头，不能以 http: / https: 开头，长度 2 - 32

@dataclass_json
@dataclass
class CtvpcAclCloneReturnObjResponse:
    """接口业务数据"""
    aclID: Optional[str]  # acl id
    name: Optional[str]  # acl 名称

@dataclass_json
@dataclass
class CtvpcAclCloneResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    requestID: Optional[str]  # 请求 id
    returnObj: Optional[CtvpcAclCloneReturnObjResponse]  # 接口业务数据

# 克隆 Acl,仅实现acl的规则复制，不包括关联资源和相关属性
class CtvpcAclCloneApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)

    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint

    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str,
           request: CtvpcAclCloneRequest) -> CtvpcAclCloneResponse:
        url = endpoint + "/v4/acl/clone"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict,
                                   credential=credential)
            return CtvpcAclCloneResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
