from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbQueryModifyPgelbSpecPriceRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 区域ID
    elbID: str  # 负载均衡 ID
    slaName: str  # lb的规格名称, 支持:elb.s2.small，elb.s3.small，elb.s4.small，elb.s5.small，elb.s2.large，elb.s3.large，elb.s4.large，elb.s5.large


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbQueryModifyPgelbSpecPriceRequest':
        if not json_data:
            return None
        obj = CtelbQueryModifyPgelbSpecPriceRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbQueryModifyPgelbSpecPriceReturnObjSubOrderPricesOrderItemPricesResponse:
    resourceType: Optional[str]  # 资源类型
    totalPrice: Optional[str]  # 总价格（单位：元）
    finalPrice: Optional[str]  # 最终价格（单位：元）


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbQueryModifyPgelbSpecPriceReturnObjSubOrderPricesOrderItemPricesResponse':
        if not json_data:
            return None
        obj = CtelbQueryModifyPgelbSpecPriceReturnObjSubOrderPricesOrderItemPricesResponse(None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbQueryModifyPgelbSpecPriceReturnObjSubOrderPricesResponse:
    serviceTag: Optional[str]  # 服务类型
    totalPrice: Any  # 子订单总价格（单位：元）
    finalPrice: Any  # 最终价格（单位：元）
    orderItemPrices: Optional[List[Optional[CtelbQueryModifyPgelbSpecPriceReturnObjSubOrderPricesOrderItemPricesResponse]]]  # item价格信息


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbQueryModifyPgelbSpecPriceReturnObjSubOrderPricesResponse':
        if not json_data:
            return None
        obj = CtelbQueryModifyPgelbSpecPriceReturnObjSubOrderPricesResponse(None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbQueryModifyPgelbSpecPriceReturnObjResponse:
    """业务数据"""
    totalPrice: Any  # 总价格（单位：元）
    discountPrice: Any  # 折后价格（单位：元）
    finalPrice: Any  # 最终价格（单位：元）
    subOrderPrices: Optional[List[Optional[CtelbQueryModifyPgelbSpecPriceReturnObjSubOrderPricesResponse]]]  # 子订单价格信息


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbQueryModifyPgelbSpecPriceReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbQueryModifyPgelbSpecPriceReturnObjResponse(None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbQueryModifyPgelbSpecPriceResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtelbQueryModifyPgelbSpecPriceReturnObjResponse]  # 业务数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbQueryModifyPgelbSpecPriceResponse':
        if not json_data:
            return None
        obj = CtelbQueryModifyPgelbSpecPriceResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 保障型负载均衡变配询价
class CtelbQueryModifyPgelbSpecPriceApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbQueryModifyPgelbSpecPriceRequest) -> CtelbQueryModifyPgelbSpecPriceResponse:
        url = endpoint + "/v4/elb/query-modify-price"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict, credential=credential)
            return CtelbQueryModifyPgelbSpecPriceResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
