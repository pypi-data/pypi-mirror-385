Web Scraping
=================

This example leverages python-lolhtml to scrape a webpage which could be particularly large and where we do not desire 
any HTML output. It discards the HTML produced by the HTMLRewriter but stores all text entries it identifies in a list.

Web pages can be quite noisy, so this example specifically targets HTML tags that generally contain useful content. 
Additionally, we filter the content by length after stripping strings to remove content such as punctuation. 
Punctuation-only strings frequently occur in cases where the previous word is a link and that word is the end of a 
paragraph.