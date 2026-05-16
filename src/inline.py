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
