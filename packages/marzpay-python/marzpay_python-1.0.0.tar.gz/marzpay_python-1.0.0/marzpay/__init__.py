"""
MarzPay Python SDK

Official Python SDK for MarzPay - Mobile Money Payment Platform for Uganda.
"""

from .marzpay import MarzPay
from .errors import MarzPayError

__version__ = "1.0.0"
__author__ = "MarzPay Team"
__email__ = "dev@wearemarz.com"

__all__ = [
    "MarzPay",
    "MarzPayError",
]


