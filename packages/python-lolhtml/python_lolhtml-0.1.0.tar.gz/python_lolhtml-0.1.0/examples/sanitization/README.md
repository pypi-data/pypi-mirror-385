Sanitization
=================

This example leverages python-lolhtml to delete potentially dangerous elements and attributes. We forbid tags besides 
`p` and `span`, which are common in blog posts. However, these tags could still contain malicious content, such as 
hidden text, prompting us to remove attributes.

Notice how the otherwise hidden message is revealed by removing the `style` tag. Additionally, the `script` tag is 
removed and its inner text is retained.

While this example loads all the content into the rewriter at once with one singular read, python-lolhtml also supports
streaming content and writing in chunks.

> [!CAUTION]
> It is generally a bad idea to make your own sanitizer, especially if your use case prompts a more permissive set of 
> rules. If you are not sure about what you are doing, consider using a purpose-built package like 
> [nh3](https://pypi.org/project/nh3/) or [bleach](https://pypi.org/project/bleach/).

> [!CAUTION]
> When making sanitizers using lol-html, you should generally **not** restrict sanitization to a specific element within
> the HTML. In these cases, the parser may effectively become confused and mistake an element to be outside the scope, 
> such as with tags that never close to where the outcome is determined by browser implementation.