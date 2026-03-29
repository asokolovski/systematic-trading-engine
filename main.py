"""
Runnable project demo entrypoint.

Example:
    python3 main.py
"""

from __future__ import annotations

from runners.paper_trading_runner import run as run_paper_trading
from runners.research_runner import run


def prompt_for_mode() -> str:
    """
    Let the user choose between the research and paper-trading demos.
    """

    print("Available demos:")
    print("  1. Phase 1 Research Backtester")
    print("  2. Phase 2 Paper Trading")

    while True:
        choice = input("Choose a demo by number [1]: ").strip() or "1"
        if choice in {"1", "2"}:
            return choice
        print("Invalid selection. Please choose 1 or 2.")


def main() -> None:
    """
    Launch one of the project demo runners.
    """

    choice = prompt_for_mode()
    if choice == "1":
        run()
        return

    run_paper_trading()


if __name__ == "__main__":
    main()
