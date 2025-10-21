from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbQuerySlaRequest:
    regionID: str  # 区域ID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbQuerySlaRequest':
        if not json_data:
            return None
        obj = CtelbQuerySlaRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbQuerySlaReturnObjResponse:
    regionID: Optional[str]  # 区域ID
    azName: Optional[str]  # az名称
    projectID: Optional[str]  # 项目ID
    iD: Optional[str]  # 规格ID
    name: Optional[str]  # 规格名称
    description: Optional[str]  # 规格描述
    spec: Optional[str]  # 规格类型: 标准型I / 标准型II / 增强型I / 增强型II / 高阶型I / 高阶型II / 存量 /免费型


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbQuerySlaReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbQuerySlaReturnObjResponse(None,None,None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbQuerySlaResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[List[Optional[CtelbQuerySlaReturnObjResponse]]]  # 接口业务数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbQuerySlaResponse':
        if not json_data:
            return None
        obj = CtelbQuerySlaResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 查看规格列表
class CtelbQuerySlaApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbQuerySlaRequest) -> CtelbQuerySlaResponse:
        url = endpoint + "/v4/elb/query-sla"
        params = {'regionID':request.regionID}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtelbQuerySlaResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
