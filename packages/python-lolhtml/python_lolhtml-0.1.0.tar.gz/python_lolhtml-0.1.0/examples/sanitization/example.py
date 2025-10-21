import pathlib
import lolhtml


class LinkInsertionHandler:
    def element(self, el: lolhtml.Element) -> None:
        if el.tag_name not in ("p", "span"):
            el.remove_and_keep_content()
            return

        for attribute_name, attribute_value in el.attributes:
            el.remove_attribute(attribute_name)


output: bytearray = bytearray()
rewriter: lolhtml.HTMLRewriter = lolhtml.HTMLRewriter(output.extend)
rewriter.on("*", LinkInsertionHandler())

webpage_path: pathlib.Path = pathlib.Path(__file__).parent.joinpath("webpage.html")
with open(webpage_path, "rb") as f:
    rewriter.write(f.read())

rewriter.end()
print(output.decode("utf-8"))
