from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbShowAccessControlRequest:
    regionID: str  # 区域ID
    id: Optional[str]  # 访问控制ID, 该字段后续废弃
    accessControlID: Optional[str]  # 访问控制ID, 推荐使用该字段, 当同时使用 id 和 accessControlID 时，优先使用 accessControlID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowAccessControlRequest':
        if not json_data:
            return None
        obj = CtelbShowAccessControlRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbShowAccessControlReturnObjResponse:
    """返回结果"""
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
    def from_json(json_data: dict) -> 'CtelbShowAccessControlReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbShowAccessControlReturnObjResponse(None,None,None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbShowAccessControlResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtelbShowAccessControlReturnObjResponse]  # 返回结果


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowAccessControlResponse':
        if not json_data:
            return None
        obj = CtelbShowAccessControlResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 查询策略地址组详情，访问控制采用黑、白名单方式实现，此接口为查询黑、白名单的地址组。
class CtelbShowAccessControlApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbShowAccessControlRequest) -> CtelbShowAccessControlResponse:
        url = endpoint + "/v4/elb/show-access-control"
        params = {'regionID':request.regionID, 'id':request.id, 'accessControlID':request.accessControlID}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtelbShowAccessControlResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
