from typing import List, Optional, Dict, Any
from ctyunsdk_elb20220909.core.client import CtyunClient
from ctyunsdk_elb20220909.core.credential import Credential
from ctyunsdk_elb20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class CtelbListCertificateRequest:
    regionID: str  # 资源池ID
    iDs: Optional[str]  # 证书ID列表，以,分隔
    name: Optional[str]  # 证书名称，以,分隔，必须与ID顺序严格对应
    type: Optional[str]  # 证书类型。Ca或Server，以,分隔，必须与ID和name的顺序严格对应


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListCertificateRequest':
        if not json_data:
            return None
        obj = CtelbListCertificateRequest()
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


@dataclass
class CtelbListCertificateReturnObjResponse:
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
    def from_json(json_data: dict) -> 'CtelbListCertificateReturnObjResponse':
        if not json_data:
            return None
        obj = CtelbListCertificateReturnObjResponse(None,None,None,None,None,None,None,None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

@dataclass
class CtelbListCertificateResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str]  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str]  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[List[Optional[CtelbListCertificateReturnObjResponse]]]  # 接口业务数据


    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtelbListCertificateResponse':
        if not json_data:
            return None
        obj = CtelbListCertificateResponse(None,None,None,None,None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 获取证书列表
class CtelbListCertificateApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)
    
    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint
    
    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str, request: CtelbListCertificateRequest) -> CtelbListCertificateResponse:
        url = endpoint + "/v4/elb/list-certificate"
        params = {'regionID':request.regionID, 'iDs':request.iDs, 'name':request.name, 'type':request.type}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtelbListCertificateResponse.from_json(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
