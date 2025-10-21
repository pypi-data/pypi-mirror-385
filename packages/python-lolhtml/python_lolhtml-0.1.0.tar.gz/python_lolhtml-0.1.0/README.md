<!--suppress HtmlDeprecatedAttribute-->
<div align="center">
   <h1>😂 python-lolhtml</h1>

[![Build Status](https://github.com/Jayson-Fong/python-lolhtml/actions/workflows/CI.yml/badge.svg?branch=main)](https://github.com/Jayson-Fong/python-lolhtml/actions/workflows/CI.yml)
[![Latest Version](https://img.shields.io/pypi/v/python-lolhtml.svg)](https://pypi.org/project/python-lolhtml/)
[![Python Versions](https://img.shields.io/pypi/pyversions/python-lolhtml.svg)](https://pypi.org/project/python-lolhtml/)
[![Format](https://img.shields.io/pypi/format/python-lolhtml.svg)](https://pypi.org/project/python-lolhtml/)
[![License](https://img.shields.io/pypi/l/python-lolhtml)](https://github.com/Jayson-Fong/python-lolhtml/blob/main/README.md)
[![Status](https://img.shields.io/pypi/status/python-lolhtml)](https://pypi.org/project/python-lolhtml/)
[![Types](https://img.shields.io/pypi/types/python-lolhtml)](https://pypi.org/project/python-lolhtml/)


</div>

<hr />

<div align="center">

[💼 Purpose](#purpose) | [⚡ Performance](#performance) | [🛠️ Installation](#installation) | [⚙️ Usage](#usage) | 
[⚖️ License](#license)

</div>

<hr />

# Purpose

python-lolhtml provides Python bindings for the [lol-html](https://crates.io/crates/lol_html) Rust crate, enabling
stream-capable HTML rewriting and parsing with minimal buffering while using CSS selectors.

It is particularly powerful when using Python as a reverse proxy to transform HTML content, such as for rewriting mixed
content links; however, while the API isn't directly made for it, it can also be used for web scraping. Through 
leveraging lol-html's streaming capabilities, content can be rewritten or parsed even when the content has not been 
fully received yet, enabling faster response times.

# Performance

As a Python binding, parsing is predominantly offloaded to Rust, which can provide a noticeable speedup.

<details style="border: 1px solid; border-radius: 8px; padding: 8px; margin-top: 4px;">
<summary>🔍 python-lolhtml v. BeautifulSoup4: Text Extraction</summary>

For websites where there exists minimal content to parse, BeautifulSoup4 tends to produce output faster compared to 
python-lolhtml; however, when parsing real-world websites such as Wikipedia, there can be noticeable speedups in 
parsing time.

The following example fetches a Wikipedia article about the Python programming language. While this metric is not run on
standardized hardware (rather, it is a consumer-grade laptop with an Intel CPU), it produces the following output:

```
BeautifulSoup4: 36.069569201001286 seconds
python-lolhtml: 15.644805246000033 seconds
python-lolhtml Speedup: 2.305530087069849
```

This demonstrates roughly a 2.3x speedup compared to parsing conducted with BeautifulSoup4 for text extraction.

<details style="border: 1px solid; border-radius: 8px; padding: 8px; margin-top: 4px;">
<summary>🚰 Source Code</summary>

```python
import timeit
from typing import List

import requests
from bs4 import BeautifulSoup

import lolhtml


content: bytes = requests.get(
    "https://en.wikipedia.org/wiki/Python_(programming_language)",
    headers={"User-Agent": "Python - Performance Testing"},
).text.encode("utf-8")


def time_beautiful_soup():
    soup = BeautifulSoup(content, "html.parser")
    soup.get_text()


class ElementHandler:

    def __init__(self, value_store: List[str]):
        self.value_store: List[str] = value_store

    def text(self, text_chunk: lolhtml.TextChunk):
        self.value_store.append(text_chunk.text)


def time_lolhtml():
    output: bytearray = bytearray()
    element_handler: ElementHandler = ElementHandler([])

    rewriter: lolhtml.HTMLRewriter = lolhtml.HTMLRewriter(output.extend)
    rewriter.on("*", element_handler)
    rewriter.write(content)
    rewriter.end()


beautiful_soup_time: float = timeit.timeit(time_beautiful_soup, number=100)
print("BeautifulSoup4:", beautiful_soup_time, "seconds")

python_lolhtml_time: float = timeit.timeit(time_lolhtml, number=100)
print("python-lolhtml:", python_lolhtml_time, "seconds")
print("python-lolhtml Speedup:", beautiful_soup_time / python_lolhtml_time)
```

</details>

</details>

# Installation

python-lolhtml is available for installation from PyPI:

```shell
python -m pip install python-lolhtml
```

For the latest development builds, you may alternatively build the package yourself from GitHub:

```shell
python3 -m pip install git+https://github.com/Jayson-Fong/python-lolhtml.git
```

# Usage

For each rewriting or parsing task, a `lolhtml.HTMLRewriter` instance is required. It includes a buffer that can be 
written to where the content is then streamed, matching is performed against CSS selectors, and handlers are executed
as defined.

For example, to upgrade anchor links:

```python
import lolhtml


class AnchorUpgrader:
    # noinspection PyMethodMayBeStatic
    def element(self, el: lolhtml.Element):
        if not el.has_attribute("href"):
            return
        
        current_link: str = el.get_attribute("href")
        if current_link.startswith("http://"):
            el.set_attribute("href", "https" + current_link[4:])
            

output: bytearray = bytearray()
rewriter: lolhtml.HTMLRewriter = lolhtml.HTMLRewriter(output.extend)
rewriter.on("a", AnchorUpgrader())

rewriter.write(b'<html><a href="http://example">Link</a></html>')
rewriter.end()

print(output)
```

You may also choose to stream content and provide it to the HTMLRewriter instance as it becomes available:

```python
import lolhtml
import requests


class HeaderSwapHandler:
    # noinspection PyMethodMayBeStatic
    def text(self, t: lolhtml.TextChunk):
        if t.text == "Example Domain":
            t.replace("python-lolhtml Example")


with requests.get("https://example.com", stream=True) as r:
    r.raise_for_status()

    output: bytearray = bytearray()
    rewriter: lolhtml.HTMLRewriter = lolhtml.HTMLRewriter(output.extend)
    rewriter.on("h1, title", HeaderSwapHandler())

    for chunk in r.iter_content(chunk_size=8192):
        rewriter.write(chunk)

    rewriter.end()
    print(output.decode("utf-8"))
```

A variety of method and property-specific examples can be found in [python-lolhtml/tests](https://github.com/Jayson-Fong/python-lolhtml/tree/main/tests) and 
[python-lolhtml/examples](https://github.com/Jayson-Fong/python-lolhtml/tree/main/examples).

# License

While the python-lolhtml code is under the MIT license, the distribution (built `.whl` files) include lol-html, which is 
licensed under the BSD 3-Clause License.