from typing import List, Optional, Dict, Any
from ctyunsdk_vpc20220909.core.client import CtyunClient
from ctyunsdk_vpc20220909.core.credential import Credential
from ctyunsdk_vpc20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcBatchCheckPortStatusRequest:
    regionID: str  # 区域id
    portIDs: str  # 多个网卡用 , 拼接起来, port-id,port-id, 最多支持同时检查 10 个网卡



@dataclass_json
@dataclass
class CtvpcBatchCheckPortStatusReturnObjResponse:
    id: Optional[str]  # 网卡 id
    status: Optional[str]  # 网卡状态,ready / unready / error / unknown


@dataclass_json
@dataclass
class CtvpcBatchCheckPortStatusResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[List[Optional[CtvpcBatchCheckPortStatusReturnObjResponse]]]  # 接口业务数据



# 网卡状态批量查询接口
class CtvpcBatchCheckPortStatusApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtvpcBatchCheckPortStatusRequest) -> CtvpcBatchCheckPortStatusResponse:
        url = endpoint + "/v4/ports/check-status-batch"
        params = {'regionID':request.regionID, 'portIDs':request.portIDs}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtvpcBatchCheckPortStatusResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
