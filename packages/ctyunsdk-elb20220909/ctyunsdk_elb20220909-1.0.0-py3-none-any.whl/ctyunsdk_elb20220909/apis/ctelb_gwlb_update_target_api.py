from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbGwlbUpdateTargetRequest:
    regionID: str  # 资源池 ID
    targetID: str  # 后端服务 ID
    description: Optional[str]  # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:"{},./;'[\]·！@#￥%……&*（） —— -+={}\《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128
    weight: Any  # 权重，仅支持填 100


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbGwlbUpdateTargetRequest':
        if not json_data:
            return None
        obj = CtelbGwlbUpdateTargetRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbGwlbUpdateTargetReturnObjResponse:
    """接口业务数据"""
    targetID: Optional[str]  # 后端服务ID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbGwlbUpdateTargetReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbGwlbUpdateTargetReturnObjResponse(None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbGwlbUpdateTargetResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtelbGwlbUpdateTargetReturnObjResponse]  # 接口业务数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbGwlbUpdateTargetResponse':
        if not json_data:
            return None
        obj = CtelbGwlbUpdateTargetResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 更新target
class CtelbGwlbUpdateTargetApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbGwlbUpdateTargetRequest) -> CtelbGwlbUpdateTargetResponse:
        url = endpoint + "/v4/gwlb/update-target"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtelbGwlbUpdateTargetResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
