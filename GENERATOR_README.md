# Synthetic Corpus Generator (research)

`project_generator.py` produces a synthetic corpus for stress-testing and evaluation. Use this tool when you need reproducible, instrumented datasets for pipelines.

Example:

```bash
python project_generator.py --lines 1981000 --files 200 --out synthetic_corpus
```

Adjust `--lines` and `--files` to reduce generation size for local testing.
