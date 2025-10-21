from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbQueryRenewPgelbPriceRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 区域ID
    elbID: str  # 负载均衡 ID
    cycleType: str  # 订购类型：month（包月） / year（包年）
    cycleCount: Any  # 订购时长, 当 cycleType = month, 支持续订 1 - 11 个月; 当 cycleType = year, 支持续订 1 - 3 年


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbQueryRenewPgelbPriceRequest':
        if not json_data:
            return None
        obj = CtelbQueryRenewPgelbPriceRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbQueryRenewPgelbPriceReturnObjSubOrderPricesOrderItemPricesResponse:
    resourceType: Optional[str]  # 资源类型
    totalPrice: Optional[str]  # 总价格（单位：元）
    finalPrice: Optional[str]  # 最终价格（单位：元）


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbQueryRenewPgelbPriceReturnObjSubOrderPricesOrderItemPricesResponse':
        if not json_data:
            return None
        obj = CtelbQueryRenewPgelbPriceReturnObjSubOrderPricesOrderItemPricesResponse(None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbQueryRenewPgelbPriceReturnObjSubOrderPricesResponse:
    serviceTag: Optional[str]  # 服务类型
    totalPrice: Any  # 子订单总价格（单位：元）
    finalPrice: Any  # 最终价格（单位：元）
    orderItemPrices: Optional[List[Optional[CtelbQueryRenewPgelbPriceReturnObjSubOrderPricesOrderItemPricesResponse]]]  # item价格信息


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbQueryRenewPgelbPriceReturnObjSubOrderPricesResponse':
        if not json_data:
            return None
        obj = CtelbQueryRenewPgelbPriceReturnObjSubOrderPricesResponse(None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbQueryRenewPgelbPriceReturnObjResponse:
    """业务数据"""
    totalPrice: Any  # 总价格（单位：元）
    discountPrice: Any  # 折后价格（单位：元）
    finalPrice: Any  # 最终价格（单位：元）
    subOrderPrices: Optional[List[Optional[CtelbQueryRenewPgelbPriceReturnObjSubOrderPricesResponse]]]  # 子订单价格信息


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbQueryRenewPgelbPriceReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbQueryRenewPgelbPriceReturnObjResponse(None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbQueryRenewPgelbPriceResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtelbQueryRenewPgelbPriceReturnObjResponse]  # 业务数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbQueryRenewPgelbPriceResponse':
        if not json_data:
            return None
        obj = CtelbQueryRenewPgelbPriceResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 保障型负载均衡续订询价
class CtelbQueryRenewPgelbPriceApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbQueryRenewPgelbPriceRequest) -> CtelbQueryRenewPgelbPriceResponse:
        url = endpoint + "/v4/elb/query-renew-price"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtelbQueryRenewPgelbPriceResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
