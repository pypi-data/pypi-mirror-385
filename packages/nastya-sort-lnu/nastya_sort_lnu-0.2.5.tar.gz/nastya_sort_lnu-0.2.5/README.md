# nastya-sort

Lightweight implementation of Unix `sort` utility in Python with Click framework.

## Features

- ✅ Sort lines from files or stdin
- ✅ Numeric sorting with `-n` flag
- ✅ Reverse order with `-r` flag
- ✅ Docker support
- ✅ Compatible with Unix sort behavior

## Installation

### From source

```bash
git clone https://github.com/Nastia2004/nastya-sort-lnu.git
cd nastya-sort-lnu
pip install -e .
```

### Using Docker

```bash

# Or build locally
docker build -t nastya-sort .
```

## Usage

### Command Line Interface

```bash
# Sort lines from stdin
echo -e "banana\napple\ncherry" | sort

# Sort file contents
sort file.txt

# Numeric sort
echo -e "10\n2\n100\n20" | sort -n
# Output: 2, 10, 20, 100

# Reverse order
sort -r file.txt

# Combine options
sort -rn numbers.txt
```

## Command Options

| Option | Description |
|--------|-------------|
| `-n, --numeric` | Compare according to string numerical value |
| `-r, --reverse` | Reverse the result of comparisons |
| `-h, --help` | Show help message and exit |

## Examples

### Basic Sorting

```bash
# Alphabetical sort
cat names.txt | sort

# Sort and save to file
sort input.txt > sorted.txt
```

### Numeric Sorting

```bash
# Sort numbers correctly
echo -e "100\n20\n3\n1000" | sort -n
# Output:
# 3
# 20
# 100
# 1000
```

### Reverse Sorting

```bash
# Descending order
echo -e "a\nc\nb" | sort -r
# Output:
# c
# b
# a
```

### Combined with Other Tools

```bash
# Sort and remove duplicates
sort file.txt | uniq

# Sort CSV by second column
cut -d',' -f2 data.csv | sort -n

# Count and sort word frequency
cat text.txt | tr ' ' '\n' | sort | uniq -c | sort -rn
```

## Development

### Setup Environment

```bash
# Create virtual environment
python3 -m venv test
source test/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

### Building Docker Image

```bash
docker build -t nastya-sort .
docker run nastya-sort --help
```

### Testing

```bash
# Test basic sorting
echo -e "c\na\nb" | sort

# Test numeric sorting
echo -e "10\n2\n1" | sort -n

# Test with Docker
echo -e "3\n1\n2" | docker run -i nastya-sort -n
```


## Project Structure

```
nastya-sort/
├── nastya_sort/
│   ├── __init__.py       # Package version
│   └── cli.py            # CLI implementation
├── .github/
│   └── workflows/
│       └── docker-publish.yml  # CI/CD pipeline
├── Dockerfile            # Docker image definition
├── setup.py              # Package configuration
├── README.md             # This file
└── .gitignore           # Git ignore rules
```