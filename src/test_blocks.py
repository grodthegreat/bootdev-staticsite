import unittest

from blocks import markdown_to_blocks


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


if __name__ == "__main__":
    unittest.main()
