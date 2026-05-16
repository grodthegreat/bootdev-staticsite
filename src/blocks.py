def markdown_to_blocks(markdown: str) -> list[str]:
    return list(
        filter(
            lambda line: line != "",
            list(
                map(
                    lambda line: line.strip(),
                    markdown.split("\n\n"),
                )
            ),
        )
    )
