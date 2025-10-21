from typing import List, Optional, Dict, Any
from ctyunsdk_bandwidth20220909.core.client import CtyunClient
from ctyunsdk_bandwidth20220909.core.credential import Credential
from ctyunsdk_bandwidth20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcShowBandwidthRequest:
    regionID: str  # 共享带宽所在的区域id
    bandwidthID: str  # 查询的共享带宽id。


@dataclass_json
@dataclass
class CtvpcShowBandwidthReturnObjEipsResponse:
    ip: Optional[str] = None  # 弹性 IP 的 IP
    eipID: Optional[str] = None  # 弹性 IP 的 ID


@dataclass_json
@dataclass
class CtvpcShowBandwidthReturnObjResponse:
    """返回查询的共享带宽详细信息。"""
    id: Optional[str] = None  # 共享带宽id。
    status: Optional[str] = None  # ACTIVE
    bandwidth: Optional[Any] = None  # 共享带宽的带宽峰值， 单位：Mbps。
    name: Optional[str] = None  # 共享带宽名称。
    expireAt: Optional[str] = None  # 过期时间
    createdAt: Optional[str] = None  # 创建时间
    lineType: Optional[str] = None  # 线路类型
    eips: Optional[List[Optional[CtvpcShowBandwidthReturnObjEipsResponse]]] = None  # 绑定的弹性 IP 列表，见下表


@dataclass_json
@dataclass
class CtvpcShowBandwidthResponse:
    statusCode: Optional[Any] = None  # 返回状态码（800为成功，900为失败）
    message: Optional[str] = None  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str] = None  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str] = None  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcShowBandwidthReturnObjResponse] = None  # 返回查询的共享带宽详细信息。


# 调用此接口可查询共享带宽实例详情。
class CtvpcShowBandwidthApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)

    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint

    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str,
           request: CtvpcShowBandwidthRequest) -> CtvpcShowBandwidthResponse:
        url = endpoint + "/v4/bandwidth/describe"
        params = {'regionID': request.regionID, 'bandwidthID': request.bandwidthID}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtvpcShowBandwidthResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
