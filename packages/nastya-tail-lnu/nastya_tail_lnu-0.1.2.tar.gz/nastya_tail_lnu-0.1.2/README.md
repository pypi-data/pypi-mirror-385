# nastya-tail

⚡ Lightweight and optimized implementation of Unix `tail` utility in Python with Click framework.

## Features

- ✅ Output last N lines from files or stdin (default: 10)
- ✅ Byte-based output with `-c` option
- ✅ Multiple file support with headers
- ✅ Memory-efficient using `deque` for large files
- ✅ Optimized file seeking for byte operations
- ✅ Compatible with Unix tail behavior
- ✅ Published on PyPI

## Installation
```bash
pip install nastya-tail-lnu
```

## Usage
```bash
# Last 10 lines (default)
tail file.txt

# Last 20 lines
tail -n 20 file.txt

# Last 100 bytes
tail -c 100 file.txt

# Multiple files with headers
tail file1.txt file2.txt
```

## Command Options

| Option | Description |
|--------|-------------|
| `-n, --lines N` | Output the last N lines (default: 10) |
| `-c, --bytes N` | Output the last N bytes |
| `-v, --verbose` | Always print filename headers |
| `-q, --quiet` | Never print filename headers |
| `-h, --help` | Show help message |

## Performance

- Uses `collections.deque` for memory efficiency
- File seeking for byte operations
- Memory usage: O(n) where n is number of lines to output
- Works efficiently with GB-sized files

---

## 📁 Структура директорій

Створіть таку структуру:
```
nastya-tail/
├── .github/
│   └── workflows/
│       └── pypi-publish.yml
├── nastya_tail/
│   ├── __init__.py
│   └── cli.py
├── .gitignore
├── LICENSE
├── MANIFEST.in
├── pyproject.toml
├── README.md
└── setup.py