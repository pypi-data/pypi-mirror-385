from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbElbCreateAccessLogRequest:
    clientToken: Optional[str]  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 区域ID
    elbID: str  # 负载均衡ID
    projectCode: str  # 日志项目ID
    projectName: str  # 日志项目名称
    unitCode: str  # 日志单元ID
    unitName: str  # 日志单元名称
    logCollection: Any  # 0:关闭日志收集 1:启用日志收集


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbElbCreateAccessLogRequest':
        if not json_data:
            return None
        obj = CtelbElbCreateAccessLogRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbElbCreateAccessLogReturnObjResponse:
    id: Optional[str]  # 访问日志ID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbElbCreateAccessLogReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbElbCreateAccessLogReturnObjResponse(None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbElbCreateAccessLogResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[List[Optional[CtelbElbCreateAccessLogReturnObjResponse]]]  # 返回结果


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbElbCreateAccessLogResponse':
        if not json_data:
            return None
        obj = CtelbElbCreateAccessLogResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 创建elb流日志
class CtelbElbCreateAccessLogApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbElbCreateAccessLogRequest) -> CtelbElbCreateAccessLogResponse:
        url = endpoint + "/v4/elb/add-access-log"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtelbElbCreateAccessLogResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
