# Docufill

Extract guest info from passport and ID scans. Built for hotel receptionists who are tired of manually typing data from document photocopies.

## How it works

1. Feed it a passport/ID image (JPG, PNG) or PDF
2. It tries MRZ (Machine Readable Zone) extraction first — the two lines of text at the bottom of passports
3. If no MRZ is found, it falls back to full-page OCR with pattern matching
4. You get structured fields: name, DOB, passport number, nationality, expiry, sex

## Install

```bash
pip install docufill
```

### System dependencies

Docufill needs Tesseract and Poppler installed on your system:

**macOS:**
```bash
brew install tesseract poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr poppler-utils
```

**Windows:**
```bash
choco install tesseract poppler
```

Run `docufill doctor` to verify everything is set up.

## Usage

### CLI

```bash
# Check dependencies
docufill doctor

# Scan a document
docufill scan passport.jpg
docufill scan passport.pdf --json

# Launch web UI
docufill serve
docufill serve --port 8080
```

### Web UI

```bash
docufill serve
```

Opens a local web page with drag-and-drop. Drop a passport scan, get a table of extracted fields with copy buttons.

### Python API

```python
from docufill.scanner import scan

result = scan("passport.jpg")
print(result.full_name)
print(result.date_of_birth)
print(result.to_json())
```

## Development

```bash
git clone https://github.com/docufill/docufill
cd docufill
pip install -e ".[dev]"
pytest
```

## License

MIT
