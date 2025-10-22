"""
Aethermark - High-Performance Markdown Processing with Pybind11

Aethermark is a blazing-fast Markdown parser and renderer built with pybind11,
introducing Aethermark-Flavored Markdown (AFM) - a powerful extension to
CommonMark that combines rigorous standards compliance with enhanced features.

Key Features:
───────────────────────────────────────────────────────────────────────────────
• Optimized Performance: C++ core with Python bindings delivers 5-10x faster
  parsing than pure Python implementations
• AFM Dialect: Extends CommonMark with thoughtful syntax enhancements while
  maintaining full backward compatibility
• Extensible Architecture: Plugin system for custom syntax, renderers, and
  post-processors
• Precision Rendering: AST-based processing guarantees consistent,
  standards-compliant output
• Modern Tooling: Full type hints, comprehensive docs, and IDE support

Example Usage:
───────────────────────────────────────────────────────────────────────────────
>>> import aethermark
>>> md = aethermark.AFMParser()
>>> html = md.render("**AFM** adds _native_ syntax extensions!")
>>> print(html)
<p><strong>AFM</strong> adds <em>native</em> syntax extensions!</p>

Advanced Features:
───────────────────────────────────────────────────────────────────────────────
• Direct AST manipulation for programmatic document construction
• Source mapping for accurate error reporting
• Custom render targets (HTML, LaTeX, etc.)
• Thread-safe batch processing

Why Aethermark?
───────────────────────────────────────────────────────────────────────────────
For projects requiring:
• Scientific/technical documentation with complex markup needs
• High-volume Markdown processing
• Custom Markdown extensions without compromising performance
• Perfect round-trip parsing/render cycles

Learn more at: https://github.com/aethermark/aethermark
"""

def greet(name: str) -> str:
    """
    Greet someone by name.

    Args:
        name (str): Name of the person.

    Returns:
        str: Greeting string.
    """
    ...
