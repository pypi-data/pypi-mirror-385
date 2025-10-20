"""Context window validation utilities for Arbitrium Framework.

This module provides functions to validate prompt sizes against model context windows
before making API calls, preventing context overflow errors.
"""

from typing import Any

import litellm

from .constants import DEFAULT_CONTEXT_SAFETY_MARGIN


def _process_inline_token(token: Any, plain_parts: list[str]) -> None:
    """Process an inline token and add to plain parts."""
    if token.children:
        for child in token.children:
            if child.type == "text":
                plain_parts.append(child.content)
            elif child.type == "code_inline":
                plain_parts.append(child.content)
            elif child.type in ["link_open", "link_close"]:
                continue
    else:
        plain_parts.append(token.content)


def _process_code_block(token: Any, plain_parts: list[str]) -> None:
    """Process a code block token and add to plain parts."""
    plain_parts.append("\n")
    plain_parts.append(token.content)
    plain_parts.append("\n")


def _process_structural_token(token: Any, plain_parts: list[str]) -> None:
    """Process structural tokens (headings, paragraphs, lists, breaks)."""
    if token.type in [
        "heading_open",
        "heading_close",
        "paragraph_open",
        "paragraph_close",
        "bullet_list_open",
        "bullet_list_close",
        "ordered_list_open",
        "ordered_list_close",
        "softbreak",
        "hardbreak",
    ]:
        plain_parts.append("\n")


def _extract_text_from_tokens(tokens: Any, plain_parts: list[str]) -> None:
    """Recursively extract text from markdown tokens."""
    for token in tokens:
        if token.type == "inline":
            _process_inline_token(token, plain_parts)
        elif token.type in ["code_block", "fence"]:
            _process_code_block(token, plain_parts)
        else:
            _process_structural_token(token, plain_parts)

        # Recursively process children
        if token.children:
            _extract_text_from_tokens(token.children, plain_parts)


def markdown_to_plain_text(text: str) -> str:
    """Convert markdown to plain text to reduce token count.

    Removes all markdown formatting (bold, italic, headers, links, etc.)
    while preserving the actual content, including formulas and code.

    Args:
        text: The markdown text to convert

    Returns:
        Plain text version with formatting removed
    """
    import logging
    import re

    from markdown_it import MarkdownIt

    # Disable markdown_it debug logging
    logging.getLogger("markdown_it").setLevel(logging.WARNING)

    # Parse markdown and render to tokens
    md = MarkdownIt()
    tokens = md.parse(text)

    # Extract plain text from tokens
    plain_parts: list[str] = []
    _extract_text_from_tokens(tokens, plain_parts)
    result = "".join(plain_parts)

    # Clean up excessive whitespace
    result = re.sub(r"\n\n+", "\n\n", result)  # Max 2 newlines
    result = re.sub(r" +", " ", result)  # Collapse spaces

    return result.strip()


def estimate_token_count(text: str, model_name: str) -> int:
    """Estimate the number of tokens in text for a given model.

    Args:
        text: The text to count tokens for
        model_name: The model name for tokenizer selection

    Returns:
        Estimated token count

    Raises:
        ValueError: If tokenization fails
    """
    count: int = litellm.token_counter(model=model_name, text=text)
    return count


def validate_prompt_size(
    prompt: str,
    model_name: str,
    context_window: int,
    max_tokens: int = 4000,
    safety_margin: float = DEFAULT_CONTEXT_SAFETY_MARGIN,
) -> tuple[bool, int, str]:
    """Validate that a prompt will fit within the model's context window.

    Args:
        prompt: The prompt text to validate
        model_name: The model name for tokenizer selection
        context_window: The model's context window size
        max_tokens: Maximum tokens reserved for response
        safety_margin: Safety margin as fraction of context window (0.1 = 10%)

    Returns:
        Tuple of (is_valid, token_count, message)
    """
    token_count = estimate_token_count(prompt, model_name)

    # Calculate available space
    safety_tokens = int(context_window * safety_margin)
    available_tokens = context_window - max_tokens - safety_tokens

    if token_count <= available_tokens:
        return (
            True,
            token_count,
            f"Prompt fits within context window ({token_count}/{available_tokens} tokens)",
        )
    else:
        excess_tokens = token_count - available_tokens
        return (
            False,
            token_count,
            (
                f"Prompt exceeds context window by {excess_tokens} tokens ({token_count}/{available_tokens} available)"
            ),
        )
