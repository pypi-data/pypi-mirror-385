from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbGwlbListRequest:
    regionID: str  # 资源池 ID
    projectID: Optional[str]  # 企业项目ID，默认"0"
    gwLbID: Optional[str]  # 网关负载均衡ID
    pageNumber: Any  # 列表的页码，默认值为 1。
    pageSize: Any  # 分页查询时每页的行数，最大值为 50，默认值为 10。


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbGwlbListRequest':
        if not json_data:
            return None
        obj = CtelbGwlbListRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbGwlbListReturnObjResultsResponse:
    gwLbID: Optional[str]  # 网关负载均衡 ID
    name: Optional[str]  # 名字
    description: Optional[str]  # 描述
    vpcID: Optional[str]  # 虚拟私有云 ID
    subnetID: Optional[str]  # 子网 ID
    portID: Optional[str]  # 网卡 ID
    ipv6Enabled: Optional[bool]  # 是否开启 ipv6
    privateIpAddress: Optional[str]  # 私有 IP 地址
    ipv6Address: Optional[str]  # ipv6 地址
    slaName: Optional[str]  # 规格
    deleteProtection: Optional[bool]  # 是否开启删除保护
    createdAt: Optional[str]  # 创建时间
    updatedAt: Optional[str]  # 更新时间


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbGwlbListReturnObjResultsResponse':
        if not json_data:
            return None
        obj = CtelbGwlbListReturnObjResultsResponse(None,None,None,None,None,None,None,None,None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbGwlbListReturnObjResponse:
    """接口业务数据"""
    results: Optional[List[Optional[CtelbGwlbListReturnObjResultsResponse]]]  # 接口业务数据
    totalCount: Any  # 列表条目数
    currentCount: Any  # 分页查询时每页的行数。
    totalPage: Any  # 总页数


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbGwlbListReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbGwlbListReturnObjResponse(None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbGwlbListResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtelbGwlbListReturnObjResponse]  # 接口业务数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbGwlbListResponse':
        if not json_data:
            return None
        obj = CtelbGwlbListResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 查看网关负载均衡列表
class CtelbGwlbListApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbGwlbListRequest) -> CtelbGwlbListResponse:
        url = endpoint + "/v4/gwlb/list"
        params = {'regionID':request.regionID, 'projectID':request.projectID, 'gwLbID':request.gwLbID, 'pageNumber':request.pageNumber, 'pageSize':request.pageSize}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtelbGwlbListResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
