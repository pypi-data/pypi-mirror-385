from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbListTargetRequest:
    regionID: str  # 区域ID
    targetGroupID: Optional[str]  # 后端主机组ID
    iDs: Optional[str]  # 后端主机ID列表，以,分隔


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListTargetRequest':
        if not json_data:
            return None
        obj = CtelbListTargetRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbListTargetReturnObjResponse:
    regionID: Optional[str]  # 区域ID
    azName: Optional[str]  # 可用区名称
    projectID: Optional[str]  # 项目ID
    iD: Optional[str]  # 后端主机ID
    targetGroupID: Optional[str]  # 后端主机组ID
    description: Optional[str]  # 描述
    instanceType: Optional[str]  # 实例类型: VM / BM
    instanceID: Optional[str]  # 实例ID
    protocolPort: Any  # 协议端口
    weight: Any  # 权重
    healthCheckStatus: Optional[str]  # IPv4的健康检查状态: offline / online / unknown
    healthCheckStatusIpv6: Optional[str]  # IPv6的健康检查状态: offline / online / unknown
    status: Optional[str]  # 状态: DOWN / ACTIVE
    createdTime: Optional[str]  # 创建时间，为UTC格式
    updatedTime: Optional[str]  # 更新时间，为UTC格式


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListTargetReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbListTargetReturnObjResponse(None,None,None,None,None,None,None,None,None,None,None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbListTargetResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[List[Optional[CtelbListTargetReturnObjResponse]]]  # 接口业务数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListTargetResponse':
        if not json_data:
            return None
        obj = CtelbListTargetResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 查看后端主机列表
class CtelbListTargetApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbListTargetRequest) -> CtelbListTargetResponse:
        url = endpoint + "/v4/elb/list-target"
        params = {'regionID':request.regionID, 'targetGroupID':request.targetGroupID, 'iDs':request.iDs}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtelbListTargetResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
