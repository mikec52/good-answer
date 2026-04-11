#!/usr/bin/env python3
"""
add_variants.py — Adds answer variants to master_question_bank.json using
the Anthropic Message Batches API with claude-haiku-4-5.

Usage:
  # Run a 10-question test first:
  python3 add_variants.py --test

  # Submit the full job:
  python3 add_variants.py --submit

  # Check status and collect results (run after submitting):
  python3 add_variants.py --collect

  # Both submit and auto-collect when ready (polls until done):
  python3 add_variants.py --submit --wait
"""

import argparse
import json
import os
import sys
import time

import anthropic

INPUT_FILE  = "master_question_bank.json"
OUTPUT_FILE = "master_question_bank_variants.json"
BATCH_ID_FILE = ".variants_batch_id"
MODEL = "claude-haiku-4-5-20251001"

SYSTEM_PROMPT = """You are helping build a Family Feud game. Your job is to add
alternate acceptable phrasings ("variants") to survey answers so that players
who type a natural shorthand or paraphrase still get credit.

Rules:
- Use your judgment on every answer regardless of length — a one-word answer
  may need variants (e.g. "Pregnant" could accept "Having a baby") and a
  multi-word answer may not need any.
- Only add variants that a reasonable person might actually type during a live
  game. Don't pad with unlikely edge cases.
- Do NOT add variants for numeric answers (e.g. "10", "40", "1980") — players
  will type the number exactly.
- Do NOT add variants that are already covered by the text field itself.
- A valid variant IS the answer — a synonym, shorthand, or specific instance
  that unambiguously belongs to it. For example, "Wine" and "Beer" are valid
  variants of "Alcohol" because wine and beer are alcohol. "Meat" and "Fish"
  are valid variants of "Food" because they are food.
- A variant is NOT valid if it is a separate answer to the survey question that
  happens to be in the same category. For example, on a question about things
  that can be spoiled, "A movie" and "Plot" are NOT variants of "A Surprise" —
  they are different answers to the question entirely.
- Return ONLY valid JSON — the full question object with variants arrays added
  where appropriate. No commentary, no markdown fences."""

def build_user_prompt(question_obj):
    return f"""Add variants to the answers in this question where appropriate.
Return the complete question object as JSON with a "variants" key added to each
answer that needs one. Omit the "variants" key entirely for answers that don't
need alternate phrasings.

{json.dumps(question_obj, indent=2)}"""

def make_batch_request(idx, question_obj):
    return {
        "custom_id": str(idx),
        "params": {
            "model": MODEL,
            "max_tokens": 2048,
            "system": SYSTEM_PROMPT,
            "messages": [
                {"role": "user", "content": build_user_prompt(question_obj)}
            ]
        }
    }

def submit_batch(questions, label="full"):
    client = anthropic.Anthropic()
    requests = [make_batch_request(i, q) for i, q in enumerate(questions)]
    print(f"Submitting batch of {len(requests)} questions ({label})...")
    batch = client.messages.batches.create(requests=requests)
    print(f"Batch submitted. ID: {batch.id}  Status: {batch.processing_status}")
    with open(BATCH_ID_FILE, "w") as f:
        json.dump({"batch_id": batch.id, "count": len(questions), "label": label}, f)
    print(f"Batch ID saved to {BATCH_ID_FILE}")
    return batch

def collect_results(questions_source):
    if not os.path.exists(BATCH_ID_FILE):
        print("No batch ID file found. Run --submit first.")
        sys.exit(1)

    with open(BATCH_ID_FILE) as f:
        meta = json.load(f)
    batch_id = meta["batch_id"]
    label = meta.get("label", "full")

    client = anthropic.Anthropic()
    batch = client.messages.batches.retrieve(batch_id)
    print(f"Batch {batch_id} status: {batch.processing_status}")

    if batch.processing_status != "ended":
        print("Batch not finished yet. Re-run --collect later (or use --wait).")
        sys.exit(0)

    # Load the appropriate source questions
    all_questions = load_questions()
    if label == "test":
        source_questions = all_questions[:10]
    else:
        source_questions = all_questions

    # Collect results into a dict keyed by custom_id
    results = {}
    for result in client.messages.batches.results(batch_id):
        if result.result.type == "succeeded":
            raw = result.result.message.content[0].text.strip()
            # Strip markdown code fences if the model included them
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[-1]  # drop opening fence line
                raw = raw.rsplit("```", 1)[0].strip()  # drop closing fence
            try:
                parsed = json.loads(raw)
                results[result.custom_id] = parsed
            except json.JSONDecodeError:
                print(f"  WARNING: Could not parse JSON for question {result.custom_id}")
                print(f"    Raw response: {raw[:200]}")
                results[result.custom_id] = None
        else:
            print(f"  ERROR on question {result.custom_id}: {result.result.type}")
            results[result.custom_id] = None

    # Merge variants back into source questions
    merged = []
    success = 0
    failed = 0
    for i, q in enumerate(source_questions):
        updated = results.get(str(i))
        if updated is not None:
            # Preserve original fields; only update the answers array (with variants)
            merged_q = dict(q)
            merged_q["answers"] = updated.get("answers", q["answers"])
            merged.append(merged_q)
            success += 1
        else:
            merged.append(q)  # keep original on failure
            failed += 1

    out_path = OUTPUT_FILE if label != "test" else "test_variants_output.json"
    with open(out_path, "w") as f:
        json.dump(merged, f, indent=2)

    print(f"\nDone. {success} updated, {failed} failed/skipped.")
    print(f"Output written to: {out_path}")

def poll_until_done(batch_id, interval=30):
    client = anthropic.Anthropic()
    while True:
        batch = client.messages.batches.retrieve(batch_id)
        status = batch.processing_status
        counts = batch.request_counts
        print(f"  [{time.strftime('%H:%M:%S')}] {status} — "
              f"processing: {counts.processing}  succeeded: {counts.succeeded}  errored: {counts.errored}")
        if status == "ended":
            return
        time.sleep(interval)

def load_questions():
    with open(INPUT_FILE) as f:
        return json.load(f)

FAILED_INDICES = [308, 340, 578, 1381, 1672, 2211, 2585, 2626, 2684]

def retry_failed():
    """Resubmit only the questions that failed JSON parsing in the full run."""
    # Work from the variants file so we patch it in place
    with open(OUTPUT_FILE) as f:
        current = json.load(f)

    targets = [(i, current[i]) for i in FAILED_INDICES]
    # Use original indices as custom_ids so collect can map back correctly
    client = anthropic.Anthropic()
    requests = [make_batch_request(i, q) for i, q in targets]
    print(f"Resubmitting {len(requests)} failed questions...")
    batch = client.messages.batches.create(requests=requests)
    print(f"Batch submitted. ID: {batch.id}  Status: {batch.processing_status}")
    with open(BATCH_ID_FILE, "w") as f:
        json.dump({"batch_id": batch.id, "count": len(requests), "label": "retry"}, f)
    return batch

def collect_retry():
    """Merge retry results back into the variants output file."""
    if not os.path.exists(BATCH_ID_FILE):
        print("No batch ID file found.")
        sys.exit(1)
    with open(BATCH_ID_FILE) as f:
        meta = json.load(f)
    batch_id = meta["batch_id"]

    client = anthropic.Anthropic()
    batch = client.messages.batches.retrieve(batch_id)
    if batch.processing_status != "ended":
        print(f"Batch not finished yet ({batch.processing_status}). Re-run --collect later.")
        sys.exit(0)

    with open(OUTPUT_FILE) as f:
        current = json.load(f)

    success = 0
    for result in client.messages.batches.results(batch_id):
        idx = int(result.custom_id)
        if result.result.type == "succeeded":
            raw = result.result.message.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[-1]
                raw = raw.rsplit("```", 1)[0].strip()
            try:
                parsed = json.loads(raw)
                current[idx]["answers"] = parsed.get("answers", current[idx]["answers"])
                success += 1
            except json.JSONDecodeError:
                print(f"  Still could not parse question {idx}")
        else:
            print(f"  ERROR on question {idx}: {result.result.type}")

    with open(OUTPUT_FILE, "w") as f:
        json.dump(current, f, indent=2)
    print(f"\nRetry done. {success}/{len(FAILED_INDICES)} patched into {OUTPUT_FILE}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test",         action="store_true", help="Submit 10-question test batch")
    parser.add_argument("--submit",       action="store_true", help="Submit full batch")
    parser.add_argument("--collect",      action="store_true", help="Collect and merge results from last batch")
    parser.add_argument("--retry-failed", action="store_true", help="Resubmit the 9 questions that failed JSON parsing")
    parser.add_argument("--wait",         action="store_true", help="Poll until done then collect automatically")
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        sys.exit(1)

    questions = load_questions()

    if args.test:
        sample = questions[:10]
        batch = submit_batch(sample, label="test")
        if args.wait:
            poll_until_done(batch.id)
            collect_results(sample)
    elif args.submit:
        batch = submit_batch(questions, label="full")
        if args.wait:
            poll_until_done(batch.id)
            collect_results(questions)
    elif args.collect:
        meta = json.load(open(BATCH_ID_FILE)) if os.path.exists(BATCH_ID_FILE) else {}
        if meta.get("label") == "retry":
            collect_retry()
        else:
            collect_results(questions)
    elif args.__dict__["retry_failed"]:
        batch = retry_failed()
        if args.wait:
            poll_until_done(batch.id)
            collect_retry()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
