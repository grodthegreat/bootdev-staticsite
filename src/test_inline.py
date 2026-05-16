import unittest

from inline import (
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_delimiter,
    split_nodes_image,
    split_nodes_link,
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


class TestSplitNodesImage(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_single_image(self):
        node = TextNode(
            "Before ![alt](https://example.com/img.png) after",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("Before ", TextType.TEXT),
                TextNode("alt", TextType.IMAGE, "https://example.com/img.png"),
                TextNode(" after", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_image_at_start(self):
        node = TextNode(
            "![logo](https://example.com/logo.png) then text",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("logo", TextType.IMAGE, "https://example.com/logo.png"),
                TextNode(" then text", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_image_at_end(self):
        node = TextNode(
            "Some text then ![logo](https://example.com/logo.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("Some text then ", TextType.TEXT),
                TextNode("logo", TextType.IMAGE, "https://example.com/logo.png"),
            ],
            new_nodes,
        )

    def test_image_only(self):
        # No surrounding text — no empty TextNodes should appear
        node = TextNode(
            "![solo](https://example.com/solo.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [TextNode("solo", TextType.IMAGE, "https://example.com/solo.png")],
            new_nodes,
        )

    def test_no_images(self):
        # Node with no images passes through unchanged
        node = TextNode("Plain text with no images.", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([node], new_nodes)

    def test_non_text_node_passes_through(self):
        # Already-typed nodes are not processed
        node = TextNode("already bold", TextType.BOLD)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([node], new_nodes)

    def test_mixed_input_list(self):
        nodes = [
            TextNode("![img](https://example.com/a.png) text", TextType.TEXT),
            TextNode("skip me", TextType.BOLD),
        ]
        new_nodes = split_nodes_image(nodes)
        self.assertListEqual(
            [
                TextNode("img", TextType.IMAGE, "https://example.com/a.png"),
                TextNode(" text", TextType.TEXT),
                TextNode("skip me", TextType.BOLD),
            ],
            new_nodes,
        )

    def test_does_not_split_on_links(self):
        # A plain link should not produce an IMAGE node
        node = TextNode("A [link](https://example.com) here.", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([node], new_nodes)

    def test_consecutive_images_no_text_between(self):
        node = TextNode(
            "![a](https://example.com/a.png)![b](https://example.com/b.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("a", TextType.IMAGE, "https://example.com/a.png"),
                TextNode("b", TextType.IMAGE, "https://example.com/b.png"),
            ],
            new_nodes,
        )


class TestSplitNodesLink(unittest.TestCase):
    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode(
                    "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
                ),
            ],
            new_nodes,
        )

    def test_single_link(self):
        node = TextNode(
            "Before [click here](https://example.com) after",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("Before ", TextType.TEXT),
                TextNode("click here", TextType.LINK, "https://example.com"),
                TextNode(" after", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_link_at_start(self):
        node = TextNode(
            "[click](https://example.com) then text",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("click", TextType.LINK, "https://example.com"),
                TextNode(" then text", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_link_at_end(self):
        node = TextNode(
            "Some text then [click](https://example.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("Some text then ", TextType.TEXT),
                TextNode("click", TextType.LINK, "https://example.com"),
            ],
            new_nodes,
        )

    def test_link_only(self):
        node = TextNode("[solo](https://example.com)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [TextNode("solo", TextType.LINK, "https://example.com")],
            new_nodes,
        )

    def test_no_links(self):
        node = TextNode("Plain text with no links.", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual([node], new_nodes)

    def test_non_text_node_passes_through(self):
        node = TextNode("already italic", TextType.ITALIC)
        new_nodes = split_nodes_link([node])
        self.assertListEqual([node], new_nodes)

    def test_mixed_input_list(self):
        nodes = [
            TextNode("[link](https://example.com) text", TextType.TEXT),
            TextNode("skip me", TextType.CODE),
        ]
        new_nodes = split_nodes_link(nodes)
        self.assertListEqual(
            [
                TextNode("link", TextType.LINK, "https://example.com"),
                TextNode(" text", TextType.TEXT),
                TextNode("skip me", TextType.CODE),
            ],
            new_nodes,
        )

    def test_does_not_split_on_images(self):
        # An image should not produce a LINK node
        node = TextNode("An ![image](https://example.com/img.png) here.", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual([node], new_nodes)

    def test_consecutive_links_no_text_between(self):
        node = TextNode(
            "[a](https://example.com/a)[b](https://example.com/b)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("a", TextType.LINK, "https://example.com/a"),
                TextNode("b", TextType.LINK, "https://example.com/b"),
            ],
            new_nodes,
        )

    def test_link_url_with_query_string(self):
        node = TextNode(
            "[search](https://example.com/search?q=hello&page=2)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode(
                    "search",
                    TextType.LINK,
                    "https://example.com/search?q=hello&page=2",
                )
            ],
            new_nodes,
        )


if __name__ == "__main__":
    unittest.main()
