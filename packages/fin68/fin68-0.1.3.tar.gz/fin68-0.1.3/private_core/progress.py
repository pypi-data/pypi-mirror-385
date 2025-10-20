import sys
import os
import math
import time
import shutil
from dataclasses import dataclass

# ==========
# Helpers
# ==========
_SPINNER = ("⠋","⠙","⠸","⠴","⠦","⠇")  # nhẹ & mượt
_RESET = "\x1b[0m"
_DIM = "\x1b[2m"
_BOLD = "\x1b[1m"
_CYAN = "\x1b[36m"
_GREEN = "\x1b[38;2;93;105;244m"
_YELLOW = "\x1b[33m"
_BLUE = "\x1b[34m"

def _isatty() -> bool:
    return sys.stdout.isatty()

def _ansi_ok() -> bool:
    # Trên Win10+ đa số terminal hỗ trợ ANSI; nếu không, ta tự tắt.
    if os.name == "nt":
        # VSCode, Windows Terminal thường ok; nếu là non-tty -> tắt
        return _isatty()
    return _isatty()

def _fmt_time(seconds: float) -> str:
    if math.isinf(seconds) or seconds < 0:
        return "--:--"
    m, s = divmod(int(seconds + 0.5), 60)
    if m >= 100:  # cực dài
        h, m = divmod(m, 60)
        return f"{h:d}h{m:02d}m"
    return f"{m:02d}:{s:02d}"

def _term_width(default: int = 80) -> int:
    try:
        # dùng fallback của shutil cho chắc
        return shutil.get_terminal_size(fallback=(default, 24)).columns
    except Exception:
        return default
def _compose_right(current: int, total: int, rate: float, remaining: float, elapsed: float, pal) -> list[str]:
    # Tách các mảnh để có thể lược bớt khi thiếu chỗ
    parts = [
        f"{pal(_DIM)}{current}/{total}{pal(_RESET)}",
        f"{pal(_BLUE)}{int((current/total)*100) if total else 0:3d}%{pal(_RESET)}",
        f"{pal(_YELLOW)}{rate:0.2f}/s{pal(_RESET)}",
        f"ETA {pal(_YELLOW)}{_fmt_time(remaining)}{pal(_RESET)}",
        f"{pal(_DIM)}+{_fmt_time(elapsed)}{pal(_RESET)}",
    ]
    return parts

def _join_right(parts: list[str]) -> str:
    # Ghép "  " giữa các mảnh
    return "  ".join(parts)
@dataclass
class _Meter:
    total: int
    start_t: float
    last_draw_t: float
    symbol: str
    enable_color: bool
    min_redraw_interval: float = 1/24  # ~24 FPS max để tránh flicker

    def palette(self, code: str) -> str:
        return code if self.enable_color else ""

# ==========
# API: drop-in
# ==========
_state = None  # giữ meter hiện tại

def start_progress(total: int, symbol: str) -> None:
    """Gọi 1 lần trước khi bắt đầu."""
    global _state
    if total <= 0 or not _isatty():
        _state = None
        return
    _state = _Meter(
        total=total,
        start_t=time.perf_counter(),
        last_draw_t=0.0,
        symbol=symbol,
        enable_color=_ansi_ok()
    )
    _draw_progress(0)

def update_progress(current: int) -> None:
    """Gọi mỗi lần cập nhật tiến độ."""
    if _state is None:
        return
    # throttle để nhẹ CPU
    now = time.perf_counter()
    if now - _state.last_draw_t < _state.min_redraw_interval and current < _state.total:
        return
    _draw_progress(current)

def finish_progress() -> None:
    """Gọi khi hoàn tất."""
    if _state is None:
        return
    _draw_progress(_state.total, force=True)
    sys.stdout.write("\n")
    sys.stdout.flush()

# ==========
# Renderer
# ==========
def _draw_progress(current: int, force: bool = False) -> None:
    global _state
    m = _state
    current = max(0, min(current, m.total))
    now = time.perf_counter()
    elapsed = max(1e-9, now - m.start_t)
    rate = current / elapsed
    remaining = (m.total - current) / rate if rate > 0 else float("inf")

    spin = _SPINNER[int(now * 10) % len(_SPINNER)]
    pal = m.palette
    ok = (current == m.total)

    left = f"{pal(_BOLD)}{spin if not ok else '✔'}{pal(_RESET)} {pal(_CYAN)}{m.symbol}{pal(_RESET)}"

    # Khởi tạo right thành các mảnh để co giãn
    right_parts = _compose_right(current, m.total, rate, remaining, elapsed, pal)

    width = max(40, _term_width())
    bar_min = 10

    # Ước lượng trước rồi co giãn nếu cần
    def _len_noansi(s: str) -> int:
        return len(_strip_ansi(s))

    # Tính budget cho toàn bộ dòng:
    # left + " [" + bar + "] " + right  <= width
    # => budget_right_bar = width - len(left) - 4 (ngoặc + khoảng trắng)
    budget_right_bar = width - _len_noansi(left) - 4
    if budget_right_bar < bar_min:
        # Không đủ chỗ: phải cắt right trước
        budget_right_bar = bar_min

    # Bắt đầu với right đầy đủ, rồi giảm dần nếu không vừa
    right = _join_right(right_parts)
    # Tính bar_w còn lại sau khi dành chỗ cho right hiện tại
    bar_w = max(bar_min, budget_right_bar - _len_noansi(right))
    if bar_w < bar_min:
        # Co right bằng cách bỏ dần mảnh từ ít quan trọng nhất
        # thứ tự bỏ: elapsed, ETA, rate, percent -> vẫn giữ "current/total"
        drop_order = [4, 3, 2, 1]  # indices trong right_parts
        rp = right_parts[:]
        for idx in drop_order:
            if idx < len(rp):
                rp.pop(idx)
                right = _join_right(rp)
                bar_w = max(bar_min, budget_right_bar - _len_noansi(right))
                if bar_w >= bar_min:
                    break
        right_parts = rp

    # Recompute final right/bar
    right = _join_right(right_parts)
    frac = 0 if m.total == 0 else current / m.total
    filled = int(bar_w * frac)
    bar = "█" * filled + "░" * (bar_w - filled)

    line = f"{left} [{pal(_GREEN)}{bar}{pal(_RESET)}] {right}"
    # Nếu vẫn dài hơn width (do ký tự rộng hẹp), pad/trunc an toàn
    sys.stdout.write("\r" + _pad_to_width(line, width))
    sys.stdout.flush()
    m.last_draw_t = now
def _strip_ansi(s: str) -> str:
    # đơn giản: bỏ các chuỗi ESC[...\w
    import re
    return re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", s)

def _pad_to_width(s: str, width: int) -> str:
    s_len = len(_strip_ansi(s))
    if s_len < width:
        return s + " " * (width - s_len)
    return s[:width]
