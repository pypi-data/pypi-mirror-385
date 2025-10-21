from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbListAccessControlRequest:
    regionID: str  # 区域ID
    iDs: Optional[List[Optional[str]]]  # 访问控制ID列表
    name: Optional[str]  # 访问控制名称,只能由数字，字母，-组成不能以数字和-开头，最大长度32


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListAccessControlRequest':
        if not json_data:
            return None
        obj = CtelbListAccessControlRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbListAccessControlReturnObjResponse:
    azName: Optional[str]  # 可用区名称
    projectID: Optional[str]  # 项目ID
    iD: Optional[str]  # 访问控制ID
    name: Optional[str]  # 访问控制名称
    description: Optional[str]  # 描述
    sourceIps: Optional[List[Optional[str]]]  # IP地址的集合或者CIDR
    createTime: Optional[str]  # 创建时间，为UTC格式


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListAccessControlReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbListAccessControlReturnObjResponse(None,None,None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbListAccessControlResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[List[Optional[CtelbListAccessControlReturnObjResponse]]]  # 返回结果


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListAccessControlResponse':
        if not json_data:
            return None
        obj = CtelbListAccessControlResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 查询策略地址组，访问控制采用黑、白名单方式实现，此接口为查询黑、白名单的地址组。
class CtelbListAccessControlApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbListAccessControlRequest) -> CtelbListAccessControlResponse:
        url = endpoint + "/v4/elb/list-access-control"
        params = {'regionID':request.regionID, 'iDs':request.iDs, 'name':request.name}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtelbListAccessControlResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
