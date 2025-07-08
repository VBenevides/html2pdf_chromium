# html2pdf-chromium

Convert HTML files or HTML strings to PDF using Chromium-based browsers(like Chrome or Edge) in headless mode without dependencies such as chromedriver.


## ✨ Features

- 📄 Convert HTML **files or strings** to PDF
- 🧠 Uses **headless Chrome or Edge**
- 🧰 **No additional Python dependencies** — uses only the standard library
- ❌ **Does not require `chromedriver`** or Selenium

## 📦 Installation

```bash
pip install html2pdf-chromium
```


## Usage

### PDF from HTML File

```python
from html2pdf_chromium import Converter

converter = Converter()  # Uses Chrome by default
converter.convert_file("example.html", "output.pdf")
```

### PDF from HTML String

```python
from html2pdf_chromium import Converter

converter = Converter()  # Uses Chrome by default
content = """
<html>
  <body>
    <h1>Hello PDF!</h1>
    <p>This was generated from an HTML string.</p>
  </body>
</html>
"""
converter.convert_string(content, "output.pdf")
```

### Selecting browser (used to detect executables in common paths)

```python
from html2pdf_chromium import Converter

converter = Converter(browser="edge")
converter.convert_file("example.html", "output.pdf")
```

### Using a custom path for other Chromium based browsers

```python
from html2pdf_chromium import Converter

converter = Converter(executable_path="path_to_executable/chromium.exe") 
converter.convert_file("example.html", "output.pdf")
```
