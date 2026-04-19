"""Generate a very large multi-file project with a target total number of lines.

Usage:
  python generate_big_project.py --lines 1981000 --out generated_project

WARNING: This will create many files and write a large amount of data to disk.
Ensure you have sufficient disk space and that you really want to proceed.
"""
import os
import argparse
from pathlib import Path


def create_scaffold(base: Path):
    (base / "src").mkdir(parents=True, exist_ok=True)
    (base / "tests").mkdir(parents=True, exist_ok=True)
    (base / "docs").mkdir(parents=True, exist_ok=True)

    # Create a modest set of starter files (these are small)
    for i in range(1, 13):
        fname = base / "src" / f"module_{i:02}.py"
        with fname.open("w", encoding="utf8") as f:
            f.write("# module stub\n")
            f.write(f"def hello_{i}():\n    return 'hello from module {i}'\n")

    # utils folder
    utils_dir = base / "src" / "utils"
    utils_dir.mkdir(parents=True, exist_ok=True)
    with (utils_dir / "__init__.py").open("w", encoding="utf8") as f:
        f.write("# utils package\n")


def distribute_lines(base: Path, total_lines: int, num_files: int):
    """Create `num_files` files under `base` (which should exist) and
    write repeated placeholder code lines until `total_lines` is reached."""

    files = []
    for i in range(num_files):
        p = base / f"big_file_{i+1:04}.py"
        files.append(p)

    # ensure directories exist
    for p in files:
        p.parent.mkdir(parents=True, exist_ok=True)

    # distribute lines evenly
    per_file = total_lines // num_files
    remainder = total_lines % num_files

    pattern = "# placeholder line: This file intentionally contains filler content for testing.\n"

    for idx, p in enumerate(files):
        lines_to_write = per_file + (1 if idx < remainder else 0)
        with p.open("w", encoding="utf8") as f:
            f.write(f"# File: {p.name} — generated filler\n")
            for n in range(lines_to_write):
                f.write(pattern)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lines", type=int, default=1981000, help="Total number of lines to generate")
    parser.add_argument("--out", type=str, default="generated_project", help="Output folder")
    parser.add_argument("--files", type=int, default=200, help="Number of files to create")
    args = parser.parse_args()

    out = Path(args.out)
    if out.exists():
        print(f"Output folder {out} already exists. Files may be overwritten.")
    else:
        out.mkdir(parents=True)

    print(f"Creating scaffold under {out}")
    create_scaffold(out)

    big_dir = out / "big_src"
    big_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating {args.lines} lines across {args.files} files in {big_dir}")
    distribute_lines(big_dir, args.lines, args.files)

    print("Generation complete.")


if __name__ == "__main__":
    main()
