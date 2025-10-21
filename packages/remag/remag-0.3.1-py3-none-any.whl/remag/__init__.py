"""
REMAG: Recovery of eukaryotic genomes using contrastive learning
"""

try:
    from ._version import __version__
except ImportError:
    # Fallback for Bioconda/conda installations without git
    __version__ = "0.2.5"

__author__ = "Daniel Gómez-Pérez"
__email__ = "daniel.gomez-perez@earlham.ac.uk"

try:
    from .core import main
    from .cli import main_cli

    __all__ = ["main", "main_cli"]
except ImportError:
    __all__ = []
