#!/usr/bin/env python3
"""
sample_variants.py — Print a random sample of questions from the variants
output file for spot-checking quality.

Usage:
  python3 sample_variants.py            # 20 random questions
  python3 sample_variants.py --n 50     # 50 random questions
  python3 sample_variants.py --seed 42  # reproducible sample
  python3 sample_variants.py --with-variants-only  # skip questions where no answer got variants
"""

import argparse
import json
import random

OUTPUT_FILE = "master_question_bank_variants.json"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n",    type=int, default=20, help="Number of questions to sample")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    parser.add_argument("--with-variants-only", action="store_true",
                        help="Only show questions where at least one answer has variants")
    args = parser.parse_args()

    with open(OUTPUT_FILE) as f:
        questions = json.load(f)

    if args.with_variants_only:
        questions = [q for q in questions
                     if any("variants" in a for a in q.get("answers", []))]

    rng = random.Random(args.seed)
    sample = rng.sample(questions, min(args.n, len(questions)))

    for i, q in enumerate(sample, 1):
        print(f"{'─' * 60}")
        print(f"[{i}] {q['question']}")
        if q.get("category"):
            cat = q["category"]
            if q.get("subCategory"):
                cat += f" / {q['subCategory']}"
            print(f"    Category: {cat}")
        print()
        for ans in q.get("answers", []):
            variants = ans.get("variants", [])
            variant_str = f"  → {', '.join(variants)}" if variants else ""
            print(f"    {ans['points']:>3}  {ans['text']}{variant_str}")
        print()

    print(f"{'─' * 60}")
    print(f"Showed {len(sample)} questions "
          f"({'with variants only' if args.with_variants_only else 'random sample'})")

if __name__ == "__main__":
    main()
