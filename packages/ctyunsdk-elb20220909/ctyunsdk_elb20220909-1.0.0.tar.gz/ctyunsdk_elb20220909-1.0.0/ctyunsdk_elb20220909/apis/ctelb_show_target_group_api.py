from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbShowTargetGroupRequest:
    regionID: str  # 区域ID
    iD: Optional[str]  # 后端主机组ID, 该字段后续废弃
    targetGroupID: str  # 后端主机组ID, 推荐使用该字段, 当同时使用 ID 和 targetGroupID 时，优先使用 targetGroupID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowTargetGroupRequest':
        if not json_data:
            return None
        obj = CtelbShowTargetGroupRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbShowTargetGroupReturnObjSessionStickyResponse:
    sessionStickyMode: Optional[str]  # 会话保持模式，支持取值：CLOSE（关闭）、INSERT（插入）、REWRITE（重写
    cookieExpire: Any  # cookie过期时间
    rewriteCookieName: Optional[str]  # cookie重写名称
    sourceIpTimeout: Any  # 源IP会话保持超时时间。


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowTargetGroupReturnObjSessionStickyResponse':
        if not json_data:
            return None
        obj = CtelbShowTargetGroupReturnObjSessionStickyResponse(None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbShowTargetGroupReturnObjResponse:
    regionID: Optional[str]  # 区域ID
    azName: Optional[str]  # 可用区名称
    projectID: Optional[str]  # 项目ID
    iD: Optional[str]  # 后端主机组ID
    name: Optional[str]  # 后端主机组名称
    description: Optional[str]  # 描述
    vpcID: Optional[str]  # vpc ID
    healthCheckID: Optional[str]  # 健康检查ID
    algorithm: Optional[str]  # 调度算法
    sessionSticky: Optional[List[Optional[CtelbShowTargetGroupReturnObjSessionStickyResponse]]]  # 会话保持配置
    status: Optional[str]  # 状态: DOWN / ACTIVE
    createdTime: Optional[str]  # 创建时间，为UTC格式
    updatedTime: Optional[str]  # 更新时间，为UTC格式


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowTargetGroupReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbShowTargetGroupReturnObjResponse(None,None,None,None,None,None,None,None,None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbShowTargetGroupResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[List[Optional[CtelbShowTargetGroupReturnObjResponse]]]  # 接口业务数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowTargetGroupResponse':
        if not json_data:
            return None
        obj = CtelbShowTargetGroupResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 查看后端主机组信息
class CtelbShowTargetGroupApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbShowTargetGroupRequest) -> CtelbShowTargetGroupResponse:
        url = endpoint + "/v4/elb/show-target-group"
        params = {'regionID':request.regionID, 'iD':request.iD, 'targetGroupID':request.targetGroupID}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtelbShowTargetGroupResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
