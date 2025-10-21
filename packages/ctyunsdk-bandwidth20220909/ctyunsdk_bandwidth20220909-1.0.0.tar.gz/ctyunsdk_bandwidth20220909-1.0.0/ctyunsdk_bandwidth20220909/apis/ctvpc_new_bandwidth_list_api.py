from typing import List, Optional, Dict, Any
from ctyunsdk_bandwidth20220909.core.client import CtyunClient
from ctyunsdk_bandwidth20220909.core.credential import Credential
from ctyunsdk_bandwidth20220909.core.exception import CtyunRequestException

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, List, Dict, Any


@dataclass_json
@dataclass
class CtvpcNewBandwidthListRequest:
    regionID: str  # 共享带宽所在的区域id。
    queryContent: Optional[str] = None  # 【模糊查询】 共享带宽实例名称 / 带宽 ID
    projectID: Optional[str] = None  # 企业项目 ID，默认为'0'
    pageNumber: Optional[Any] = None  # 列表的页码，默认值为 1。
    pageNo: Optional[Any] = None  # 列表的页码，默认值为 1, 推荐使用该字段, pageNumber 后续会废弃
    pageSize: Optional[Any] = None  # 分页查询时每页的行数，最大值为 50，默认值为 10。


@dataclass_json
@dataclass
class CtvpcNewBandwidthListReturnObjBandwidthsEipsResponse:
    ip: Optional[str] = None  # 弹性 IP 的 IP
    eipID: Optional[str] = None  # 弹性 IP 的 ID


@dataclass_json
@dataclass
class CtvpcNewBandwidthListReturnObjBandwidthsResponse:
    id: Optional[str] = None  # 共享带宽id。
    status: Optional[str] = None  # 共享带宽状态: ACTIVE / EXPIRED / FREEZING
    bandwidth: Optional[Any] = None  # 共享带宽的带宽峰值， 单位：Mbps。
    name: Optional[str] = None  # 共享带宽名称。
    createdAt: Optional[str] = None  # 创建时间
    expireAt: Optional[str] = None  # 过期时间
    lineType: Optional[str] = None  # 线路类型
    enableSecondLevelMonitor: Optional[bool] = None  # 是否开启秒级监控
    eips: Optional[List[Optional[CtvpcNewBandwidthListReturnObjBandwidthsEipsResponse]]] = None  # 绑定的弹性 IP 列表


@dataclass_json
@dataclass
class CtvpcNewBandwidthListReturnObjResponse:
    """返回查询的共享带宽实例的详细信息。"""
    totalCount: Optional[Any] = None  # 列表条目数。
    currentCount: Optional[Any] = None  # 分页查询时每页的行数。
    totalPage: Optional[Any] = None  # 分页查询时总页数。
    bandwidths: Optional[List[Optional[CtvpcNewBandwidthListReturnObjBandwidthsResponse]]] = None  # 共享带宽列表


@dataclass_json
@dataclass
class CtvpcNewBandwidthListResponse:
    statusCode: Optional[Any] = None  # 返回状态码（800为成功，900为失败）
    message: Optional[str] = None  # statusCode为900时的错误信息; statusCode为800时为success, 英文
    description: Optional[str] = None  # statusCode为900时的错误信息; statusCode为800时为成功, 中文
    errorCode: Optional[str] = None  # statusCode为900时为业务细分错误码，三段式：product.module.code; statusCode为800时为SUCCESS
    returnObj: Optional[CtvpcNewBandwidthListReturnObjResponse] = None  # 返回查询的共享带宽实例的详细信息。


# 调用此接口可查询指定区域下共享带宽实例列表。
class CtvpcNewBandwidthListApi:
    def __init__(self, ak: str = None, sk: str = None):
        self.endpoint = None
        self.credential = Credential(ak, sk)

    def set_endpoint(self, endpoint: str) -> None:
        self.endpoint = endpoint

    @staticmethod
    def do(credential: Credential, client: CtyunClient, endpoint: str,
           request: CtvpcNewBandwidthListRequest) -> CtvpcNewBandwidthListResponse:
        url = endpoint + "/v4/bandwidth/new-list"
        params = {'regionID': request.regionID, 'queryContent': request.queryContent, 'projectID': request.projectID,
                  'pageNumber': request.pageNumber, 'pageNo': request.pageNo, 'pageSize': request.pageSize}
        try:
            request_dict = request.to_dict() if hasattr(request, 'to_dict') else request
            request_dict = {key: value for key, value in request_dict.items() if value is not None}
            response = client.get(url=url, params=params, header_params=request_dict, credential=credential)
            return CtvpcNewBandwidthListResponse.from_dict(response.json())
        except Exception as e:
            raise CtyunRequestException(str(e))
