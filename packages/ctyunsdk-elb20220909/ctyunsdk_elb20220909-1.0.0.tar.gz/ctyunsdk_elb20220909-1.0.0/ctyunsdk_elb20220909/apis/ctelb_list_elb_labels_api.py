from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbListElbLabelsRequest:
    regionID: str  # 区域ID
    elbID: str  # 负载均衡 ID
    pageNo: Any  # 列表的页码，默认值为 1, 推荐使用该字段, pageNumber 后续会废弃
    pageSize: Any  # 分页查询时每页的行数，最大值为 50，默认值为 10。


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListElbLabelsRequest':
        if not json_data:
            return None
        obj = CtelbListElbLabelsRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbListElbLabelsReturnObjResultsResponse:
    labelID: Optional[str]  # 标签 id
    labelKey: Optional[str]  # 标签名
    labelValue: Optional[str]  # 标签值


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListElbLabelsReturnObjResultsResponse':
        if not json_data:
            return None
        obj = CtelbListElbLabelsReturnObjResultsResponse(None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbListElbLabelsReturnObjResponse:
    """返回结果"""
    results: Optional[List[Optional[CtelbListElbLabelsReturnObjResultsResponse]]]  # 绑定的标签列表
    totalCount: Optional[str]  # 列表条目数
    currentCount: Optional[str]  # 分页查询时每页的行数。
    totalPage: Optional[str]  # 总页数


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListElbLabelsReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbListElbLabelsReturnObjResponse(None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbListElbLabelsResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtelbListElbLabelsReturnObjResponse]  # 返回结果


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListElbLabelsResponse':
        if not json_data:
            return None
        obj = CtelbListElbLabelsResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 获取负载均衡绑定的标签
class CtelbListElbLabelsApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbListElbLabelsRequest) -> CtelbListElbLabelsResponse:
        url = endpoint + "/v4/elb/list-labels"
        params = {'regionID':request.regionID, 'elbID':request.elbID, 'pageNo':request.pageNo, 'pageSize':request.pageSize}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtelbListElbLabelsResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
