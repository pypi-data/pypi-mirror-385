from __future__ import annotations

"""
fin68.clients.eod.sector (stub)
==============================

Type stub cho lớp `SectorEod` — phục vụ autocomplete/typing trong IDE và
static type checker. Không thực thi logic, chỉ khai báo kiểu & docstring ngắn.
"""

from typing import TYPE_CHECKING, Sequence, Union
from ..base import BaseClient
from .helper import DateStr, Interval,IcbName, _EodMixin
from .icb_types import SectorArg
if TYPE_CHECKING:
    from pandas import DataFrame
    from private_core.http_core import HttpSession



class SectorEod(BaseClient, _EodMixin):
    """
    Endpoint EOD cho dữ liệu ngành (ICB Sector Aggregates).

    Parameters
    ----------
    session : HttpSession
        Phiên HTTP đã xác thực, truyền từ `EodClient`.

    Notes
    -----
    - Hỗ trợ nhiều mã ngành cùng lúc (list[str]).
    - Chuẩn hóa khoảng thời gian, validate `interval`.
    - Trả về OHLCV trung bình/tổng hợp cho từng ngành.
    """

    def __init__(self, session: "HttpSession") -> None: ...
    """
    Khởi tạo `SectorEod` với session HTTP đã xác thực.

    Parameters
    ----------
    session : HttpSession
        Phiên HTTP dùng chung từ `EodClient`.
    """

    def ohlcv(
        self,
        symbol: SectorArg,
        start: DateStr = None,
        end: DateStr = None,
        interval: Interval = "1D",
    ) -> "DataFrame": ...
    """
    Lấy dữ liệu OHLCV (Open, High, Low, Close, Volume) cho một hoặc nhiều ngành ICB.

    Parameters
    ----------
    symbol : str or Sequence[str]
        Mã ngành hoặc danh sách mã ngành (VD: "ICB01010", ["ICB01010", "ICB03020"]).
    start : str, optional
        Ngày bắt đầu "YYYY-MM-DD". Nếu None, dùng mặc định hệ thống.
    end : str, optional
        Ngày kết thúc "YYYY-MM-DD". Nếu None, mặc định là hôm nay.
    interval : {"1D", "1W", "1M", "3M", "6M", "1Y"}, default "1D"
        Khoảng thời gian lấy dữ liệu.

    Returns
    -------
    DataFrame
        Gồm các cột cơ bản: `icbCode`, `Date`, `Open`, `High`, `Low`, `Close`, `Volume`.

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
    >>> cli.eod.sector.ohlcv("ICB01010", start="2024-01-01", end="2024-06-30")
    >>> cli.eod.sector.ohlcv(["ICB01010", "ICB03020"])
    """
