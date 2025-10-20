from __future__ import annotations

"""
fin68.clients.eod.stock (stub)
==============================

Type stub cho lớp `StockEod` — phục vụ autocomplete/typing trong IDE (VSCode/PyCharm)
và static type checker (mypy/pyright). Không thực thi logic.

Ghi chú
-------
- Docstring giữ chuẩn NumPy style như bản .py.
- Các thân hàm được thay bằng `...` (ellipsis) theo PEP 484.
"""

from typing import TYPE_CHECKING, Sequence, Union
from ..base import BaseClient
from .helper import DateStr, Interval, _EodMixin

if TYPE_CHECKING:
    from pandas import DataFrame
    from private_core.http_core import HttpSession

SymbolArg = Union[str, Sequence[str]]

class StockEod(BaseClient, _EodMixin):
    """
    Cung cấp các endpoint EOD cho từng mã cổ phiếu (equity symbol).

    Parameters
    ----------
    session : HttpSession
        Phiên HTTP đã xác thực, được truyền từ `EodClient`.

    Notes
    -----
    - Hỗ trợ truy vấn nhiều mã cùng lúc (`list[str]`).
    - Có `adjusted=True` để lấy giá đã điều chỉnh cổ tức/chia tách.
    - Kế thừa `_EodMixin` để chuẩn hóa khoảng thời gian và validate interval.
    """

    def __init__(self, session: "HttpSession") -> None: ...
    """
    Khởi tạo `StockEod` với session đã xác thực.

    Parameters
    ----------
    session : HttpSession
        Phiên HTTP dùng chung từ `EodClient`.
    """

    def ohlcv(
        self,
        symbol: SymbolArg,
        start: DateStr = None,
        end: DateStr = None,
        interval: Interval = "1D",
    ) -> "DataFrame": ...
    """
    Lấy dữ liệu OHLCV (Open, High, Low, Close, Volume) cho một hoặc nhiều mã cổ phiếu.

    Parameters
    ----------
    symbol : str or Sequence[str]
        Mã cổ phiếu hoặc danh sách mã (VD: "HPG", ["HPG", "VCB"]).
    start : str, optional
        Ngày bắt đầu, định dạng "YYYY-MM-DD". Nếu `None`, dùng mặc định hệ thống.
    end : str, optional
        Ngày kết thúc, định dạng "YYYY-MM-DD". Nếu `None`, mặc định là hôm nay.
    interval : {"1D", "1W", "1M", "3M", "6M", "1Y"}, default "1D"
        Khoảng thời gian lấy dữ liệu.

    Returns
    -------
    DataFrame
        Gồm các cột cơ bản: `symbol`, `Date`, `Open`, `High`, `Low`, `Close`, `Volume`.


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
    >>> df = cli.eod.stock.ohlcv("HPG", start="2024-01-01", end="2024-06-30")
    >>> df.head()
    """
