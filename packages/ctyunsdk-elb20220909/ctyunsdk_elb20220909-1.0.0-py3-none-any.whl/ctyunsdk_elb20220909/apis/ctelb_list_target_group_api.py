from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbListTargetGroupRequest:
    clientToken: Optional[str]  # 客户端存根，用于保证订单幂等性。要求单个云平台账户内唯一
    regionID: str  # 区域ID
    iDs: Optional[str]  # 后端主机组ID列表，以,分隔
    vpcID: Optional[str]  # vpc ID
    healthCheckID: Optional[str]  # 健康检查ID
    name: Optional[str]  # 后端主机组名称


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListTargetGroupRequest':
        if not json_data:
            return None
        obj = CtelbListTargetGroupRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbListTargetGroupReturnObjSessionStickyResponse:
    sessionStickyMode: Optional[str]  # 会话保持模式，支持取值：CLOSE（关闭）、INSERT（插入）、REWRITE（重写
    cookieExpire: Any  # cookie过期时间
    rewriteCookieName: Optional[str]  # cookie重写名称
    sourceIpTimeout: Any  # 源IP会话保持超时时间。


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListTargetGroupReturnObjSessionStickyResponse':
        if not json_data:
            return None
        obj = CtelbListTargetGroupReturnObjSessionStickyResponse(None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbListTargetGroupReturnObjResponse:
    regionID: Optional[str]  # 区域ID
    azName: Optional[str]  # 可用区名称
    projectID: Optional[str]  # 项目ID
    iD: Optional[str]  # 后端主机组ID
    name: Optional[str]  # 后端主机组名称
    description: Optional[str]  # 描述
    vpcID: Optional[str]  # vpc ID
    healthCheckID: Optional[str]  # 健康检查ID
    algorithm: Optional[str]  # 调度算法
    sessionSticky: Optional[List[Optional[CtelbListTargetGroupReturnObjSessionStickyResponse]]]  # 会话保持配置
    status: Optional[str]  # 状态: DOWN / ACTIVE
    createdTime: Optional[str]  # 创建时间，为UTC格式
    updatedTime: Optional[str]  # 更新时间，为UTC格式


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListTargetGroupReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbListTargetGroupReturnObjResponse(None,None,None,None,None,None,None,None,None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbListTargetGroupResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[List[Optional[CtelbListTargetGroupReturnObjResponse]]]  # 接口业务数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListTargetGroupResponse':
        if not json_data:
            return None
        obj = CtelbListTargetGroupResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 查看后端主机组列表
class CtelbListTargetGroupApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbListTargetGroupRequest) -> CtelbListTargetGroupResponse:
        url = endpoint + "/v4/elb/list-target-group"
        params = {'clientToken':request.clientToken, 'regionID':request.regionID, 'iDs':request.iDs, 'vpcID':request.vpcID, 'healthCheckID':request.healthCheckID, 'name':request.name}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtelbListTargetGroupResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
