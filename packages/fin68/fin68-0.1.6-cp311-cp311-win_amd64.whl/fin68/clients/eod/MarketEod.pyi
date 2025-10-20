from __future__ import annotations

"""
fin68.clients.eod.market (stub)
===============================

Type stub cho lớp `MarketEod` — phục vụ autocomplete/typing trong IDE và
static type checker. Không thực thi logic, chỉ khai báo kiểu.

Ghi chú
-------
- Docstring giữ phong cách NumPy, giúp IDE hiển thị tooltip rõ ràng.
- Thân hàm dùng `...` theo chuẩn stub.
"""

from typing import TYPE_CHECKING, Sequence, Union, Literal
from ..base import BaseClient
from .helper import DateStr, Interval, _EodMixin

if TYPE_CHECKING:
    from pandas import DataFrame
    from private_core.http_core import HttpSession

IndexArg = Union[
    Literal["VNINDEX", "VN30", "HNX", "HNX30", "UPCOM"],
    Sequence[Literal["VNINDEX", "VN30", "HNX", "HNX30", "UPCOM"]],
]


class MarketEod(BaseClient, _EodMixin):
    """
    Endpoint EOD cho các chỉ số thị trường (VNINDEX, VN30, HNX, HNX30, UPCOM).

    Parameters
    ----------
    session : HttpSession
        Phiên HTTP đã xác thực, được truyền từ `EodClient`.

    Notes
    -----
    - Hỗ trợ truy vấn nhiều chỉ số cùng lúc (list).
    - Tự động chuẩn hóa khoảng thời gian và validate `interval`.
    - Trả về dữ liệu OHLCV (Open, High, Low, Close, Volume) của chỉ số.
    """

    def __init__(self, session: "HttpSession") -> None: ...
    """
    Khởi tạo `MarketEod` với session HTTP đã xác thực.

    Parameters
    ----------
    session : HttpSession
        Phiên HTTP chia sẻ từ `EodClient`.
    """

    def ohlcv(
        self,
        symbol: IndexArg,
        start: DateStr = None,
        end: DateStr = None,
        interval: Interval = "1D",
    ) -> "DataFrame": ...
    """
    Lấy dữ liệu OHLCV cho một hoặc nhiều chỉ số thị trường.

    Parameters
    ----------
    symbol : {"VNINDEX", "VN30", "HNX", "HNX30", "UPCOM"} or Sequence
        Chỉ số hoặc danh sách chỉ số cần lấy dữ liệu.
    start : str, optional
        Ngày bắt đầu, định dạng "YYYY-MM-DD". Nếu `None`, dùng mặc định hệ thống.
    end : str, optional
        Ngày kết thúc, định dạng "YYYY-MM-DD". Nếu `None`, mặc định là hôm nay.
    interval : {"1D", "1W", "1M", "3M", "6M", "1Y"}, default "1D"
        Khoảng thời gian lấy dữ liệu.

    Returns
    -------
    DataFrame
        Bảng dữ liệu gồm: `symbol`, `Date`, `Open`, `High`, `Low`, `Close`, `Volume`.

    Raises
    ------
    ValueError
        Nếu `start > end` hoặc `interval` không hợp lệ.
    ApiRequestError
        Nếu backend trả lỗi khi gọi API.

    Examples
    --------
    >>> from fin68 import client
    >>> cli = client(api_key="sk_live_...")
    >>> cli.eod.market.ohlcv("VNINDEX", start="2024-01-01", end="2024-06-30")
    >>> cli.eod.market.ohlcv(["VNINDEX", "VN30", "HNX"])
    """
