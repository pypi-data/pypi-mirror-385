from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbGwlbShowRequest:
    regionID: str  # 资源池 ID
    projectID: Optional[str]  # 企业项目ID，默认"0"
    gwLbID: str  # 网关负载均衡ID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbGwlbShowRequest':
        if not json_data:
            return None
        obj = CtelbGwlbShowRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbGwlbShowReturnObjResponse:
    """接口业务数据"""
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
    def from_json(json_data: dict) -> 'CtelbGwlbShowReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbGwlbShowReturnObjResponse(None,None,None,None,None,None,None,None,None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbGwlbShowResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtelbGwlbShowReturnObjResponse]  # 接口业务数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbGwlbShowResponse':
        if not json_data:
            return None
        obj = CtelbGwlbShowResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 查看网关负载均衡详情
class CtelbGwlbShowApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbGwlbShowRequest) -> CtelbGwlbShowResponse:
        url = endpoint + "/v4/gwlb/show"
        params = {'regionID':request.regionID, 'projectID':request.projectID, 'gwLbID':request.gwLbID}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtelbGwlbShowResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
