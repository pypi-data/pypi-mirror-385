from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbGwlbCreateRequest:
    regionID: str  # 区域ID
    clientToken: str  # 客户端存根，用于保证订单幂等性。要求单个云平台账户内唯一
    projectID: Optional[str]  # 企业项目ID，默认"0"
    subnetID: str  # 子网 ID
    name: str  # 支持拉丁字母、中文、数字，下划线，连字符，中文 / 英文字母开头，不能以 http: / https: 开头，长度 2 - 32
    description: Optional[str]  # 支持拉丁字母、中文、数字, 特殊字符：~!@#$%^&*()_-+= <>?:"{},./;'[\]·！@#￥%……&*（） —— -+={}\《》？：“”【】、；‘'，。、，不能以 http: / https: 开头，长度 0 - 128
    privateIpAddress: Optional[str]  # 私有 ip 地址
    ipv6Address: Optional[str]  # ipv6 地址
    deleteProtection: Optional[bool]  # 是否开启删除保护，默认为 False
    ipv6Enabled: Optional[bool]  # 是否开启 ipv6，默认为 False
    cycleType: str  # 仅支持按需
    payVoucherPrice: Optional[str]  # 代金券金额，支持到小数点后两位


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbGwlbCreateRequest':
        if not json_data:
            return None
        obj = CtelbGwlbCreateRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbGwlbCreateReturnObjResponse:
    """接口业务数据"""
    masterOrderID: Optional[str]  # 订单id。
    masterOrderNO: Optional[str]  # 订单编号, 可以为 null。
    masterResourceStatus: Optional[str]  # 资源状态: started（启用） / renewed（续订） / refunded（退订） / destroyed（销毁） / failed（失败） / starting（正在启用） / changed（变配）/ expired（过期）/ unknown（未知）
    masterResourceID: Optional[str]  # 资源 ID 可以为 null。
    regionID: Optional[str]  # 可用区id。
    gwLbID: Optional[str]  # 网关负载均衡 ID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbGwlbCreateReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbGwlbCreateReturnObjResponse(None,None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbGwlbCreateResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtelbGwlbCreateReturnObjResponse]  # 接口业务数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbGwlbCreateResponse':
        if not json_data:
            return None
        obj = CtelbGwlbCreateResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 创建网关负载均衡
class CtelbGwlbCreateApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbGwlbCreateRequest) -> CtelbGwlbCreateResponse:
        url = endpoint + "/v4/gwlb/create"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtelbGwlbCreateResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
