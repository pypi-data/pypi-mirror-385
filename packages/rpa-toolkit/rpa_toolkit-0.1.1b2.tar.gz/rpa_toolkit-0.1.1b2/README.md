# RPA Toolkit

A Python toolkit for Robotic Process Automation (RPA) with enhanced processing and solutions to common automation challenges.

## Overview

The RPA Toolkit is designed to simplify data extraction and automation tasks, particularly when working with different file formats like Excel, PDF, RTF, etc.

## Features

- **Excel Processing**: Advanced Excel file reading with automatic column name cleaning and data type casting
- **Header Detection**: Intelligent identification of header rows in Excel files where headers are not at the top
- **PDF Text Extraction**: Efficient extraction of text content from PDF files with page range selection, also supports extraction from the end of the document
- **Polars Integration**: Built on top of Polars for fast and memory-efficient DataFrame operations

## Prerequisites

- Python 3.10 or higher

## Installation

```bash
pip install rpa-toolkit
```

## Usage Examples

### Excel Processing

#### Basic Excel Reading

```python
from rpa_toolkit import read_excel

# Read an Excel file into a Polars LazyFrame
df = read_excel("data.xlsx")
result = df.collect()  # Convert to DataFrame when ready
```

#### Reading Specific Sheets

```python
# Read a specific sheet by name
df = read_excel("data.xlsx", sheet_name="SalesData")

# Read a specific sheet by ID (1-based sheet index)
df = read_excel("data.xlsx", sheet_id=1)
```

#### Advanced Excel Processing with Type Casting

```python
# Read Excel with specific column types
df = read_excel(
    "data.xlsx",
    cast={"date": pl.Date, "value": pl.Float64, "id": pl.Int64}
)
```

#### Finding Header Rows

```python
from rpa_toolkit import find_header_row

# Find the header row in an Excel file
header_row_index = find_header_row("messy_data.xlsx")
print(f"Header row found at index: {header_row_index}")

# Use the found header row to read the data
df = read_excel("messy_data.xlsx", header_row=header_row_index)
```

#### Finding Header Row with Expected Keywords

```python
# Find header row that contains specific keywords
header_row_index = find_header_row(
    "data.xlsx",
    expected_keywords=["name", "email", "date"]
)
df = read_excel("data.xlsx", header_row=header_row_index)
```

### PDF Processing

#### Basic PDF Text Extraction

```python
from rpa_toolkit import extract_text_from_pdf

# Extract all text from a PDF
text = extract_text_from_pdf("document.pdf")
print(text)
```

#### Extract Text from Specific Pages

```python
# Extract text from specific page range
text = extract_text_from_pdf("document.pdf", start_page=2, end_page=5)

# Extract text from first 3 pages
text = extract_text_from_pdf("document.pdf", start_page=0, end_page=3)
```

## Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Run the test suite: `pytest`
6. Commit your changes (`git commit -m 'feat: amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Setup

```bash
# Clone the repository
git clone https://github.com/your-username/rpa-toolkit.git
cd rpa-toolkit

# Install dependencies
pip install -e .
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=rpa_toolkit
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions, please file an issue on the GitHub repository.
