import unittest

from blocknode import BlockType, block_to_block_type


class TestBlockToBlockType(unittest.TestCase):
    # --- Headings ---

    def test_h1(self):
        self.assertEqual(block_to_block_type("# Heading one"), BlockType.HEADING)

    def test_h2(self):
        self.assertEqual(block_to_block_type("## Heading two"), BlockType.HEADING)

    def test_h6(self):
        self.assertEqual(block_to_block_type("###### Heading six"), BlockType.HEADING)

    def test_heading_requires_space_after_hashes(self):
        # No space after # means it's not a heading
        self.assertEqual(block_to_block_type("#NoSpace"), BlockType.PARAGRAPH)

    def test_seven_hashes_is_not_heading(self):
        self.assertEqual(block_to_block_type("####### Too many"), BlockType.PARAGRAPH)

    def test_hash_in_middle_is_paragraph(self):
        self.assertEqual(
            block_to_block_type("text # not a heading"), BlockType.PARAGRAPH
        )

    # --- Code ---

    def test_code_block(self):
        self.assertEqual(block_to_block_type("```\nsome code\n```"), BlockType.CODE)

    def test_code_block_multiline(self):
        block = "```\ndef hello():\n    print('hi')\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_code_block_with_language(self):
        block = "```python\nprint('hi')\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_code_missing_closing_backticks(self):
        self.assertEqual(block_to_block_type("```\nsome code"), BlockType.PARAGRAPH)

    def test_code_missing_opening_backticks(self):
        self.assertEqual(block_to_block_type("some code\n```"), BlockType.PARAGRAPH)

    def test_two_backticks_is_not_code(self):
        self.assertEqual(block_to_block_type("``\ncode\n``"), BlockType.PARAGRAPH)

    # --- Quote ---

    def test_single_line_quote(self):
        self.assertEqual(block_to_block_type(">This is a quote"), BlockType.QUOTE)

    def test_single_line_quote_with_space(self):
        self.assertEqual(block_to_block_type("> This is a quote"), BlockType.QUOTE)

    def test_multiline_quote(self):
        block = "> line one\n> line two\n> line three"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_quote_one_line_missing_gt(self):
        # Second line doesn't start with >
        block = "> line one\nline two"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    # --- Unordered list ---

    def test_unordered_list_single_item(self):
        self.assertEqual(block_to_block_type("- item one"), BlockType.UNORDERED_LIST)

    def test_unordered_list_multiple_items(self):
        block = "- item one\n- item two\n- item three"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_unordered_list_missing_space(self):
        self.assertEqual(block_to_block_type("-no space"), BlockType.PARAGRAPH)

    def test_unordered_list_one_bad_line(self):
        block = "- good\nbad line\n- also good"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    # --- Ordered list ---

    def test_ordered_list_single_item(self):
        self.assertEqual(block_to_block_type("1. first"), BlockType.ORDERED_LIST)

    def test_ordered_list_multiple_items(self):
        block = "1. first\n2. second\n3. third"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_ordered_list_must_start_at_one(self):
        block = "2. second\n3. third"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_must_increment(self):
        # Skips from 1 to 3
        block = "1. first\n3. third"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_repeated_number(self):
        block = "1. first\n1. also first"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_missing_space_after_dot(self):
        block = "1.no space\n2.also no space"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_longer(self):
        block = "\n".join(f"{i}. item {i}" for i in range(1, 11))
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    # --- Paragraph fallback ---

    def test_plain_paragraph(self):
        self.assertEqual(block_to_block_type("Just some text."), BlockType.PARAGRAPH)

    def test_paragraph_with_inline_markdown(self):
        block = "This has **bold** and _italic_ and `code` inline."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_empty_string_is_paragraph(self):
        self.assertEqual(block_to_block_type(""), BlockType.PARAGRAPH)


if __name__ == "__main__":
    unittest.main()
