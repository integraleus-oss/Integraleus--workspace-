#!/usr/bin/env python3
"""Contradiction Matrix lookup for the TRIZ skill.

Resolves a pair of the 39 engineering parameters to the recommended inventive
principles, with names — so the agent never has to hand-parse the JSON or risk
transposing the (asymmetric!) axes.

Usage:
    python scripts/matrix_lookup.py 9 10
    python scripts/matrix_lookup.py --improving 9 --worsening 10
    python scripts/matrix_lookup.py --find speed          # search parameter names
    python scripts/matrix_lookup.py --principle 15        # explain one principle
    python scripts/matrix_lookup.py --list                # all 39 parameters

Exit codes: 0 = found, 1 = empty cell (legitimate: 292 cells are empty), 2 = bad input.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MATRIX = ROOT / "references" / "contradiction_matrix.json"
PARAMS = ROOT / "references" / "39_parameters.md"
PRINCIPLES = ROOT / "references" / "40_principles.md"

ROW_RE = re.compile(r"^\|\s*(\d{1,2})\s*\|\s*([^|]+?)\s*\|")


def parse_table(path: Path, limit: int) -> dict[int, str]:
    """Read '| id | name | ... |' rows from a markdown table."""
    out: dict[int, str] = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        m = ROW_RE.match(line)
        if m:
            idx = int(m.group(1))
            if 1 <= idx <= limit and idx not in out:
                out[idx] = m.group(2).strip()
    return out


def load_matrix() -> dict:
    with MATRIX.open(encoding="utf-8") as fh:
        return json.load(fh)


def fmt_principles(ids: list[int], names: dict[int, str]) -> str:
    return "\n".join(f"  {i:>2}. {names.get(i, '(name unavailable)')}" for i in ids)


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True, description="TRIZ contradiction matrix lookup")
    ap.add_argument("pair", nargs="*", type=int, help="improving worsening (1-39 each)")
    ap.add_argument("--improving", "-i", type=int, help="improving parameter id (matrix row)")
    ap.add_argument("--worsening", "-w", type=int, help="worsening parameter id (matrix column)")
    ap.add_argument("--find", "-f", metavar="TEXT", help="search the 39 parameter names")
    ap.add_argument("--principle", "-p", type=int, metavar="ID", help="show one principle")
    ap.add_argument("--list", "-l", action="store_true", help="list all 39 parameters")
    args = ap.parse_args()

    params = parse_table(PARAMS, 39)
    principles = parse_table(PRINCIPLES, 40)

    if args.list:
        for i in sorted(params):
            print(f"{i:>2}. {params[i]}")
        return 0

    if args.find:
        needle = args.find.lower()
        hits = [(i, n) for i, n in sorted(params.items()) if needle in n.lower()]
        if not hits:
            print(f"No parameter name contains {args.find!r}. Use --list to see all 39.")
            return 1
        for i, n in hits:
            print(f"{i:>2}. {n}")
        return 0

    if args.principle is not None:
        pid = args.principle
        if not 1 <= pid <= 40:
            print("Principle id must be 1-40.", file=sys.stderr)
            return 2
        print(f"{pid}. {principles.get(pid, '(name unavailable)')}")
        print("Full description: references/40_principles.md")
        return 0

    improving, worsening = args.improving, args.worsening
    if improving is None or worsening is None:
        if len(args.pair) == 2:
            improving, worsening = args.pair
        else:
            ap.print_help()
            return 2

    for label, val in (("improving", improving), ("worsening", worsening)):
        if not 1 <= val <= 39:
            print(f"{label} parameter must be 1-39 (got {val}).", file=sys.stderr)
            return 2
    if improving == worsening:
        print(
            f"Both parameters are #{improving} ({params.get(improving, '?')}). "
            "A parameter conflicting with itself is a PHYSICAL contradiction, not a technical one — "
            "use resources/separation_principles.md instead of the matrix.",
            file=sys.stderr,
        )
        return 2

    cells = load_matrix()["cells"]
    ids = cells.get(f"{improving},{worsening}", [])

    print(f"Improving: {improving}. {params.get(improving, '?')}")
    print(f"Worsening: {worsening}. {params.get(worsening, '?')}")
    if ids:
        print(f"\nRecommended principles ({len(ids)}):")
        print(fmt_principles(ids, principles))
        print("\nSource tag: matrix")
    else:
        print("\nCell is empty — no principles are statistically recommended for this pair.")
        print("This is normal (292 of 1521 cells are empty). Select principles by meaning from")
        print("references/40_principles.md and tag the result `Source: inferred`, not `matrix`.")

    rev = cells.get(f"{worsening},{improving}", [])
    if rev:
        print(f"\nReverse formulation ({worsening} improving vs {improving} worsening) gives: "
              f"{', '.join(str(i) for i in rev)}")
        print("The matrix is asymmetric — run both TC directions before converging.")

    print("\nPrinciples are directional hints; adapt each to the concrete system.")
    return 0 if ids else 1


if __name__ == "__main__":
    sys.exit(main())
