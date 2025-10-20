from __future__ import annotations

"""
fin68.clients.eod.sector
========================

Cung cấp lớp `SectorEod` — các endpoint EOD (End-of-Day) cho dữ liệu ngành (ICB Sector Aggregates).

Dữ liệu thể hiện hiệu suất, biến động, và khối lượng giao dịch trung bình của từng ngành
(ICB Code) hoặc nhóm ngành (Sub-sector). Phù hợp cho phân tích xoay vòng ngành (sector rotation)
và đánh giá xu hướng thị trường theo nhóm.

Notes
-----
- Dữ liệu được lấy qua `private_core.eod_core.fetch_ohlcv()`.
- Tất cả kết quả trả về dạng `pandas.DataFrame`.
- Cho phép truy vấn nhiều mã ngành cùng lúc.
"""

from typing import TYPE_CHECKING, Sequence, Union
from private_core import eod_core
from ..base import BaseClient
from .helper import DateStr, Interval, _EodMixin
from .icb_types import SectorArg,icbMap
if TYPE_CHECKING:
    from pandas import DataFrame
    from private_core.http_core import HttpSession




class SectorEod(BaseClient, _EodMixin):
    """
    Cung cấp các endpoint EOD cho nhóm ngành (ICB Sector/Industry).

    Lớp này giúp truy vấn dữ liệu tổng hợp cho từng ngành (ICB Code) theo ngày, tuần, tháng, v.v.

    Parameters
    ----------
    session : HttpSession
        Phiên HTTP đã xác thực, được truyền từ `EodClient`.

    Notes
    -----
    - Cho phép lấy dữ liệu nhiều mã ngành cùng lúc (list[str]).
    - Hỗ trợ chuẩn hóa khoảng thời gian và kiểm tra `interval`.
    - Trả về OHLCV (Open, High, Low, Close, Volume) trung bình của từng ngành.
    - Các mã ngành tuân theo chuẩn phân loại ICB (ví dụ: `ICB01010`, `ICB03020`...).
    """

    def __init__(self, session: "HttpSession") -> None:
        """
        Khởi tạo `SectorEod` với session HTTP đã xác thực.

        Parameters
        ----------
        session : HttpSession
            Phiên HTTP dùng chung từ `EodClient`.
        """
        super().__init__(session=session)

    def ohlcv(
        self,
        symbol: SectorArg,
        start: DateStr = None,
        end: DateStr = None,
        interval: Interval = "1D",
    ) -> "DataFrame":
        """
        Lấy dữ liệu OHLCV (Open, High, Low, Close, Volume) cho một hoặc nhiều ngành ICB.

        Parameters
        ----------
        symbol : str or Sequence[str]
            Mã ngành hoặc danh sách mã ngành (ví dụ: `"ICB01010"`, `["ICB01010", "ICB03020"]`).
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
            Bảng dữ liệu OHLCV cho từng mã ngành, gồm:
            - `icbCode`: mã ngành  
            - `Date`: ngày giao dịch  
            - `Open`, `High`, `Low`, `Close`, `Volume`  
            - Có thể có thêm `MarketCap`, `TurnoverRatio` nếu backend hỗ trợ.

        Raises
        ------
        ValueError
            Nếu ngày bắt đầu > ngày kết thúc hoặc `interval` không hợp lệ.
        ApiRequestError
            Nếu backend trả lỗi khi gọi API.

        Examples
        --------
        >>> from fin68 import client
        >>> cli = client(api_key="sk_live_...")
        >>> df = cli.eod.sector.ohlcv("ICB01010", start="2024-01-01", end="2024-06-30")
        >>> df.head()
            icbCode        Date     Open     High      Low    Close   Volume
        0   ICB01010  2024-01-02  1320.25  1334.11  1305.21  1310.55  9.32e6

        >>> # Lấy đồng thời nhiều ngành
        >>> cli.eod.sector.ohlcv(["ICB01010", "ICB03020"])

        Notes
        -----
        - Phù hợp để phân tích hiệu suất ngành theo thời gian.
        - Dữ liệu thường được tổng hợp từ trung bình trọng số theo vốn hóa.
        - Wrapper của `private_core.eod_core.fetch_ohlcv`.
        """
        icb_codes=[]
        if isinstance(symbol, list):
            for sec in symbol:
                if sec.lower() not in icbMap:
                    raise ValueError(f"Không tìm thấy mã ngành cho tên '{sec}'")
                icb_codes.append(icbMap.get(sec.lower()))
        else:
            if symbol.lower() not in icbMap:
                raise ValueError(f"Không tìm thấy mã ngành cho tên '{symbol}'")
            icb_codes.append(icbMap.get(symbol.lower()))


        if not symbol:
            raise ValueError(f"Không tìm thấy mã ngành cho tên '{symbol}'")
        start_date, end_date = self._normalize_range(start, end)
        interval_value = self._validate_interval(interval)
        payload = eod_core.fetch_ohlcv(
            self.session,
            icb_codes,
            start=start_date,
            end=end_date,
            interval=interval_value,
        )
        return self._to_dataframe(payload)
