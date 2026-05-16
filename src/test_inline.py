import unittest

from inline import (
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_delimiter,
)
from textnode import TextNode, TextType


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_code_block(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            result,
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
        )

    def test_bold(self):
        node = TextNode(
            "This is text with a **bolded phrase** in the middle", TextType.TEXT
        )
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            result,
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bolded phrase", TextType.BOLD),
                TextNode(" in the middle", TextType.TEXT),
            ],
        )

    def test_italic(self):
        node = TextNode("This is text with an _italic_ word", TextType.TEXT)
        result = split_nodes_delimiter([node], "_", TextType.ITALIC)
        self.assertEqual(
            result,
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word", TextType.TEXT),
            ],
        )

    def test_delimiter_at_start(self):
        node = TextNode("`code` at the start", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            result,
            [
                TextNode("code", TextType.CODE),
                TextNode(" at the start", TextType.TEXT),
            ],
        )

    def test_delimiter_at_end(self):
        node = TextNode("ends with **bold**", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            result,
            [
                TextNode("ends with ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
            ],
        )

    def test_multiple_delimiters_same_type(self):
        node = TextNode("`one` and `two` code blocks", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            result,
            [
                TextNode("one", TextType.CODE),
                TextNode(" and ", TextType.TEXT),
                TextNode("two", TextType.CODE),
                TextNode(" code blocks", TextType.TEXT),
            ],
        )

    def test_no_delimiter_in_text(self):
        node = TextNode("plain text with no delimiter", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            result,
            [
                TextNode("plain text with no delimiter", TextType.TEXT),
            ],
        )

    def test_non_text_node_passes_through(self):
        """Bold/italic/etc. nodes must be left untouched."""
        node = TextNode("already bold", TextType.BOLD)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(result, [TextNode("already bold", TextType.BOLD)])

    def test_mixed_list(self):
        """Plain text and already-typed nodes can coexist in the input list."""
        nodes = [
            TextNode("Hello `world`", TextType.TEXT),
            TextNode("skip me", TextType.BOLD),
        ]
        result = split_nodes_delimiter(nodes, "`", TextType.CODE)
        self.assertEqual(
            result,
            [
                TextNode("Hello ", TextType.TEXT),
                TextNode("world", TextType.CODE),
                TextNode("skip me", TextType.BOLD),
            ],
        )

    def test_chained_calls_for_different_types(self):
        """Calling the function twice handles two different delimiter types."""
        node = TextNode("**bold** and `code`", TextType.TEXT)
        after_bold = split_nodes_delimiter([node], "**", TextType.BOLD)
        after_code = split_nodes_delimiter(after_bold, "`", TextType.CODE)
        self.assertEqual(
            after_code,
            [
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("code", TextType.CODE),
            ],
        )

    def test_unclosed_delimiter_raises(self):
        node = TextNode("oops `unclosed code", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", TextType.CODE)


class TestExtractMarkdownImages(unittest.TestCase):
    def test_single_image(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_multiple_images(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        matches = extract_markdown_images(text)
        self.assertListEqual(
            [
                ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
                ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
            ],
            matches,
        )

    def test_no_images(self):
        matches = extract_markdown_images("Just plain text with no images.")
        self.assertListEqual([], matches)

    def test_empty_string(self):
        matches = extract_markdown_images("")
        self.assertListEqual([], matches)

    def test_empty_alt_text(self):
        matches = extract_markdown_images("![](https://i.imgur.com/zjjcJKZ.png)")
        self.assertListEqual([("", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_image_at_start_of_text(self):
        matches = extract_markdown_images(
            "![logo](https://example.com/logo.png) followed by text"
        )
        self.assertListEqual([("logo", "https://example.com/logo.png")], matches)

    def test_image_at_end_of_text(self):
        matches = extract_markdown_images(
            "Some text then ![logo](https://example.com/logo.png)"
        )
        self.assertListEqual([("logo", "https://example.com/logo.png")], matches)

    def test_does_not_match_plain_links(self):
        # A plain link (no !) should not be captured as an image
        matches = extract_markdown_images("[not an image](https://example.com)")
        self.assertListEqual([], matches)

    def test_image_alt_text_with_spaces(self):
        matches = extract_markdown_images(
            "![my cool image](https://example.com/img.png)"
        )
        self.assertListEqual(
            [("my cool image", "https://example.com/img.png")], matches
        )

    def test_url_with_query_string(self):
        matches = extract_markdown_images(
            "![chart](https://example.com/img.png?size=large&fmt=webp)"
        )
        self.assertListEqual(
            [("chart", "https://example.com/img.png?size=large&fmt=webp")], matches
        )

    def test_mixed_images_and_links(self):
        # Links should not be captured, only images
        text = (
            "A [link](https://example.com) and an ![image](https://example.com/img.png)"
        )
        matches = extract_markdown_images(text)
        self.assertListEqual([("image", "https://example.com/img.png")], matches)


class TestExtractMarkdownLinks(unittest.TestCase):
    def test_single_link(self):
        matches = extract_markdown_links(
            "This is text with a link [to boot dev](https://www.boot.dev)"
        )
        self.assertListEqual([("to boot dev", "https://www.boot.dev")], matches)

    def test_multiple_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        matches = extract_markdown_links(text)
        self.assertListEqual(
            [
                ("to boot dev", "https://www.boot.dev"),
                ("to youtube", "https://www.youtube.com/@bootdotdev"),
            ],
            matches,
        )

    def test_no_links(self):
        matches = extract_markdown_links("Just plain text with no links.")
        self.assertListEqual([], matches)

    def test_empty_string(self):
        matches = extract_markdown_links("")
        self.assertListEqual([], matches)

    def test_empty_anchor_text(self):
        matches = extract_markdown_links("[](https://example.com)")
        self.assertListEqual([("", "https://example.com")], matches)

    def test_link_at_start_of_text(self):
        matches = extract_markdown_links("[click here](https://example.com) for more")
        self.assertListEqual([("click here", "https://example.com")], matches)

    def test_link_at_end_of_text(self):
        matches = extract_markdown_links("See also [this page](https://example.com)")
        self.assertListEqual([("this page", "https://example.com")], matches)

    def test_does_not_match_images(self):
        # Image syntax (with !) should not be captured as a link
        matches = extract_markdown_links("![image](https://example.com/img.png)")
        self.assertListEqual([], matches)

    def test_url_with_query_string(self):
        matches = extract_markdown_links(
            "[search](https://example.com/search?q=hello&page=2)"
        )
        self.assertListEqual(
            [("search", "https://example.com/search?q=hello&page=2")], matches
        )

    def test_mixed_images_and_links(self):
        # Images should not be captured, only links
        text = (
            "A [link](https://example.com) and an ![image](https://example.com/img.png)"
        )
        matches = extract_markdown_links(text)
        self.assertListEqual([("link", "https://example.com")], matches)

    def test_anchor_text_with_spaces(self):
        matches = extract_markdown_links("[visit our homepage](https://example.com)")
        self.assertListEqual([("visit our homepage", "https://example.com")], matches)


if __name__ == "__main__":
    unittest.main()
