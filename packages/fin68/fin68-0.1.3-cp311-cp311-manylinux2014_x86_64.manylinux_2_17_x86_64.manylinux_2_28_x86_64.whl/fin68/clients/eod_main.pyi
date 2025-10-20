# fin68/clients/<your_module_name>.pyi
from typing import TYPE_CHECKING
from .base import BaseClient
from .eod import MarketEod, SectorEod, StockEod

if TYPE_CHECKING:
    from private_core.http_core import HttpSession

__all__: list[str]

class EodClient(BaseClient):
    """
    Facade EOD: gom các namespace `stock`, `market`, `sector`.
    """

    stock: StockEod 
    """
    Namespace dữ liệu EOD cho **cổ phiếu (Stock-level)**.

    Cung cấp các endpoint chuyên biệt để truy xuất dữ liệu End-of-Day (EOD)
    cho từng mã cổ phiếu riêng lẻ — phù hợp cho các tác vụ như:
    - Phân tích giá lịch sử (OHLCV)
    - Tính toán chỉ báo kỹ thuật (MA, RSI, MACD, Bollinger, v.v.)
    - So sánh hiệu suất cổ phiếu giữa các mã

    Methods chính
    --------------
    - `ohlcv(symbol, start=None, end=None, interval="1D")`
        → Lấy dữ liệu OHLCV (Open, High, Low, Close, Volume) theo ngày, tuần, tháng…

    Parameters
    ----------
    symbol : str or list[str]
        Mã cổ phiếu hoặc danh sách mã (VD: `"HPG"`, `["HPG", "VCB"]`)

    Examples
    --------
    >>> cli.eod.stock.ohlcv("HPG", start="2024-01-01", end="2024-06-30")
    >>> cli.eod.stock.ohlcv(["HPG", "VCB", "FPT"], interval="1W")
    """

    market: MarketEod
    """
    Namespace dữ liệu EOD cho **chỉ số thị trường (Market-level)**.

    Cung cấp dữ liệu tổng hợp cho các chỉ số thị trường phổ biến như:
    - VNINDEX (sàn HOSE)
    - VN30 (rổ 30 cổ phiếu vốn hóa lớn)
    - HNX, HNX30 (sàn Hà Nội)
    - UPCOM (thị trường UPCOM)

    Dữ liệu này giúp phân tích xu hướng toàn thị trường, đo lường biến động,
    và so sánh hiệu suất giữa các sàn.

    Methods chính
    --------------
    - `ohlcv(symbol, start=None, end=None, interval="1D")`
        → Lấy dữ liệu OHLCV của các chỉ số (VNINDEX, VN30, HNX, …)

    Parameters
    ----------
    symbol : {"VNINDEX", "VN30", "HNX", "HNX30", "UPCOM"} or list
        Tên chỉ số hoặc danh sách chỉ số.

    Examples
    --------
    >>> cli.eod.market.ohlcv("VNINDEX", start="2024-01-01", end="2024-06-30")
    >>> cli.eod.market.ohlcv(["VNINDEX", "VN30", "HNX"])
    """

    sector: SectorEod
    """
    Namespace dữ liệu EOD cho **ngành và nhóm ngành (Sector-level)**.

    Cung cấp dữ liệu tổng hợp theo mã ICB (Industry Classification Benchmark),
    phản ánh biến động và hiệu suất trung bình của từng ngành hoặc tiểu ngành.
    Thường dùng trong phân tích xoay vòng ngành (sector rotation) hoặc theo dõi
    xu hướng dòng tiền giữa các nhóm cổ phiếu.

    Methods chính
    --------------
    - `ohlcv(icb_code, start=None, end=None, interval="1D")`
        → Lấy dữ liệu OHLCV trung bình theo ngành hoặc nhóm ngành.

    Parameters
    ----------
    icb_code : str or list[str]
        Mã ngành theo chuẩn ICB (VD: `"ICB01010"`, `"ICB03020"`).

    Examples
    --------
    >>> cli.eod.sector.ohlcv("ICB01010", start="2024-01-01", end="2024-06-30")
    >>> cli.eod.sector.ohlcv(["ICB01010", "ICB03020"], interval="1W")

    Notes
    -----
    - Dữ liệu ngành được tính theo trọng số vốn hóa.
    - Thường dùng để xác định nhóm ngành dẫn dắt thị trường.
    """


    def __init__(self, session: "HttpSession") -> None: ...
