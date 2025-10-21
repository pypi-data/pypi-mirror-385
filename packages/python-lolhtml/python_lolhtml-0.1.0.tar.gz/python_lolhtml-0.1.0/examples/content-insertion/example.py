import pathlib
import lolhtml


class LinkInsertionHandler:
    def element(self, el: lolhtml.Element) -> None:
        el.after("""<li><a href="#">Sales</a></li>""", lolhtml.ContentType.HTML)


output: bytearray = bytearray()
rewriter: lolhtml.HTMLRewriter = lolhtml.HTMLRewriter(output.extend)
rewriter.on("nav > ul > li:nth-of-type(2)", LinkInsertionHandler())

webpage_path: pathlib.Path = pathlib.Path(__file__).parent.joinpath("webpage.html")
with open(webpage_path, "rb") as f:
    while True:
        chunk: bytes = f.read(1024)
        if not chunk:
            break

        rewriter.write(chunk)

rewriter.end()
print(output.decode("utf-8"))
