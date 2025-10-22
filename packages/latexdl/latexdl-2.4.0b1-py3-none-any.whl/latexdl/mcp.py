from __future__ import annotations

import os
import re
import xml.etree.ElementTree as ET
from typing import Annotated, Any

from fastmcp import FastMCP

from .main import convert_arxiv_latex

mcp = FastMCP("latexdl")

# Environment variables:
# - ARXIV_FALLBACK_TO_LATEX: Enable/disable fallback to LaTeX when markdown conversion fails (default: "true")


async def _robust_download_paper(arxiv_id: str) -> str:
    """Download paper with robust fallback behavior.

    Tries to convert to markdown first, falls back to LaTeX if markdown conversion fails
    and fallback is enabled via environment variable.

    Args:
        arxiv_id: The arXiv ID of the paper to download

    Returns:
        The paper content (markdown if successful, LaTeX if fallback enabled)

    Raises:
        Exception: If both markdown and LaTeX downloads fail, or if fallback is disabled
    """
    try:
        # First, try to convert to markdown
        content, metadata = convert_arxiv_latex(
            arxiv_id,
            markdown=True,
            include_bibliography=True,
            include_metadata=True,
            use_cache=True,
        )
        return content
    except Exception as markdown_error:
        # If markdown conversion fails and fallback is enabled, try LaTeX
        if os.getenv("ARXIV_FALLBACK_TO_LATEX", "true").lower() in (
            "true",
            "1",
            "yes",
            "on",
        ):
            try:
                content, metadata = convert_arxiv_latex(
                    arxiv_id,
                    markdown=False,  # Get raw LaTeX
                    include_bibliography=True,
                    include_metadata=True,
                    use_cache=True,
                )
                return content
            except Exception as latex_error:
                # Both conversions failed
                raise Exception(
                    f"Both markdown and LaTeX conversion failed. "
                    f"Markdown error: {markdown_error}. LaTeX error: {latex_error}"
                )
        else:
            # Fallback is disabled, re-raise the original markdown error
            raise markdown_error


def _parse_markdown_hierarchy(markdown_text: str) -> list[dict[str, Any]]:
    """Parse markdown headings into a hierarchical structure.

    Args:
        markdown_text: The markdown content to parse

    Returns:
        A list of root-level sections, each with potential nested children
    """
    # Extract all heading lines with their levels
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    headings = [
        {"level": len(match.group(1)), "title": match.group(2).strip()}
        for match in heading_pattern.finditer(markdown_text)
    ]

    if not headings:
        return []

    # Build hierarchical structure
    root: list[dict[str, Any]] = []
    stack: list[dict[str, Any]] = []

    for heading in headings:
        node = {
            "level": heading["level"],
            "title": heading["title"],
            "children": [],
        }

        # Find the correct parent by popping from stack until we find appropriate level
        while stack and stack[-1]["level"] >= heading["level"]:
            stack.pop()

        if not stack:
            # This is a root-level heading
            root.append(node)
        else:
            # Add as child of the last item in stack
            stack[-1]["children"].append(node)

        stack.append(node)

    return root


def _tree_to_xml(tree: list[dict[str, Any]], arxiv_id: str) -> str:
    """Convert hierarchical structure to XML string.

    Args:
        tree: The hierarchical section structure
        arxiv_id: The arXiv ID of the paper

    Returns:
        XML string representation of the structure
    """
    root = ET.Element("paper")
    root.set("arxiv_id", arxiv_id)

    def add_sections(parent_elem: ET.Element, sections: list[dict[str, Any]]) -> None:
        for section in sections:
            section_elem = ET.SubElement(parent_elem, "section")
            section_elem.set("level", str(section["level"]))
            section_elem.set("title", section["title"])

            if section["children"]:
                add_sections(section_elem, section["children"])

    add_sections(root, tree)

    # Convert to string with pretty formatting
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="unicode", xml_declaration=True)


@mcp.tool(
    name="download_paper_content",
    description="Download and extract the full text content of an arXiv paper given its ID.",
)
async def download_paper_content(
    arxiv_id: Annotated[str, "ArXiv paper ID (e.g., '2103.12345' or '2103.12345v1')"],
) -> str:
    """Download the full content of an arXiv paper.

    Args:
        arxiv_id: The arXiv ID of the paper to download

    Returns:
        The full text content of the paper (markdown if possible, LaTeX if fallback enabled)
    """
    try:
        return await _robust_download_paper(arxiv_id)
    except Exception as e:
        return f"Error downloading paper {arxiv_id}: {str(e)}"


@mcp.tool(
    name="get_paper_structure",
    description="Extract the hierarchical section structure of an arXiv paper as XML. Only works for papers that can be converted to markdown.",
)
async def get_paper_structure(
    arxiv_id: Annotated[str, "ArXiv paper ID (e.g., '2103.12345' or '2103.12345v1')"],
) -> str:
    """Get the hierarchical section structure of a paper as XML.

    This tool downloads the paper, converts it to markdown, and extracts
    the heading hierarchy without the actual content text.

    Args:
        arxiv_id: The arXiv ID of the paper

    Returns:
        XML representation of the paper's section structure
    """
    try:
        # Download as markdown (no fallback to LaTeX since we need markdown structure)
        content, metadata = convert_arxiv_latex(
            arxiv_id,
            markdown=True,
            include_bibliography=True,
            include_metadata=True,
            use_cache=True,
        )

        # Parse the hierarchy
        tree = _parse_markdown_hierarchy(content)

        # Convert to XML
        xml_str = _tree_to_xml(tree, arxiv_id)

        return xml_str

    except Exception as e:
        return f"Error extracting paper structure for {arxiv_id}: {str(e)}"


def main():
    mcp.run()


if __name__ == "__main__":
    main()
