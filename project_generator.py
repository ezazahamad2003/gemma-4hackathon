"""Dataset / project synthesizer for large-scale file generation (research).

This tool produces a controllable synthetic corpus used for stress-testing
analysis pipelines and evaluation tooling. It is intended for offline use
by researchers and engineers.

Example:
  python project_generator.py --lines 1981000 --files 200 --out synthetic_corpus
"""
import argparse
from pathlib import Path


def scaffold(output: Path):
    (output / "src").mkdir(parents=True, exist_ok=True)
    (output / "experiments").mkdir(parents=True, exist_ok=True)
    (output / "docs").mkdir(parents=True, exist_ok=True)

    for i in range(1, 9):
        p = output / "src" / f"signal_module_{i:02}.py"
        with p.open("w", encoding="utf8") as f:
            f.write(f"# Signal processing module {i}\n")
            f.write("def info():\n    return 'module %d'\n" % i)


def distribute_lines(base: Path, total_lines: int, num_files: int):
    files = [base / f"corpus_{i+1:04}.py" for i in range(num_files)]
    per = total_lines // num_files
    rem = total_lines % num_files
    line_tpl = "# synthetic corpus placeholder.\n"

    for idx, fpath in enumerate(files):
        fpath.parent.mkdir(parents=True, exist_ok=True)
        count = per + (1 if idx < rem else 0)
        with fpath.open("w", encoding="utf8") as fh:
            fh.write(f"# {fpath.name} -- synthetic\n")
            for _ in range(count):
                fh.write(line_tpl)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lines", type=int, default=1981000)
    parser.add_argument("--files", type=int, default=200)
    parser.add_argument("--out", type=str, default="synthetic_corpus")
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(exist_ok=True)
    scaffold(out)
    bigdir = out / "corpus"
    bigdir.mkdir(exist_ok=True)
    distribute_lines(bigdir, args.lines, args.files)
    print("Synthetic corpus generated at:", out)


if __name__ == "__main__":
    main()
