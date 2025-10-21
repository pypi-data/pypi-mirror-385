Rebranding
==========

This example leverages python-lolhtml to rebrand a webpage from "lol-html" to "python-lolhtml" by string replacement
within `title`, `p`, and `main` tags. These are specified to avoid affecting business-logic, such as the content of
`script` tags.

While this example loads content from the file in chunks, it is for demonstration purposes only, and it can be 
simplified by reading the entire file into memory and writing it to the reader immediately rather than performing 
chunking.