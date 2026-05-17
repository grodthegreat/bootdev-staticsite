import shutil
import sys
from pathlib import Path

from blocks import extract_title, markdown_to_html_node


def generate_page(
    from_path: Path, template_path: Path, dest_path: Path, basepath: str
) -> None:
    """Generates an HTML file from a markdown file using a template."""
    print(
        f"Generating page from {from_path} to {dest_path} using {template_path} with basepath {basepath}"
    )

    # Read markdown and template content
    with open(from_path, "r", encoding="utf-8") as f:
        markdown_content = f.read()

    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    # Convert Markdown structure into clean HTML output
    html_node = markdown_to_html_node(markdown_content)
    html_content = html_node.to_html()

    # Pull the document header text
    title = extract_title(markdown_content)

    # Inject the payload data into the HTML wrapper
    final_html = template_content.replace("{{ Title }}", title).replace(
        "{{ Content }}", html_content
    )

    # Adjust absolute root links to match our configured base path environment
    final_html = final_html.replace('href="/', f'href="{basepath}')
    final_html = final_html.replace('src="/', f'src="{basepath}')

    # Make certain destination directories match up safely
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(final_html)


def generate_pages_recursive(
    dir_path_content: str, template_path: str, dest_dir_path: str, basepath: str
) -> None:
    """Recursively crawls the content directory and generates HTML pages in the destination directory."""
    content_path = Path(dir_path_content)
    template_file = Path(template_path)
    dest_path = Path(dest_dir_path)

    if not content_path.exists():
        raise ValueError(f"Content directory does not exist: {dir_path_content}")

    # Iterate through all files and directories recursively
    for entry in content_path.iterdir():
        if entry.is_dir():
            # Calculate the corresponding nested directory path in target output location
            new_dest_dir = dest_path / entry.name
            generate_pages_recursive(
                str(entry), template_path, str(new_dest_dir), basepath
            )
        elif entry.is_file() and entry.suffix == ".md":
            # Calculate the destination file path, switching .md extension to .html
            new_dest_file = dest_path / f"{entry.stem}.html"
            generate_page(entry, template_file, new_dest_file, basepath)


def main() -> None:
    # Safely look for basepath CLI argument string, fallback to root context "/"
    basepath = "/"
    if len(sys.argv) > 1:
        basepath = sys.argv[1]

    # 1. Clear out target production directory (now 'docs') and sync assets
    root = Path().parent.resolve()
    docs = Path(root / "docs").resolve()

    if docs.exists():
        if docs.is_file():
            docs.unlink()
        if docs.is_dir():
            shutil.rmtree(docs)
    docs.mkdir(exist_ok=True)

    static = Path(root / "static").resolve()
    if static.exists() and static.is_dir():
        for item in static.iterdir():
            dest = docs / item.name
            if item.is_file():
                shutil.copy2(item.resolve(), dest)
            if item.is_dir():
                shutil.copytree(item.resolve(), dest)

    # 2. Recursively generate all pages from the content folder into 'docs'
    generate_pages_recursive("content", "template.html", "docs", basepath)


if __name__ == "__main__":
    main()
