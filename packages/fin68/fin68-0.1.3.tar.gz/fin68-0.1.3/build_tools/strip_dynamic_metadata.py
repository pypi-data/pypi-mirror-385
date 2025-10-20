from __future__ import annotations
from typing import Iterable
import argparse, base64, csv, hashlib, sys, tempfile, zipfile
from pathlib import Path
HEADERS_TO_STRIP = {"dynamic", "license-file"}  # lower-case, không dấu hai chấm

def _rewrite_wheel(path: Path) -> bool:
    if not path.is_file():
        raise FileNotFoundError(path)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        with zipfile.ZipFile(path) as whl:
            whl.extractall(tmp)

        dist_info_dirs = list(tmp.glob("*.dist-info"))
        if not dist_info_dirs:
            raise RuntimeError(f"{path} missing *.dist-info")
        di = dist_info_dirs[0]

        meta = di / "METADATA"
        lines = meta.read_text(encoding="utf-8").splitlines()

        filtered, skip_cont = [], False
        for line in lines:
            if skip_cont and (line.startswith(" ") or line.startswith("\t")):
                continue
            skip_cont = False
            if ":" in line:
                name, _ = line.split(":", 1)
                if name.strip().lower() in HEADERS_TO_STRIP:
                    skip_cont = True
                    continue
            filtered.append(line)

        changed = filtered != lines
        if changed:
            meta.write_text("\n".join(filtered) + "\n", encoding="utf-8")

        # RECORD signatures (giờ đã sai) → xóa nếu tồn tại
        for sig in ("RECORD.jws", "RECORD.p7s"):
            p = di / sig
            if p.exists():
                p.unlink()

        # Ghi lại RECORD
        rec = di / "RECORD"
        rows = []
        for fp in sorted(tmp.rglob("*")):
            if fp.is_dir():
                continue
            rel = fp.relative_to(tmp).as_posix()
            if fp == rec:
                rows.append((rel, "", ""))
                continue
            data = fp.read_bytes()
            digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode()
            rows.append((rel, f"sha256={digest}", str(len(data))))
        with rec.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows(rows)

        tmp_wheel = path.with_suffix(".tmp.whl")
        with zipfile.ZipFile(tmp_wheel, "w", compression=zipfile.ZIP_DEFLATED) as whl:
            for fp in sorted(tmp.rglob("*")):
                if not fp.is_dir():
                    whl.write(fp, fp.relative_to(tmp).as_posix())
        tmp_wheel.replace(path)
        return changed


def _iter_wheels(patterns: Iterable[str]) -> list[Path]:
    wheels: list[Path] = []
    for pattern in patterns:
        matched = list(Path(".").glob(pattern))
        wheels.extend(p for p in matched if p.suffix == ".whl")
    return wheels


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Strip unsupported Dynamic:* metadata entries from wheel files."
    )
    parser.add_argument(
        "patterns",
        nargs="*",
        default=["dist/*.whl"],
        help="Glob patterns pointing to wheel files (default: dist/*.whl).",
    )
    args = parser.parse_args(argv)

    wheels = _iter_wheels(args.patterns)
    if not wheels:
        print("strip_dynamic_metadata: no wheel files found.", file=sys.stderr)
        return 1

    for wheel_path in wheels:
        changed = _rewrite_wheel(wheel_path)
        action = "updated" if changed else "skipped"
        print(f"{action}: {wheel_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
