# Big Project Generator

This repository includes `generate_big_project.py`, a script that will create a large multi-file project filled with placeholder lines.

Default command (creates ~1,981,000 lines across 200 files):

```bash
python generate_big_project.py --lines 1981000 --files 200 --out generated_project
```

Be cautious: this will create a large amount of data on disk. Adjust `--lines` and `--files` as needed.
