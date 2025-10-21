from typing import List

import lolhtml
import requests


extracted_text: List[str] = []


class TextExtractHandler:
    # noinspection PyMethodMayBeStatic
    def text(self, t: lolhtml.TextChunk):
        normalized_text: str = t.text.strip()
        if len(normalized_text) > 3:
            extracted_text.append(normalized_text)
            print(normalized_text)


with requests.get(
    "https://en.wikipedia.org/wiki/Python_(programming_language)",
    headers={"User-Agent": "Requests Example"},
    stream=True,
) as r:
    r.raise_for_status()

    output: bytearray = bytearray()
    rewriter: lolhtml.HTMLRewriter = lolhtml.HTMLRewriter(lambda _: ...)
    rewriter.on("p, span, li, code, a, title, table", TextExtractHandler())

    for chunk in r.iter_content(chunk_size=8192):
        rewriter.write(chunk)

    rewriter.end()

print("Collected", len(extracted_text), "strings!")
