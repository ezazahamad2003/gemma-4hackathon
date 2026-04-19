def write_text(path, text):
    with open(path, "w", encoding="utf8") as f:
        f.write(text)
