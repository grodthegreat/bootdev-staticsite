import re

from textnode import TextNode, TextType


def split_nodes_delimiter(
    old_nodes: list[TextNode],
    delimiter: str,
    text_type: TextType,
) -> list[TextNode]:
    new_nodes: list[TextNode] = []

    for node in old_nodes:
        # Non-TEXT nodes pass through unchanged
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        parts = node.text.split(delimiter)

        # An even number of parts means an unclosed delimiter
        if len(parts) % 2 == 0:
            raise ValueError(
                f"Invalid Markdown: unclosed delimiter '{delimiter}' in: {node.text!r}"
            )

        for i, part in enumerate(parts):
            if part == "":
                continue
            # Even indices are plain text, odd indices are inside the delimiter
            if i % 2 == 0:
                new_nodes.append(TextNode(part, TextType.TEXT))
            else:
                new_nodes.append(TextNode(part, text_type))

    return new_nodes


def extract_markdown_images(text: str) -> list[tuple[str, str]]:
    matches = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches


def extract_markdown_links(text: str) -> list[tuple[str, str]]:
    matches = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches


def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes: list[TextNode] = []
    for node in old_nodes:
        text = node.text
        matches = extract_markdown_images(text)
        for match in matches:
            parts = text.split(f"![{match[0]}]({match[1]})", maxsplit=1)
            if parts[0] != "":
                new_nodes.append(TextNode(parts[0], node.text_type))
            new_nodes.append(TextNode(match[0], TextType.IMAGE, match[1]))
            text = parts[1]
        if text != "":
            new_nodes.append(TextNode(text, node.text_type))
    return new_nodes


def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes: list[TextNode] = []
    for node in old_nodes:
        text = node.text
        matches = extract_markdown_links(text)
        for match in matches:
            parts = text.split(f"[{match[0]}]({match[1]})", maxsplit=1)
            if parts[0] != "":
                new_nodes.append(TextNode(parts[0], node.text_type))
            new_nodes.append(TextNode(match[0], TextType.LINK, match[1]))
            text = parts[1]
        if text != "":
            new_nodes.append(TextNode(text, node.text_type))
    return new_nodes
