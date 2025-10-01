from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
import difflib
from pathlib import Path
from typing import List


@dataclass
class DiffPair:
    title: str
    from_path: Path
    to_path: Path


def read_text_utf8(path: Path) -> List[str]:
    return path.read_text(encoding="utf-8").splitlines(True)


def compute_unified_diff(from_file: Path, to_file: Path) -> str:
    from_lines = read_text_utf8(from_file)
    to_lines = read_text_utf8(to_file)
    diff_lines = difflib.unified_diff(
        from_lines,
        to_lines,
        fromfile=str(from_file),
        tofile=str(to_file),
        lineterm="",
        n=3,
    )
    return "\n".join(diff_lines)


def build_markdown(pairs: List[DiffPair]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines: List[str] = []
    lines.append(f"# 02-modified と new の差分集約\n\n")
    lines.append(f"生成日時: {now}\n\n")

    for pair in pairs:
        lines.append(f"## {pair.title}\n\n")
        lines.append("- **from**: " + str(pair.from_path).replace('\\\\', '/') + "\n")
        lines.append("- **to**: " + str(pair.to_path).replace('\\\\', '/') + "\n\n")

        unified = compute_unified_diff(pair.from_path, pair.to_path)
        if not unified.strip():
            lines.append("差分なし\n\n")
            continue

        lines.append("```diff\n")
        lines.append(unified + "\n")
        lines.append("```\n\n")

    return "".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate unified diff markdown for specified pairs.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("review/03-modifications/差分_02-modified_vs_new.md"),
        help="Output markdown file path",
    )
    args = parser.parse_args()

    pairs: List[DiffPair] = [
        DiffPair(
            title="DAO運営規程 v2.0 → v2.1",
            from_path=Path("new/DAO運営規程ver2.0.md"),
            to_path=Path("review/02-modified/運営規程ver2.1.md"),
        ),
        DiffPair(
            title="DAO総会規程 v2.0 → v2.1",
            from_path=Path("new/DAO総会規程ver2.0.md"),
            to_path=Path("review/02-modified/DAO総会規程ver2.1.md"),
        ),
        DiffPair(
            title="トークン規程 v2.1 → v2.2",
            from_path=Path("new/トークン規程_v2.1_統合版.md"),
            to_path=Path("review/02-modified/トークン規程ver2.2.md"),
        ),
    ]

    # Validate existence early with a clear error message
    missing: List[str] = [
        str(p)
        for pair in pairs
        for p in (pair.from_path, pair.to_path)
        if not p.exists()
    ]
    if missing:
        raise FileNotFoundError("Missing files: " + ", ".join(missing))

    content = build_markdown(pairs)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(content, encoding="utf-8")
    print(str(args.output))


if __name__ == "__main__":
    main()


