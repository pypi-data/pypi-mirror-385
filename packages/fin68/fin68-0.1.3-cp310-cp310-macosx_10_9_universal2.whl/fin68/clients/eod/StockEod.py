from __future__ import annotations

"""
fin68.clients.eod.stock
=======================

Cung cấp lớp `StockEod` — tập trung các endpoint EOD dành cho từng mã cổ phiếu riêng lẻ.  
Bao gồm dữ liệu OHLCV (Open, High, Low, Close, Volume), điều chỉnh giá (adjusted) và
hỗ trợ các khoảng thời gian khác nhau (ngày, tuần, tháng...).

Notes
-----
- Dữ liệu lấy từ `private_core.eod_core.fetch_ohlcv()`.
- Tất cả kết quả được trả về dưới dạng `pandas.DataFrame`.
- Tự động kiểm tra và chuẩn hóa ngày bắt đầu/kết thúc, validate interval.
"""

from typing import TYPE_CHECKING, Sequence, Union

from private_core import eod_core
from ..base import BaseClient
from .helper import DateStr, Interval, _EodMixin

if TYPE_CHECKING:
    from pandas import DataFrame
    from private_core.http_core import HttpSession

SymbolArg = Union[str, Sequence[str]]


class StockEod(BaseClient, _EodMixin):
    """
    Cung cấp các endpoint EOD cho từng mã cổ phiếu (equity symbol).

    Lớp này cho phép truy vấn dữ liệu giá, khối lượng và chỉ báo kỹ thuật
    ở cấp mã cổ phiếu, tương tự như chức năng `get_price_data()` trong các
    hệ thống tài chính chuyên nghiệp.

    Parameters
    ----------
    session : HttpSession
        Phiên HTTP đã xác thực, được truyền từ `EodClient`.

    Notes
    -----
    - Toàn bộ phương thức đều hỗ trợ truy vấn nhiều mã cùng lúc (`list[str]`).
    - Có thể chọn chế độ `adjusted=True` để lấy dữ liệu điều chỉnh cổ tức/chia tách.
    - Hàm `_EodMixin` cung cấp các helper cho việc chuẩn hóa khoảng thời gian
      (`_normalize_range`) và kiểm tra tính hợp lệ của `interval`.
    """

    def __init__(self, session: "HttpSession") -> None:
        """
        Khởi tạo lớp `StockEod` với session HTTP đã được xác thực.

        Parameters
        ----------
        session : HttpSession
            Phiên HTTP dùng chung từ `EodClient`.
        """
        super().__init__(session=session)

    def ohlcv(
        self,
        symbol: SymbolArg,
        start: DateStr = None,
        end: DateStr = None,
        adjusted: bool = True,
        interval: Interval = "1D",
    ) -> "DataFrame":
        """
        Lấy dữ liệu OHLCV (Open, High, Low, Close, Volume) cho một hoặc nhiều mã cổ phiếu.

        Parameters
        ----------
        symbol : str or Sequence[str]
            Mã cổ phiếu hoặc danh sách mã cổ phiếu cần lấy dữ liệu (VD: `"HPG"`, `["HPG", "VCB"]`).
        start : str, optional
            Ngày bắt đầu, định dạng `"YYYY-MM-DD"`.  
            Nếu không truyền, hệ thống sẽ tự động lấy ngược về theo khoảng mặc định.
        end : str, optional
            Ngày kết thúc, định dạng `"YYYY-MM-DD"`.  
            Nếu không truyền, mặc định là ngày hiện tại.
        adjusted : bool, default True
            Nếu `True`, trả về giá đã điều chỉnh theo cổ tức và chia tách cổ phiếu.
        interval : {"1D", "1W", "1M", "3M", "6M", "1Y"}, default "1D"
            Khoảng thời gian dữ liệu cần lấy:
            - `"1D"`: theo ngày  
            - `"1W"`: theo tuần  
            - `"1M"`: theo tháng  
            - `"3M"`, `"6M"`, `"1Y"`: theo quý, nửa năm, hoặc năm

        Returns
        -------
        DataFrame
            Bảng dữ liệu gồm các cột:
            - `symbol`: mã cổ phiếu  
            - `Date`: ngày giao dịch  
            - `Open`, `High`, `Low`, `Close`, `Volume`  
            - Các cột bổ sung nếu backend cung cấp (ví dụ: `Adj Close`)

        Raises
        ------
        ValueError
            Khi tham số `start` > `end`, hoặc `interval` không hợp lệ.
        ApiRequestError
            Khi backend trả lỗi trong quá trình gọi API.

        Examples
        --------
        >>> from fin68 import client
        >>> cli = client(api_key="sk_live_...")
        >>> df = cli.eod.stock.ohlcv("HPG", start="2024-01-01", end="2024-06-30")
        >>> df.head()
             symbol        Date    Open    High     Low   Close    Volume
        0      HPG  2024-01-02  27200  27500  26900  27400  15300000

        Notes
        -----
        - Tự động validate khoảng thời gian (`start <= end`).
        - Có thể truy vấn nhiều mã cùng lúc để so sánh hiệu suất.
        - Hàm này là wrapper của `private_core.eod_core.fetch_ohlcv`.
        """
        start_date, end_date = self._normalize_range(start, end)
        interval_value = self._validate_interval(interval)
        payload = eod_core.fetch_ohlcv(
            self.session,
            symbol,
            start=start_date,
            end=end_date,
            adjusted=adjusted,
            interval=interval_value,
        )
        return self._to_dataframe(payload)
