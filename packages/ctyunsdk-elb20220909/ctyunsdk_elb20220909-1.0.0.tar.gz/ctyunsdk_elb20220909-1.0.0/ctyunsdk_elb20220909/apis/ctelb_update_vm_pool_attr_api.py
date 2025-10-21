from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbUpdateVmPoolAttrSessionStickyRequest:
    cookieName: Optional[str]  # cookie名称
    persistenceTimeout: Any  # 会话过期时间，1-86400
    sessionType: str  # 会话保持类型。取值范围：APP_COOKIE、HTTP_COOKIE、SOURCE_IP


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbUpdateVmPoolAttrSessionStickyRequest':
        if not json_data:
            return None
        obj = CtelbUpdateVmPoolAttrSessionStickyRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbUpdateVmPoolAttrHealthCheckRequest:
    protocol: str  # 健康检查协议。取值范围：TCP、UDP、HTTP
    timeout: Any  # 健康检查响应的最大超时时间，取值范围：2-60秒,默认2秒
    interval: Any  # 负载均衡进行健康检查的时间间隔，取值范围：1-20940秒，默认5秒
    maxRetry: Any  # 最大重试次数，取值范围：1-10次，默认2次
    httpMethod: Optional[str]  # 仅当protocol为HTTP时必填且生效,HTTP请求的方法默认GET，{GET/HEAD}
    httpUrlPath: Optional[str]  # 仅当protocol为HTTP时必填且生效,支持的最大字符长度：80
    httpExpectedCodes: Optional[str]  # 仅当protocol为HTTP时必填且生效，最长支持64个字符，只能是三位数，可以以,分隔表示多个，或者以-分割表示范围，默认200


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbUpdateVmPoolAttrHealthCheckRequest':
        if not json_data:
            return None
        obj = CtelbUpdateVmPoolAttrHealthCheckRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbUpdateVmPoolAttrRequest:
    regionID: str  # 区域ID
    targetGroupID: str  # 后端服务组ID
    name: Optional[str]  # 唯一。支持拉丁字母、中文、数字，下划线，连字符，中文 / 英文字母开头，不能以 http: / https: 开头，长度 2 - 32
    healthCheck: Optional[List[Optional[CtelbUpdateVmPoolAttrHealthCheckRequest]]]  # 当后端组已经有健康配置时，如果更新不传健康配置信息，表示移除当前后端组的健康检查配置
    sessionSticky: Optional[List[Optional[CtelbUpdateVmPoolAttrSessionStickyRequest]]]  # 当后端组已经有会话配置时，如果更新不传会话配置信息，表示移除当前后端组的会话配置


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbUpdateVmPoolAttrRequest':
        if not json_data:
            return None
        obj = CtelbUpdateVmPoolAttrRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbUpdateVmPoolAttrResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbUpdateVmPoolAttrResponse':
        if not json_data:
            return None
        obj = CtelbUpdateVmPoolAttrResponse(None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 更新后端服务组
class CtelbUpdateVmPoolAttrApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbUpdateVmPoolAttrRequest) -> CtelbUpdateVmPoolAttrResponse:
        url = endpoint + "/v4/elb/update-vm-pool"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtelbUpdateVmPoolAttrResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
