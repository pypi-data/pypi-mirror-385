from __future__ import annotations

"""
Fin68 Python Client
===================

Client cấp cao giúp xác thực API Key, hiển thị thông báo từ backend và cung cấp
các domain client như :class:`EodClient`. Thiết kế theo pattern "facade" để người
dùng khởi tạo một lần và làm việc qua thuộc tính `client.eod`, v.v.

Notes
-----
- Sử dụng `private_core.HttpSession` để gắn `base_url`, `timeout` và `user-agent`.
- Tự động gọi `validate_api_key` khi khởi tạo để nhận thông tin phiên bản, cảnh báo
  và meta của API key.
- Tất cả cảnh báo/nhắc nâng cấp được hiển thị qua `warnings.warn` hoặc `logging`.

See Also
--------
EodClient
    Domain client cho dữ liệu EOD.
"""

import logging
import warnings
from typing import Optional

from private_core.auth_core import validate_api_key
from private_core.http_core import BASE_URL, DEFAULT_TIMEOUT, HttpSession

from ._version import __version__
from .clients import EodClient
from .exceptions import ApiKeyValidationError, ConfigurationError
from .types import ApiKeyMeta, ApiKeyValidationResponse, BackendMessage, MessageType

logger = logging.getLogger(__name__)


class Fin68Client:
    """
    Điểm truy cập chính tổng hợp các domain client của Fin68.

    Khi khởi tạo, client sẽ:
    1) Tạo `HttpSession` với API key.
    2) Gọi `validate_api_key` để xác thực và lấy thông tin phiên bản.
    3) Hiển thị các thông báo (nâng cấp/báo lỗi/cảnh báo) từ backend tới người dùng.
    4) Khởi tạo các domain client (hiện tại: `eod`).

    Parameters
    ----------
    api_key : str
        API key hợp lệ do Fin68 phát hành.
    extra_context : dict, optional
        Ngữ cảnh bổ sung gửi lên backend khi validate (VD: môi trường chạy, app_name).

    Attributes
    ----------
    eod : EodClient
        Domain client cho dữ liệu EOD (OHLCV, technical, ...).
    _session : HttpSession
        Phiên HTTP dùng chung cho toàn bộ domain client.
    _api_key_meta : ApiKeyMeta or None
        Thông tin meta của API key sau khi xác thực.
    _messages : list[BackendMessage]
        Danh sách thông điệp backend trả về sau validate.

    Raises
    ------
    ConfigurationError
        Khi `api_key` rỗng/không được cung cấp.
    ApiKeyValidationError
        Khi xác thực API key thất bại (khóa sai/hết hạn/hệ thống từ chối).

    Examples
    --------
    Khởi tạo và dùng như context manager:

    >>> from fin68 import client
    >>> with client(api_key="sk_live_...") as cli:
    ...     df = cli.eod.ohlcv("HPG", start="2024-01-01", end="2024-12-31")

    Hoặc quản lý vòng đời thủ công:

    >>> cli = client(api_key="sk_live_...")
    >>> try:
    ...     meta = cli.api_key_metadata
    ...     data = cli.eod.ohlcv("VCB")
    ... finally:
    ...     cli.close()
    """

    def __init__(
        self,
        api_key: str,
        *,
        extra_context: Optional[dict] = None,
    ) -> None:
        """
        Khởi tạo client và xác thực API key ngay lập tức.

        Parameters
        ----------
        api_key : str
            API key hợp lệ.
        extra_context : dict, optional
            Context bổ sung gửi kèm khi validate.

        Raises
        ------
        ConfigurationError
            Khi không cung cấp API key.
        ApiKeyValidationError
            Khi backend từ chối API key (hết hạn, không hợp lệ, ...).
        """
        if not api_key:
            raise ConfigurationError("Cần cung cấp API key để khởi tạo fin68.client()")

        self._session = HttpSession(
            api_key,
            base_url=BASE_URL,
            timeout=DEFAULT_TIMEOUT,
            version=__version__,
        )
        self._api_key_meta: Optional[ApiKeyMeta] = None
        self._messages: list[BackendMessage] = []

        try:
            validation = validate_api_key(
                self._session,
                client_version=__version__,
                include_messages=True,
                extra_context=extra_context,
            )
        except ApiKeyValidationError:
            # Đảm bảo đóng session nếu validate thất bại
            self._session.close()
            raise
        self._api_key_meta = validation.meta
        self._messages = list(validation.iter_messages())

        self._surface_messages(validation)

        # Domain clients
        self.eod = EodClient(self._session)

    def _surface_messages(self, validation: ApiKeyValidationResponse) -> None:
        """
        Hiển thị các thông điệp từ backend (cảnh báo, lỗi, nhắc nâng cấp).

        Parameters
        ----------
        validation : ApiKeyValidationResponse
            Kết quả validate từ backend, bao gồm thông tin version và danh sách messages.

        Notes
        -----
        - Các thông điệp loại `WARNING`, `ERROR`, `NOTIFY_API_KEY_EXPIRING/EXPIRED`
          sẽ được hiển thị qua `warnings.warn(...)`.
        - Thông báo nâng cấp (khi client cũ hơn phiên bản tối thiểu/khuyến nghị)
          cũng được cảnh báo bằng `warnings.warn(...)` để người dùng sớm cập nhật.
        """
        version_info = validation.version
        for message in self._messages:
            if message.is_upgrade_notice() and version_info.requires_upgrade():
                _emit_upgrade_notice(message, version_info.backend_version)
            elif message.type in {
                MessageType.NOTIFY_API_KEY_EXPIRING,
                MessageType.NOTIFY_API_KEY_EXPIRED,
                MessageType.WARNING,
                MessageType.ERROR,
            }:
                warnings.warn(message.message, stacklevel=2)
            else:
                logger.info("Thông báo từ Fin68: %s", message.message)

        if version_info.requires_upgrade() and not any(m.is_upgrade_notice() for m in self._messages):
            warnings.warn(
                (
                    f"Đã có phiên bản fin68 mới hơn ({version_info.backend_version}). "
                    "Hãy cập nhật để sử dụng các tính năng và bản sửa lỗi mới nhất."
                ),
                stacklevel=2,
            )

        if version_info.is_out_of_support():
            warnings.warn(
                (
                    f"Phiên bản fin68 hiện tại ({version_info.client_version}) "
                    f"đã thấp hơn mức tối thiểu được hỗ trợ ({version_info.minimum_supported_version}). "
                    "Một số tính năng có thể không còn hoạt động ổn định."
                ),
                stacklevel=2,
            )

    @property
    def api_key_metadata(self) -> Optional[ApiKeyMeta]:
        """
        Trả về meta của API key sau khi xác thực.

        Returns
        -------
        ApiKeyMeta or None
            Meta của API key (ngày hết hạn, trạng thái, ...), hoặc `None` nếu không sẵn có.
        """
        return self._api_key_meta

    @property
    def messages(self) -> list[BackendMessage]:
        """
        Danh sách thông điệp backend trả về khi validate.

        Returns
        -------
        list[BackendMessage]
            Bản sao danh sách thông điệp để tránh chỉnh sửa ngoài ý muốn.
        """
        return list(self._messages)

    def close(self) -> None:
        """
        Đóng phiên HTTP bên dưới và giải phóng tài nguyên.

        Notes
        -----
        - Nên gọi trong `finally` hoặc dùng context manager để đảm bảo đóng phiên.
        """
        self._session.close()

    def __enter__(self) -> "Fin68Client":
        """
        Vào ngữ cảnh `with`.

        Returns
        -------
        Fin68Client
            Chính instance hiện tại.
        """
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        """
        Thoát ngữ cảnh `with` và tự động đóng phiên HTTP.

        Parameters
        ----------
        exc_type, exc, tb
            Thông tin ngoại lệ (nếu có). Không can thiệp vào flow ngoại lệ.
        """
        self.close()


def _emit_upgrade_notice(message: BackendMessage, latest_version: Optional[str]) -> None:
    """
    Hiển thị cảnh báo nâng cấp phiên bản client.

    Parameters
    ----------
    message : BackendMessage
        Thông điệp nâng cấp từ backend.
    latest_version : str or None
        Phiên bản mới nhất phía backend biết đến (nếu có).

    Notes
    -----
    - Sử dụng `warnings.warn(..., stacklevel=3)` để đẩy cảnh báo lên callsite người dùng.
    """
    suffix = f" Phiên bản mới nhất: {latest_version}" if latest_version else ""
    warnings.warn(f"{message.message}{suffix}", stacklevel=3)


def client(
    apiKey: Optional[str] = None,
    *,
    api_key: Optional[str] = None,
    extra_context: Optional[dict] = None,
) -> Fin68Client:
    """
    Factory tạo ra một :class:`Fin68Client` đã sẵn sàng sử dụng.

    Hỗ trợ cả hai tên tham số `api_key` (chuẩn Python) và `apiKey` (thân thiện
    với người dùng/JS). Nếu truyền cả hai, `api_key` sẽ được ưu tiên.

    Parameters
    ----------
    apiKey : str, optional
        API key. Chỉ dùng khi không truyền `api_key`.
    api_key : str, optional
        API key chuẩn (ưu tiên nếu được truyền).
    extra_context : dict, optional
        Ngữ cảnh bổ sung gửi lên backend khi validate.

    Returns
    -------
    Fin68Client
        Client đã xác thực xong, kèm các domain client như `eod`.

    Raises
    ------
    ConfigurationError
        Khi không cung cấp `api_key`/`apiKey`.
    ApiKeyValidationError
        Khi backend từ chối API key trong quá trình khởi tạo.

    Examples
    --------
    >>> from fin68 import client
    >>> cli = client(api_key="sk_live_...")
    >>> try:
    ...     df = cli.eod.ohlcv("HPG", start="2024-01-01", end="2024-06-30")
    ... finally:
    ...     cli.close()
    """
    key = api_key or apiKey
    if not key:
        raise ConfigurationError("Cần truyền tham số apiKey hoặc api_key khi khởi tạo fin68.client()")

    return Fin68Client(
        key,
        extra_context=extra_context,
    )


__all__ = ["Fin68Client", "client", "__version__"]
