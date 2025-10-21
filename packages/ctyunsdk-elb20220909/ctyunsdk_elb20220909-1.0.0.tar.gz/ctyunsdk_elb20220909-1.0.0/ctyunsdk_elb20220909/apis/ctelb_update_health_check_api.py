from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbUpdateHealthCheckRequest:
    clientToken: Optional[str]  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 区域ID,公共参数不支持修改
    iD: Optional[str]  # 健康检查ID, 后续废弃该字段
    healthCheckID: str  # 健康检查ID, 推荐使用该字段, 当同时使用 ID 和 healthCheckID 时，优先使用 healthCheckID
    name: Optional[str]  # 唯一。支持拉丁字母、中文、数字，下划线，连字符，中文 / 英文字母开头，不能以 http: / https: 开头，长度 2 - 32
    description: Optional[str]  # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:{},./;'[]·！@#￥%……&*（） —— -+={}\|《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128
    timeout: Any  # 健康检查响应的最大超时时间，取值范围：2-60秒，默认为2秒
    maxRetry: Any  # 最大重试次数，取值范围：1-10次，默认为2次
    interval: Any  # 负载均衡进行健康检查的时间间隔，取值范围：1-20940秒，默认为5秒
    httpMethod: Optional[str]  # HTTP请求的方法默认GET，{GET/HEAD/POST/PUT/DELETE/TRACE/OPTIONS/CONNECT/PATCH}（创建时仅当protocol为HTTP时必填且生效）
    httpUrlPath: Optional[str]  # 创建时仅当protocol为HTTP时必填且生效,支持的最大字符长度：80
    httpExpectedCodes: Optional[List[Optional[str]]]  # 仅当protocol为HTTP时必填且生效,支持{http_2xx/http_3xx/http_4xx/http_5xx}


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbUpdateHealthCheckRequest':
        if not json_data:
            return None
        obj = CtelbUpdateHealthCheckRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbUpdateHealthCheckResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbUpdateHealthCheckResponse':
        if not json_data:
            return None
        obj = CtelbUpdateHealthCheckResponse(None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 更新健康检查
class CtelbUpdateHealthCheckApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbUpdateHealthCheckRequest) -> CtelbUpdateHealthCheckResponse:
        url = endpoint + "/v4/elb/update-health-check"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtelbUpdateHealthCheckResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
