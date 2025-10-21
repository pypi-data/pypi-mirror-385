from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbUpdateTargetGroupSessionStickyRequest:
    """会话保持配置"""
    sessionStickyMode: str  # 会话保持模式，支持取值：CLOSE（关闭）、INSERT（插入）、REWRITE（重写），当 algorithm 为 lc / sh 时，sessionStickyMode 必须为 CLOSE
    cookieExpire: Any  # cookie过期时间。INSERT模式必填
    rewriteCookieName: Optional[str]  # cookie重写名称，REWRITE模式必填
    sourceIpTimeout: Any  # 源IP会话保持超时时间。SOURCE_IP模式必填


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbUpdateTargetGroupSessionStickyRequest':
        if not json_data:
            return None
        obj = CtelbUpdateTargetGroupSessionStickyRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbUpdateTargetGroupRequest:
    clientToken: Optional[str]  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 区域ID
    projectID: Optional[str]  # 企业项目ID，默认为'0'
    iD: Optional[str]  # 后端主机组ID, 该字段后续废弃
    targetGroupID: str  # 后端主机组ID, 推荐使用该字段, 当同时使用 ID 和 targetGroupID 时，优先使用 targetGroupID
    name: Optional[str]  # 唯一。支持拉丁字母、中文、数字，下划线，连字符，中文 / 英文字母开头，不能以 http: / https: 开头，长度 2 - 32
    description: Optional[str]  # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:'{},./;'[,]·！@#￥%……&*（） —— -+={},《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128
    healthCheckID: Optional[str]  # 健康检查ID
    algorithm: Optional[str]  # 调度算法。取值范围：rr（轮询）、wrr（带权重轮询）、lc（最少连接）、sh（源IP哈希）
    proxyProtocol: Any  # 1 开启，0 关闭
    sessionSticky: Optional[CtelbUpdateTargetGroupSessionStickyRequest]  # 会话保持配置
    protocol: Optional[str]  # 协议，支持 TCP / UDP / HTTP / HTTPS / GENEVE


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbUpdateTargetGroupRequest':
        if not json_data:
            return None
        obj = CtelbUpdateTargetGroupRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbUpdateTargetGroupReturnObjResponse:
    iD: Optional[str]  # 后端主机组ID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbUpdateTargetGroupReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbUpdateTargetGroupReturnObjResponse(None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbUpdateTargetGroupResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[List[Optional[CtelbUpdateTargetGroupReturnObjResponse]]]  # 接口业务数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbUpdateTargetGroupResponse':
        if not json_data:
            return None
        obj = CtelbUpdateTargetGroupResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 更新后端主机组
class CtelbUpdateTargetGroupApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbUpdateTargetGroupRequest) -> CtelbUpdateTargetGroupResponse:
        url = endpoint + "/v4/elb/update-target-group"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtelbUpdateTargetGroupResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
