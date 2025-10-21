from .windows import parse_windows
from .macos import parse_macos
from .linux import parse_linux
from .mobile import parse_mobile
from .bsd import parse_bsd
from .network import parse_network

__all__ = [
    "parse_bsd",
    "parse_linux",
    "parse_macos",
    "parse_mobile",
    "parse_network",
    "parse_windows",
]
