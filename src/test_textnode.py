import unittest

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


if __name__ == "__main__":
    unittest.main()
