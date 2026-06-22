#!/usr/bin/env python3
"""
PayWallet support bot.

Usage:
  python bot.py --customer cust_001 --question "how do I freeze my card?"
  python bot.py --all
"""
import argparse
import pathlib
import sys

from customer import get_safe
from llm import StubLLM
from router import route

QUESTIONS_FILE = pathlib.Path(__file__).parent / "materials" / "questions.txt"
_llm = StubLLM()


def answer(customer_id: str, question: str) -> dict:
    """Core pipeline: load safe data → route → generate reply."""
    customer = get_safe(customer_id)          # restricted fields never loaded here
    lane, topic = route(question, customer)
    reply = _llm.complete(lane, topic, customer, question)
    return {"lane": lane, "topic": topic, "reply": reply}


def _parse_questions() -> list[tuple[str, str]]:
    pairs = []
    for line in QUESTIONS_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        cid, q = [p.strip() for p in line.split("|", 1)]
        pairs.append((cid, q))
    return pairs


def main() -> None:
    parser = argparse.ArgumentParser(description="PayWallet support bot")
    parser.add_argument("--customer", metavar="ID", help="Customer ID")
    parser.add_argument("--question", metavar="Q", help="Question to answer")
    parser.add_argument("--all", action="store_true", help="Run every question in questions.txt")
    args = parser.parse_args()

    if args.all:
        for cid, q in _parse_questions():
            result = answer(cid, q)
            print(f"\n{'─'*60}")
            print(f"[{cid}] {q}")
            print(f"Lane : {result['lane']} / {result['topic']}")
            print(f"Reply: {result['reply']}")
        print(f"\n{'─'*60}")
    elif args.customer and args.question:
        result = answer(args.customer, args.question)
        print(f"Lane : {result['lane']} / {result['topic']}")
        print(f"Reply: {result['reply']}")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
