from typing import List, Optional, Dict, Any
from ctyunsdk_bandwidth20220909.core.client import CtyunClient
from ctyunsdk_bandwidth20220909.core.credential import Credential
from ctyunsdk_bandwidth20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcBandwidthQueryModifyPriceRequest:
    clientToken: str  # 客户端存根，用于保证订单幂等性, 长度 1 - 64
    regionID: str  # 共享带宽的区域 id。
    bandwidthID: str  # 共享带宽 id。
    bandwidth: Any  # 共享带宽的带宽峰值。


@dataclass_json
@dataclass
class CtvpcBandwidthQueryModifyPriceReturnObjSubOrderPricesOrderItemPricesResponse:
    resourceType: Optional[str] = None  # 资源类型
    totalPrice: Optional[Any] = None  # 总价格（单位：元）
    finalPrice: Optional[Any] = None  # 最终价格（单位：元）


@dataclass_json
@dataclass
class CtvpcBandwidthQueryModifyPriceReturnObjSubOrderPricesResponse:
    serviceTag: Optional[str] = None  # 服务类型
    totalPrice: Optional[Any] = None  # 子订单总价格（单位：元）
    finalPrice: Optional[Any] = None  # 最终价格（单位：元）
    orderItemPrices: Optional[
        List[Optional[CtvpcBandwidthQueryModifyPriceReturnObjSubOrderPricesOrderItemPricesResponse]]] = None  # item价格信息


@dataclass_json
@dataclass
class CtvpcBandwidthQueryModifyPriceReturnObjResponse:
    """业务数据"""
    totalPrice: Optional[Any] = None  # 总价格（单位：元）
    discountPrice: Optional[Any] = None  # 折后价格（单位：元）
    finalPrice: Optional[Any] = None  # 最终价格（单位：元）
    subOrderPrices: Optional[
        List[Optional[CtvpcBandwidthQueryModifyPriceReturnObjSubOrderPricesResponse]]] = None  # 子订单价格信息


@dataclass_json
@dataclass
class CtvpcBandwidthQueryModifyPriceResponse:
    statusCode: Any  # 返回状态码（800为成功，900为失败）
    message: Optional[str] = None  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str] = None  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str] = None  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcBandwidthQueryModifyPriceReturnObjResponse] = None  # 业务数据

    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @staticmethod
    def from_json(json_data: dict) -> 'CtvpcBandwidthQueryModifyPriceResponse':
        if not json_data:
            return None
        obj = CtvpcBandwidthQueryModifyPriceResponse(None, None, None, None, None)
        for key, value in json_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


# 变配询价。
class CtvpcBandwidthQueryModifyPriceApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)

    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint

    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str,
           request: CtvpcBandwidthQueryModifyPriceRequest) -> CtvpcBandwidthQueryModifyPriceResponse:
        url = endpoint + "/v4/bandwidth/query-modify-price"
        params = {}
        try:
            header_params = {}
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.post(url=url, params=params, header_params=header_params, data=request_dict,
                                   credential=credential)
            return CtvpcBandwidthQueryModifyPriceResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
