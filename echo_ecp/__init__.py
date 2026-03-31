"""
echo-ecp: Echo Convergence Protocol
Governed multi-perspective reasoning engine.
Zero external dependencies.

Nathan Poinsette (∇θ Operator) | Echo Universe
"""

from .echo_system_v4 import ECPEngine, run_convergence

__version__ = "4.0.0"
__author__ = "Nathan Poinsette"
__all__ = ["ECPEngine", "run_convergence", "__version__"]


def main():
    """CLI entry point."""
    import sys
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = input("Enter question for ECP: ")
    result = run_convergence(question)
    print(result)
