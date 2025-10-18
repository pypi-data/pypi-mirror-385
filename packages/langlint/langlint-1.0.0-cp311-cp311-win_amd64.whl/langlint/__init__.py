"""
LangLint - Intelligent translation management for code and documentation

This is the Python interface to the Rust-powered langlint library.
All heavy lifting is done in Rust for maximum performance.
"""

__version__ = "1.0.0"

# Import the Rust module
try:
    from langlint_py import scan, translate, version
    __all__ = ['scan', 'translate', 'version', '__version__']
except ImportError as e:
    # Fallback for development without maturin build
    import warnings
    warnings.warn(f"Failed to import Rust module: {e}. Please run 'maturin develop' first.")
    
    def scan(*args, **kwargs):
        raise RuntimeError("Rust module not built. Run 'maturin develop' first.")
    
    def translate(*args, **kwargs):
        raise RuntimeError("Rust module not built. Run 'maturin develop' first.")
    
    def version():
        return __version__


