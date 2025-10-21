from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbListVmPoolRequest:
    regionID: str  # 区域ID
    targetGroupID: Optional[str]  # 后端服务组ID
    name: Optional[str]  # 后端服务组名称


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListVmPoolRequest':
        if not json_data:
            return None
        obj = CtelbListVmPoolRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbListVmPoolReturnObjSessionStickyResponse:
    sessionStickyMode: Optional[str]  # 会话保持模式
    cookieExpire: Any  # cookie过期时间
    rewriteCookieName: Optional[str]  # cookie重写名称
    sourceIpTimeout: Any  # 源IP会话保持超时时间。


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListVmPoolReturnObjSessionStickyResponse':
        if not json_data:
            return None
        obj = CtelbListVmPoolReturnObjSessionStickyResponse(None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbListVmPoolReturnObjResponse:
    regionID: Optional[str]  # 区域ID
    azName: Optional[str]  # 可用区名称, 默认为 null
    projectID: Optional[str]  # 项目ID
    iD: Optional[str]  # 后端服务组ID
    name: Optional[str]  # 后端服务组名称
    description: Optional[str]  # 描述
    vpcID: Optional[str]  # vpc ID, 默认为 null
    healthCheckID: Optional[str]  # 健康检查ID
    algorithm: Optional[str]  # 调度算法
    sessionSticky: Optional[List[Optional[CtelbListVmPoolReturnObjSessionStickyResponse]]]  # 会话保持配置
    status: Optional[str]  # 状态
    createdTime: Optional[str]  # 创建时间，为UTC格式
    updatedTime: Optional[str]  # 更新时间，为UTC格式, 默认为 null


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListVmPoolReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbListVmPoolReturnObjResponse(None,None,None,None,None,None,None,None,None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbListVmPoolResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[List[Optional[CtelbListVmPoolReturnObjResponse]]]  # 接口业务数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListVmPoolResponse':
        if not json_data:
            return None
        obj = CtelbListVmPoolResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 查看后端服务组列表
class CtelbListVmPoolApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbListVmPoolRequest) -> CtelbListVmPoolResponse:
        url = endpoint + "/v4/elb/list-vm-pool"
        params = {'regionID':request.regionID, 'targetGroupID':request.targetGroupID, 'name':request.name}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtelbListVmPoolResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
