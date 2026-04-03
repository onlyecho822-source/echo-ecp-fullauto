"""
echo-ecp — Entry point for `python -m echo_ecp`

Usage:
    python -m echo_ecp "Your claim or question here"
    python -m echo_ecp "Your claim" --flow Research
    python -m echo_ecp "Your claim" --flow Legal --format json

Install:
    pip install echo-ecp

Docs:
    https://github.com/onlyecho822-source/echo-ecp-fullauto
"""
import sys
from .cli import main

if __name__ == "__main__":
    main()
