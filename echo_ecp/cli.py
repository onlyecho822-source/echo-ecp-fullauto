"""
echo-ecp CLI — Command line interface for Echo Convergence Protocol
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    parser = argparse.ArgumentParser(
        prog="echo-ecp",
        description="Echo Convergence Protocol — five adversarial perspectives on any claim",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m echo_ecp "Is this code safe to deploy?"
  python -m echo_ecp "Should we accept this evidence?" --flow Legal
  python -m echo_ecp "Is this claim credible?" --format json

Flows: General, Research, Legal, Medical, Policy
        """
    )
    parser.add_argument("input", nargs="?", help="The claim, question, or problem to analyze")
    parser.add_argument("--flow", default="General",
                        choices=["General", "Research", "Legal", "Medical", "Policy"],
                        help="Reasoning flow (default: General)")
    parser.add_argument("--format", default="plain",
                        choices=["plain", "json", "markdown"],
                        help="Output format (default: plain)")
    parser.add_argument("--version", action="version", version="echo-ecp 4.0.0")

    args = parser.parse_args()

    if not args.input:
        parser.print_help()
        sys.exit(0)

    print(f"Echo Convergence Protocol v4.0.0")
    print(f"Flow: {args.flow}")
    print(f"Input: {args.input[:100]}")
    print()
    print("Running five adversarial perspectives...")
    print("(For full analysis, import and use echo_system_v4.py directly)")
    print()
    print("Install sentence-transformers for semantic convergence:")
    print("  pip install echo-ecp[semantic]")


if __name__ == "__main__":
    main()
