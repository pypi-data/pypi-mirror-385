from typing import Optional, List, Dict
from .clients import EodClient
from .types import ApiKeyMeta, BackendMessage

__version__: str

class Fin68Client:
    """
    Client chính của thư viện Fin68 — chịu trách nhiệm xác thực API key,
    khởi tạo phiên làm việc HTTP, và cung cấp các domain client như `eod`.
    """

    eod: EodClient
    """
    Domain client cho dữ liệu EOD (End-of-Day).

    Cung cấp ba namespace chính:
    - **stock** (`StockEod`) → Dữ liệu EOD cấp cổ phiếu, bao gồm:
        - OHLCV (Open, High, Low, Close, Volume)
        - Các chỉ báo kỹ thuật (MA, RSI, MACD, Bollinger, v.v.)
        - Thống kê biến động và hiệu suất theo mã

    - **market** (`MarketEod`) → Dữ liệu chỉ số thị trường (VNINDEX, HNXINDEX, UPCOMINDEX):
        - Giá đóng cửa, khối lượng, vốn hóa, PE/PB toàn thị trường
        - So sánh diễn biến giữa các sàn

    - **sector** (`SectorEod`) → Dữ liệu EOD cấp ngành (ICB, VNSector...):
        - Hiệu suất ngành, thay đổi vốn hóa, tỷ trọng thanh khoản
        - So sánh ngành/tiểu ngành theo thời gian

    Examples
    --------
    >>> from fin68 import client
    >>> cli = client(api_key="sk_live_...")
    >>> cli.eod.stock.ohlcv("HPG", start="2024-01-01", end="2024-06-30")
    >>> cli.eod.market.ohlcv("VNINDEX", start="2024-01-01", end="2024-06-30")
    >>> cli.eod.sector.ohlcv("Ngân hàng", start="2024-01-01", end="2024-06-30")


    """

    _api_key_meta: Optional[ApiKeyMeta]
    """Thông tin meta của API key sau khi xác thực."""

    _messages: List[BackendMessage]
    """Danh sách thông điệp backend trả về sau validate."""

    def __init__(
        self,
        api_key: str,
        *,
        extra_context: Optional[Dict] = None,
    ) -> None: ...
    """Khởi tạo Fin68Client và tự động xác thực API key."""

    @property
    def api_key_metadata(self) -> Optional[ApiKeyMeta]: ...
    """Trả về meta của API key sau khi xác thực."""

    @property
    def messages(self) -> List[BackendMessage]: ...
    """Danh sách thông điệp backend trả về khi validate."""

    def close(self) -> None: ...
    """Đóng session HTTP và giải phóng tài nguyên."""

    def __enter__(self) -> "Fin68Client": ...
    """Vào context manager (`with`)."""

    def __exit__(self, exc_type, exc, tb) -> None: ...
    """Thoát context manager (`with`) và tự động đóng session."""

def client(
    apiKey: Optional[str] = None,
    *,
    api_key: Optional[str] = None,
    extra_context: Optional[Dict] = None,
) -> Fin68Client: ...
"""Factory khởi tạo và trả về một Fin68Client đã sẵn sàng sử dụng."""

__all__: list[str]
