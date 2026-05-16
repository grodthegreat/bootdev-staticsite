import re
from enum import Enum


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered list"
    ORDERED_LIST = "ordered list"


def block_to_block_type(markdown: str) -> BlockType:
    if re.match(r"^#{1,6} \w+", markdown):
        return BlockType.HEADING
    lines = markdown.split("\n")
    if re.match("^```", lines[0]) and re.match("```$", lines[-1]):
        return BlockType.CODE
    is_quote = True
    for line in lines:
        is_quote = re.match("^> ?.*", line) and is_quote
    if is_quote:
        return BlockType.QUOTE
    is_unordered = True
    for line in lines:
        is_unordered = re.match("^- .*", line) and is_unordered
    if is_unordered:
        return BlockType.UNORDERED_LIST
    is_ordered = True
    for i in range(len(lines)):
        is_ordered = re.match(f"^{i + 1}\. .*", lines[i]) and is_ordered
    if is_ordered:
        return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH
