from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbUpdateListenerIdleTimeoutRequest:
    regionID: str  # 区域ID
    listenerID: str  # 监听器ID
    idleTimeout: Any  # 链接空闲断开超时时间，单位秒，取值范围：1 - 300


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbUpdateListenerIdleTimeoutRequest':
        if not json_data:
            return None
        obj = CtelbUpdateListenerIdleTimeoutRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbUpdateListenerIdleTimeoutReturnObjResponse:
    """ID"""
    listenerID: Optional[str]  # ID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbUpdateListenerIdleTimeoutReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbUpdateListenerIdleTimeoutReturnObjResponse(None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbUpdateListenerIdleTimeoutResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtelbUpdateListenerIdleTimeoutReturnObjResponse]  # ID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbUpdateListenerIdleTimeoutResponse':
        if not json_data:
            return None
        obj = CtelbUpdateListenerIdleTimeoutResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 设置监听器 Idle Timeout
class CtelbUpdateListenerIdleTimeoutApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbUpdateListenerIdleTimeoutRequest) -> CtelbUpdateListenerIdleTimeoutResponse:
        url = endpoint + "/v4/elb/update-listener-idle-timeout"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtelbUpdateListenerIdleTimeoutResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
