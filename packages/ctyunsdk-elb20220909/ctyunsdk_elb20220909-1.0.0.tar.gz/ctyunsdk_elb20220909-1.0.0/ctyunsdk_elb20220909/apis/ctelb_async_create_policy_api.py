from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbAsyncCreatePolicyTargetGroupSessionStickyRequest:
    """会话保持"""
    cookieName: Optional[str]  # cookie名称，当 sessionType 为 APP_COOKIE 时，为必填参数
    persistenceTimeout: Any  # 会话过期时间，当 sessionType 为 APP_COOKIE 或 SOURCE_IP 时，为必填参数
    sessionType: str  # 会话保持类型。取值范围：APP_COOKIE、HTTP_COOKIE、SOURCE_IP


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbAsyncCreatePolicyTargetGroupSessionStickyRequest':
        if not json_data:
            return None
        obj = CtelbAsyncCreatePolicyTargetGroupSessionStickyRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbAsyncCreatePolicyTargetGroupHealthCheckRequest:
    """健康检查配置"""
    protocol: str  # 健康检查协议。取值范围：TCP、UDP、HTTP
    timeout: Any  # 健康检查响应的最大超时时间，取值范围：2-60秒,默认为2秒
    interval: Any  # 负载均衡进行健康检查的时间间隔，取值范围：1-20940秒，默认5秒
    maxRetry: Any  # 最大重试次数，取值范围：1-10次，默认2次
    httpMethod: Optional[str]  # 仅当protocol为HTTP时必填且生效,HTTP请求的方法默认GET，{GET/HEAD}
    httpUrlPath: Optional[str]  # 仅当protocol为HTTP时必填且生效,支持的最大字符长度：80
    httpExpectedCodes: Optional[str]  # 仅当protocol为HTTP时必填且生效，最长支持64个字符，只能是三位数，可以以,分隔表示多个，或者以-分割表示范围，默认200


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbAsyncCreatePolicyTargetGroupHealthCheckRequest':
        if not json_data:
            return None
        obj = CtelbAsyncCreatePolicyTargetGroupHealthCheckRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbAsyncCreatePolicyTargetGroupTargetsRequest:
    instanceID: str  # 后端服务主机 id
    protocolPort: Any  # 后端服务监听端口
    instanceType: str  # 后端服务主机类型，目前支持 vm
    weight: Any  # 后端服务主机权重: 1 - 256
    address: str  # 后端服务主机主网卡所在的 IP


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbAsyncCreatePolicyTargetGroupTargetsRequest':
        if not json_data:
            return None
        obj = CtelbAsyncCreatePolicyTargetGroupTargetsRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbAsyncCreatePolicyTargetGroupRequest:
    """后端服务组"""
    name: str  # 后端服务组名字
    algorithm: str  # 负载均衡算法，支持: rr (轮询), lc (最少链接)
    targets: Optional[List[Optional[CtelbAsyncCreatePolicyTargetGroupTargetsRequest]]]  # 后端服务
    healthCheck: Optional[CtelbAsyncCreatePolicyTargetGroupHealthCheckRequest]  # 健康检查配置
    sessionSticky: Optional[CtelbAsyncCreatePolicyTargetGroupSessionStickyRequest]  # 会话保持


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbAsyncCreatePolicyTargetGroupRequest':
        if not json_data:
            return None
        obj = CtelbAsyncCreatePolicyTargetGroupRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbAsyncCreatePolicyConditionsRequest:
    ruleType: str  # 规则类型，支持 HOST（按照域名）、PATH（请求路径）
    matchType: str  # 匹配类型，支持 STARTS_WITH（前缀匹配）、EQUAL_TO（精确匹配）、REGEX（正则匹配）
    matchValue: str  # 被匹配的值，如果 ruleType 为 PATH，不能用 / 进行匹配


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbAsyncCreatePolicyConditionsRequest':
        if not json_data:
            return None
        obj = CtelbAsyncCreatePolicyConditionsRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbAsyncCreatePolicyRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 区域ID
    listenerID: str  # 监听器ID
    name: str  # 支持拉丁字母、中文、数字，下划线，连字符，中文 / 英文字母开头，不能以 http: / https: 开头，长度 2 - 32
    description: Optional[str]  # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:{},./;'[]·！@#￥%……&*（） —— -+={}\|《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128
    conditions: List[CtelbAsyncCreatePolicyConditionsRequest]  # 匹配规则数据
    targetGroup: CtelbAsyncCreatePolicyTargetGroupRequest  # 后端服务组


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbAsyncCreatePolicyRequest':
        if not json_data:
            return None
        obj = CtelbAsyncCreatePolicyRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbAsyncCreatePolicyReturnObjResponse:
    """返回结果"""
    status: Optional[str]  # 创建进度: in_progress / done
    message: Optional[str]  # 进度说明
    policyID: Optional[str]  # 转发策略 ID，可能为 null


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbAsyncCreatePolicyReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbAsyncCreatePolicyReturnObjResponse(None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbAsyncCreatePolicyResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtelbAsyncCreatePolicyReturnObjResponse]  # 返回结果


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbAsyncCreatePolicyResponse':
        if not json_data:
            return None
        obj = CtelbAsyncCreatePolicyResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 创建转发规则
class CtelbAsyncCreatePolicyApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbAsyncCreatePolicyRequest) -> CtelbAsyncCreatePolicyResponse:
        url = endpoint + "/v4/elb/async-create-policy"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtelbAsyncCreatePolicyResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
