import unittest

from inline import text_to_textnodes
from textnode import TextNode, TextType, text_node_to_html_node


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.TEXT)
        node2 = TextNode("This is a text node", TextType.TEXT)
        self.assertEqual(node, node2)
        node = TextNode("This is a bold text node", TextType.BOLD)
        node2 = TextNode("This is a bold text node", TextType.BOLD)
        self.assertEqual(node, node2)
        node = TextNode("This is a italic text node", TextType.ITALIC)
        node2 = TextNode("This is a italic text node", TextType.ITALIC)
        self.assertEqual(node, node2)
        node = TextNode("This is a code text node", TextType.CODE)
        node2 = TextNode("This is a code text node", TextType.CODE)
        self.assertEqual(node, node2)
        node = TextNode("This is a link text node", TextType.LINK, "https://link.com")
        node2 = TextNode("This is a link text node", TextType.LINK, "https://link.com")
        self.assertEqual(node, node2)
        node = TextNode("This is a image text node", TextType.IMAGE, "image.png")
        node2 = TextNode("This is a image text node", TextType.IMAGE, "image.png")
        self.assertEqual(node, node2)

    def test_not_eq(self):
        node = TextNode("This is a text node", TextType.TEXT)
        node2 = TextNode("This is a different node", TextType.TEXT)
        self.assertNotEqual(node, node2)
        node2 = TextNode("This is a text node", TextType.TEXT, url="https://link.com")
        self.assertNotEqual(node, node2)
        node2 = TextNode("This is a bold text node", TextType.BOLD)
        self.assertNotEqual(node, node2)
        node2 = TextNode("This is a italic text node", TextType.ITALIC)
        self.assertNotEqual(node, node2)
        node2 = TextNode("This is a code text node", TextType.CODE)
        self.assertNotEqual(node, node2)
        node2 = TextNode("This is a link text node", TextType.LINK, "https://link.com")
        self.assertNotEqual(node, node2)
        node2 = TextNode("This is a image text node", TextType.IMAGE, "image.png")
        self.assertNotEqual(node, node2)

    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")


class TestTextToTextNodes(unittest.TestCase):
    def test_all_types(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode(
                    "obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"
                ),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            nodes,
        )

    def test_plain_text(self):
        nodes = text_to_textnodes("Just plain text.")
        self.assertListEqual(
            [TextNode("Just plain text.", TextType.TEXT)],
            nodes,
        )

    def test_bold_only(self):
        nodes = text_to_textnodes("**bold**")
        self.assertListEqual(
            [TextNode("bold", TextType.BOLD)],
            nodes,
        )

    def test_italic_only(self):
        nodes = text_to_textnodes("_italic_")
        self.assertListEqual(
            [TextNode("italic", TextType.ITALIC)],
            nodes,
        )

    def test_code_only(self):
        nodes = text_to_textnodes("`code`")
        self.assertListEqual(
            [TextNode("code", TextType.CODE)],
            nodes,
        )

    def test_image_only(self):
        nodes = text_to_textnodes("![alt](https://example.com/img.png)")
        self.assertListEqual(
            [TextNode("alt", TextType.IMAGE, "https://example.com/img.png")],
            nodes,
        )

    def test_link_only(self):
        nodes = text_to_textnodes("[click](https://example.com)")
        self.assertListEqual(
            [TextNode("click", TextType.LINK, "https://example.com")],
            nodes,
        )

    def test_bold_and_italic(self):
        nodes = text_to_textnodes("**bold** and _italic_")
        self.assertListEqual(
            [
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
            ],
            nodes,
        )

    def test_multiple_of_same_type(self):
        nodes = text_to_textnodes("`one` and `two`")
        self.assertListEqual(
            [
                TextNode("one", TextType.CODE),
                TextNode(" and ", TextType.TEXT),
                TextNode("two", TextType.CODE),
            ],
            nodes,
        )

    def test_image_and_link(self):
        nodes = text_to_textnodes(
            "![img](https://example.com/img.png) and [link](https://example.com)"
        )
        self.assertListEqual(
            [
                TextNode("img", TextType.IMAGE, "https://example.com/img.png"),
                TextNode(" and ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://example.com"),
            ],
            nodes,
        )

    def test_no_empty_text_nodes(self):
        # The result should contain no TextNodes with empty text
        nodes = text_to_textnodes("**bold**")
        for node in nodes:
            self.assertNotEqual(node.text, "")

    def test_unclosed_delimiter_raises(self):
        with self.assertRaises(ValueError):
            text_to_textnodes("oops **unclosed bold")


if __name__ == "__main__":
    unittest.main()
