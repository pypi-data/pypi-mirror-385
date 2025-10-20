# calc-workbook

[![PyPI Version](https://img.shields.io/pypi/v/calc-workbook.svg)](https://pypi.org/project/calc-workbook/)
[![Python Versions](https://img.shields.io/pypi/pyversions/calc-workbook.svg)](https://pypi.org/project/calc-workbook/)

**`calc-workbook`** is a lightweight Python package that loads Excel files, computes all formulas using the [`formulas`](https://pypi.org/project/formulas/) package, and provides a simple, high-level API to access the computed cell values from each sheet.

Unlike other Excel packages, it focuses purely on formula evaluation and data retrieval in a Pythonic way.

---

## Overview

[`openpyxl`](https://pypi.org/project/openpyxl/) is the most common Python package for reading and writing Excel files; however, it does **not** calculate cell formulas.
The [`formulas`](https://pypi.org/project/formulas/) package adds support for evaluating a large set of Excel formulas, but it does **not** provide a straightforward interface to retrieve the computed values per sheet.

**`calc-workbook`** bridges that gap by exposing a simple interface with two core classes:

* `CalcWorkbook` – loads and computes the workbook, providing access to individual sheets.
* `CalcSheet` – provides access to computed cell values and sheet metadata.

---

## Installation

```bash
pip install calc-workbook
```

---

### Example Code

```python
from calc_workbook import CalcWorkbook

# Load workbook and compute formulas
wb = CalcWorkbook.load("example.xlsx")

# List available sheets (in lowercase)
print(wb.get_sheet_names())

# Access a specific sheet in lowercase
sheet = wb.get_sheet("sheet1")

# Retrieve computed values
print("A1:", sheet.cell("A1"))
print("A1:", sheet.cell([1, 1]))
print("B1:", sheet.cell("B1"))
print("C1:", sheet.cell("C1"))
```

## Limitations

* Sheet names are stored and accessed in **lowercase** internally.
  When calling `get_sheet()`, always use the lowercase name (e.g., `"sheet1"`).

---

## API Reference

### class CalcWorkbook

Represents a computed Excel workbook.

#### Methods

| Method                                | Description                                                                                                  |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `load(filename: str) -> CalcWorkbook` | Loads an Excel file, computes all formulas using the `formulas` engine, and returns a ready-to-use workbook. |
| `get_sheet_names() -> list[str]`      | Returns the list of all sheet names in the workbook.                                                         |
| `get_sheet(name: str) -> CalcSheet`   | Returns a `CalcSheet` object for the given sheet name.                                                       |

---

### class CalcSheet

Represents a single computed Excel worksheet.

#### Methods

| Method          | Description                                            |                |                                                                                              |
| --------------- | ------------------------------------------------------ | -------------- | -------------------------------------------------------------------------------------------- |
| `rows() -> int` | Returns the maximum number of rows containing data.    |                |                                                                                              |
| `cols() -> int` | Returns the maximum number of columns containing data. |                |                                                                                              |
| `cell(ref) -> Any` | Retrieves the computed value of a cell, either by `"A1"` format or `[col, row]` coordinates. |

---

---

## License

MIT License

Copyright (c) 2025 Alexandre Bento Freire

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
