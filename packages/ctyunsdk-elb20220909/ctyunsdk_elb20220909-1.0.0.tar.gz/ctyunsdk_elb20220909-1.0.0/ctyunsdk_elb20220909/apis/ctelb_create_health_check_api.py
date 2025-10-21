from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbCreateHealthCheckRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 区域ID
    name: str  # 唯一。支持拉丁字母、中文、数字，下划线，连字符，中文 / 英文字母开头，不能以 http: / https: 开头，长度 2 - 32
    description: Optional[str]  # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:{},./;'[]·！@#￥%……&*（） —— -+={}\|《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128
    protocol: str  # 健康检查协议。取值范围：TCP、UDP、HTTP
    timeout: Any  # 健康检查响应的最大超时时间，取值范围：2-60秒，默认为2秒
    interval: Any  # 负载均衡进行健康检查的时间间隔，取值范围：1-20940秒，默认为5秒
    maxRetry: Any  # 最大重试次数，取值范围：1-10次，默认为2次
    httpMethod: Optional[str]  # 仅当protocol为HTTP时必填且生效,HTTP请求的方法默认GET，{GET/HEAD/POST/PUT/DELETE/TRACE/OPTIONS/CONNECT/PATCH}
    httpUrlPath: Optional[str]  # 仅当protocol为HTTP时必填且生效,默认为'/',支持的最大字符长度：80
    httpExpectedCodes: Optional[List[Optional[str]]]  # 仅当protocol为HTTP时必填且生效,支持http_2xx/http_3xx/http_4xx/http_5xx，一个或者多个的列表, 当 protocol 为 HTTP 时, 不填默认为 http_2xx
    protocolPort: Any  # 健康检查端口 1 - 65535


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbCreateHealthCheckRequest':
        if not json_data:
            return None
        obj = CtelbCreateHealthCheckRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbCreateHealthCheckReturnObjResponse:
    """返回结果"""
    iD: Optional[str]  # 健康检查ID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbCreateHealthCheckReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbCreateHealthCheckReturnObjResponse(None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbCreateHealthCheckResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtelbCreateHealthCheckReturnObjResponse]  # 返回结果


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbCreateHealthCheckResponse':
        if not json_data:
            return None
        obj = CtelbCreateHealthCheckResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 创建健康检查
class CtelbCreateHealthCheckApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbCreateHealthCheckRequest) -> CtelbCreateHealthCheckResponse:
        url = endpoint + "/v4/elb/create-health-check"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtelbCreateHealthCheckResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
