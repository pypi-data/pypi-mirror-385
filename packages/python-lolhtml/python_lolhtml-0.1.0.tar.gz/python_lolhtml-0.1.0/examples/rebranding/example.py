import pathlib
import lolhtml


class LinkInsertionHandler:
    def text(self, t: lolhtml.TextChunk) -> None:
        t.replace(t.text.replace("lol-html", "python-lolhtml"))


output: bytearray = bytearray()
rewriter: lolhtml.HTMLRewriter = lolhtml.HTMLRewriter(output.extend)
rewriter.on("title, p, main", LinkInsertionHandler())

webpage_path: pathlib.Path = pathlib.Path(__file__).parent.joinpath("webpage.html")
with open(webpage_path, "rb") as f:
    while True:
        chunk: bytes = f.read(1024)
        if not chunk:
            break

        rewriter.write(chunk)

rewriter.end()
print(output.decode("utf-8"))
