Content Insertion
=================

This example leverages python-lolhtml to insert a navigation link into a webpage.

It specifically inserts a new `Sales` navigation entry after the second navigation entry using the following CSS 
selector:

```css
nav > ul > li:nth-of-type(2)
```

While this example loads content from the file in chunks, it is for demonstration purposes only, and it can be 
simplified by reading the entire file into memory and writing it to the reader immediately rather than performing 
chunking.