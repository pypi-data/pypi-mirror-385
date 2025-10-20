from __future__ import annotations

"""
fin68.clients.eod.market
========================

Cung cấp lớp `MarketEod` — tập hợp các endpoint EOD (End-of-Day)
dành cho **chỉ số thị trường** như VNINDEX, VN30, HNX, HNX30 và UPCOM.

Notes
-----
- Dữ liệu được lấy từ `private_core.eod_core.fetch_ohlcv()`.
- Tất cả kết quả được trả về dưới dạng `pandas.DataFrame`.
- Có thể truy vấn nhiều chỉ số cùng lúc.

"""

from typing import TYPE_CHECKING, Sequence, Union, Literal
from private_core import eod_core
from ..base import BaseClient
from .helper import DateStr, Interval, _EodMixin

if TYPE_CHECKING:
    from pandas import DataFrame
    from private_core.http_core import HttpSession

IndexArg = Union[
    Literal["VNINDEX", "VN30", "HNX", "HNX30", "UPCOM"],
    Sequence[Literal["VNINDEX", "VN30", "HNX", "HNX30", "UPCOM"]],
]
INDEXS = {"VNINDEX", "VN30", "HNX", "HNX30", "UPCOM"}

class MarketEod(BaseClient, _EodMixin):
    """
    Cung cấp các endpoint EOD cho các chỉ số thị trường (Market Indices).

    Bao gồm các chỉ số phổ biến:
    - **VNINDEX**: chỉ số toàn thị trường HOSE  
    - **VN30**: nhóm 30 cổ phiếu vốn hóa lớn trên HOSE  
    - **HNX**, **HNX30**: chỉ số sàn Hà Nội  
    - **UPCOM**: thị trường UPCOM

    Parameters
    ----------
    session : HttpSession
        Phiên HTTP đã xác thực, được truyền từ `EodClient`.

    Notes
    -----
    - Hỗ trợ nhiều chỉ số trong cùng một lệnh truy vấn (`list[str]`).
    - Tự động kiểm tra tính hợp lệ của khoảng thời gian (`start <= end`).
    - Có thể lấy dữ liệu theo nhiều `interval` (ngày, tuần, tháng, v.v.).
    - Trả về dữ liệu OHLCV (Open, High, Low, Close, Volume) của chỉ số.
    """

    def __init__(self, session: "HttpSession") -> None:
        """
        Khởi tạo `MarketEod` với session HTTP đã xác thực.

        Parameters
        ----------
        session : HttpSession
            Phiên HTTP được chia sẻ từ `EodClient`.
        """
        super().__init__(session=session)

    def ohlcv(
        self,
        symbol: IndexArg,
        start: DateStr = None,
        end: DateStr = None,
        interval: Interval = "1D",
    ) -> "DataFrame":
        """
        Lấy dữ liệu OHLCV (Open, High, Low, Close, Volume) cho một hoặc nhiều chỉ số thị trường.

        Parameters
        ----------
        symbol : {"VNINDEX", "VN30", "HNX", "HNX30", "UPCOM"} or Sequence
            Chỉ số hoặc danh sách chỉ số cần lấy dữ liệu.
        start : str, optional
            Ngày bắt đầu, định dạng `"YYYY-MM-DD"`.  
            Nếu không truyền, hệ thống sẽ chọn mặc định (thường là 1 năm gần nhất).
        end : str, optional
            Ngày kết thúc, định dạng `"YYYY-MM-DD"`.  
            Nếu không truyền, mặc định là ngày hiện tại.
        interval : {"1D", "1W", "1M", "3M", "6M", "1Y"}, default "1D"
            Khoảng thời gian dữ liệu:
            - `"1D"`: theo ngày  
            - `"1W"`: theo tuần  
            - `"1M"`: theo tháng  
            - `"3M"`, `"6M"`, `"1Y"`: theo quý, nửa năm hoặc năm

        Returns
        -------
        DataFrame
            Bảng dữ liệu OHLCV, gồm các cột:
            - `symbol`: tên chỉ số  
            - `Date`: ngày giao dịch  
            - `Open`, `High`, `Low`, `Close`, `Volume`

        Raises
        ------
        ValueError
            Nếu ngày bắt đầu > ngày kết thúc hoặc interval không hợp lệ.
        ApiRequestError
            Nếu backend trả lỗi trong quá trình gọi API.

        Examples
        --------
        >>> from fin68 import client
        >>> cli = client(api_key="sk_live_...")
        >>> df = cli.eod.market.ohlcv("VNINDEX", start="2024-01-01", end="2024-06-30")
        >>> df.head()
            symbol        Date    Open    High     Low   Close   Volume
        0  VNINDEX  2024-01-02  1120.0  1125.6  1110.2  1119.4  612000000

        >>> # Lấy đồng thời nhiều chỉ số
        >>> cli.eod.market.ohlcv(["VNINDEX", "VN30", "HNX"])

        Notes
        -----
        - Có thể dùng để so sánh biến động giữa các chỉ số thị trường.
        - Hàm này là wrapper của `private_core.eod_core.fetch_ohlcv`.
        """
        if not isinstance(symbol, list):
            if symbol.upper() not in INDEXS:
                raise ValueError(f"Chỉ số '{symbol}' không hợp lệ. Vui lòng chọn trong {INDEXS}")
        else:
            for idx in symbol:
                if idx.upper() not in INDEXS:
                    raise ValueError(f"Chỉ số '{idx}' không hợp lệ. Vui lòng chọn trong {INDEXS}")
        start_date, end_date = self._normalize_range(start, end)
        interval_value = self._validate_interval(interval)
        payload = eod_core.fetch_ohlcv(
            self.session,
            symbol,
            start=start_date,
            end=end_date,
            interval=interval_value,
        )
        return self._to_dataframe(payload)
