from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbShowCertificateRequest:
    regionID: str  # 资源池ID
    iD: Optional[str]  # 证书ID, 该字段后续废弃
    certificateID: Optional[str]  # 证书ID, 推荐使用该字段, 当同时使用 ID 和 certificateID 时，优先使用 certificateID


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowCertificateRequest':
        if not json_data:
            return None
        obj = CtelbShowCertificateRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbShowCertificateReturnObjResponse:
    """接口业务数据"""
    regionID: Optional[str]  # 资源池ID
    azName: Optional[str]  # 可用区名称
    projectID: Optional[str]  # 项目ID
    iD: Optional[str]  # 证书ID
    name: Optional[str]  # 名称
    description: Optional[str]  # 描述
    type: Optional[str]  # 证书类型: certificate / ca
    privateKey: Optional[str]  # 服务器证书私钥
    certificate: Optional[str]  # type为Server该字段表示服务器证书公钥Pem内容;type为Ca该字段表示Ca证书Pem内容
    status: Optional[str]  # 状态: ACTIVE / INACTIVE
    createdTime: Optional[str]  # 创建时间，为UTC格式
    updatedTime: Optional[str]  # 更新时间，为UTC格式


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowCertificateReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbShowCertificateReturnObjResponse(None,None,None,None,None,None,None,None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbShowCertificateResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtelbShowCertificateReturnObjResponse]  # 接口业务数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbShowCertificateResponse':
        if not json_data:
            return None
        obj = CtelbShowCertificateResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 查看证书详情
class CtelbShowCertificateApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbShowCertificateRequest) -> CtelbShowCertificateResponse:
        url = endpoint + "/v4/elb/show-certificate"
        params = {'regionID':request.regionID, 'iD':request.iD, 'certificateID':request.certificateID}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtelbShowCertificateResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
