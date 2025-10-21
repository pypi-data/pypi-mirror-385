from __future__ import annotations

import math
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List


@dataclass
class FileStats:
    path: Path
    size: int
    formatted_size: str
    modified: datetime | None


def format_file_size(size: int) -> str:
    if size <= 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    power = min(int(math.log(size, 1024)), len(units) - 1)
    value = size / (1024 ** power)
    return f"{value:.2f} {units[power]}"


def get_file_stats(path: Path) -> FileStats:
    if not path.exists():
        return FileStats(path=path, size=0, formatted_size="0 B", modified=None)
    stat = path.stat()
    return FileStats(
        path=path,
        size=stat.st_size,
        formatted_size=format_file_size(stat.st_size),
        modified=datetime.fromtimestamp(stat.st_mtime),
    )


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def add_pdf_extension(path: Path) -> Path:
    return path if path.suffix.lower() == ".pdf" else path.with_suffix(".pdf")


def resolve_output_path(input_path: Path | str, output_path: str) -> Path:
    out = Path(output_path)
    if out.is_absolute():
        return out
    return Path(input_path).resolve().parent.joinpath(out).resolve()


def resolve_output_dir(input_path: Path | str, output_dir: str) -> Path:
    out = Path(output_dir)
    if out.is_absolute():
        return out
    return Path(input_path).resolve().parent.joinpath(out).resolve()


def parse_page_range(range_expression: str | None, total_pages: int) -> List[int]:
    if not range_expression or range_expression.strip().lower() in {"all", "*"}:
        return list(range(1, total_pages + 1))

    pages: list[int] = []
    parts = [part.strip() for part in range_expression.split(",") if part.strip()]
    if not parts:
        raise ValueError("页面范围字符串为空")

    for part in parts:
        if "-" in part:
            start_str, end_str = [p.strip() for p in part.split("-", 1)]
            if not start_str.isdigit() or not end_str.isdigit():
                raise ValueError(f"无效的页面范围: {part}")
            start = int(start_str)
            end = int(end_str)
            if start < 1 or end < 1 or start > end:
                raise ValueError(f"无效的页面范围: {part}")
            if end > total_pages:
                raise ValueError(f"页面范围超出总页数 {total_pages}: {part}")
            pages.extend(range(start, end + 1))
        else:
            if not part.isdigit():
                raise ValueError(f"无效的页面号: {part}")
            page = int(part)
            if page < 1 or page > total_pages:
                raise ValueError(f"页面号超出总页数 {total_pages}: {part}")
            pages.append(page)

    unique_pages = sorted(dict.fromkeys(pages))
    return unique_pages


def contains_chinese(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def slugify_for_filename(text: str, max_length: int = 32) -> str:
    normalized = re.sub(r"[\s]+", "_", text.strip())
    normalized = re.sub(r"[^\w\u4e00-\u9fff-]", "", normalized)
    return normalized[:max_length] or "watermark"
