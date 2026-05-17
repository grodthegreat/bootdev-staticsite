import unittest

from blocks import markdown_to_blocks, markdown_to_html_node


class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_heading_paragraph_list(self):
        md = """
# This is a heading

This is a paragraph of text. It has some **bold** and _italic_ words inside of it.

- This is the first list item in a list block
- This is a list item
- This is another list item
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "# This is a heading",
                "This is a paragraph of text. It has some **bold** and _italic_ words inside of it.",
                "- This is the first list item in a list block\n- This is a list item\n- This is another list item",
            ],
        )

    def test_single_block(self):
        md = "Just one paragraph with no blank lines."
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["Just one paragraph with no blank lines."])

    def test_empty_string(self):
        blocks = markdown_to_blocks("")
        self.assertEqual(blocks, [])

    def test_only_whitespace(self):
        blocks = markdown_to_blocks("   \n\n   \n\n   ")
        self.assertEqual(blocks, [])

    def test_strips_leading_and_trailing_whitespace_from_blocks(self):
        md = """
  padded block  

  another padded block  
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["padded block", "another padded block"])

    def test_excessive_blank_lines_between_blocks(self):
        # Three or more newlines between blocks should still produce two blocks
        md = "first block\n\n\n\nsecond block"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["first block", "second block"])

    def test_leading_and_trailing_blank_lines(self):
        # Blank lines at the start/end of the document should not produce empty blocks
        md = "\n\nfirst block\n\nsecond block\n\n"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["first block", "second block"])

    def test_multiline_block_preserved(self):
        # Newlines within a block (single \n) must be kept intact
        md = """
line one
line two
line three

separate block
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "line one\nline two\nline three",
                "separate block",
            ],
        )

    def test_code_block(self):
        md = """
Here is some code:

```python
def hello():
    print("hello")
```

And some text after.
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "Here is some code:",
                '```python\ndef hello():\n    print("hello")\n```',
                "And some text after.",
            ],
        )

    def test_paragraph(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p></div>",
        )

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_lists(self):
        md = """
- This is a list
- with items
- and _more_ items

1. This is an `ordered` list
2. with items
3. and more items

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>This is a list</li><li>with items</li><li>and <i>more</i> items</li></ul><ol><li>This is an <code>ordered</code> list</li><li>with items</li><li>and more items</li></ol></div>",
        )

    def test_headings(self):
        md = """
# this is an h1

this is paragraph text

## this is an h2
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>this is an h1</h1><p>this is paragraph text</p><h2>this is an h2</h2></div>",
        )

    def test_blockquote(self):
        md = """
> This is a
> blockquote block

this is paragraph text

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>This is a blockquote block</blockquote><p>this is paragraph text</p></div>",
        )

    def test_code(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )


if __name__ == "__main__":
    unittest.main()
