#!/usr/bin/env python3
"""
Generate submission.jsonl containing composed messages for the 30 canonical test pairs
in accordance with challenge-brief.md §7.2
"""

import sys
import json
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from bot import compose

def main():
    root = Path(__file__).parent.resolve()
    expanded_dir = root / "dataset" / "expanded"
    test_pairs_path = expanded_dir / "test_pairs.json"
    
    if not test_pairs_path.exists():
        print(f"Error: {test_pairs_path} not found.")
        sys.exit(1)
        
    with open(test_pairs_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        pairs = data.get("pairs", [])
        
    submission_file = root / "submission.jsonl"
    print(f"Generating {len(pairs)} submissions to {submission_file}...")
    
    lines = []
    for pair in pairs:
        tid = pair.get("trigger_id")
        mid = pair.get("merchant_id")
        cid = pair.get("customer_id")
        test_id = pair.get("test_id")
        
        # Load trigger
        trg_file = expanded_dir / "triggers" / f"{tid}.json"
        with open(trg_file, "r", encoding="utf-8") as f:
            trigger = json.load(f)
            
        # Load merchant
        m_file = expanded_dir / "merchants" / f"{mid}.json"
        with open(m_file, "r", encoding="utf-8") as f:
            merchant = json.load(f)
            
        # Load category
        cat_slug = merchant.get("category_slug", "")
        cat_file = expanded_dir / "categories" / f"{cat_slug}.json"
        category = {}
        if cat_file.exists():
            with open(cat_file, "r", encoding="utf-8") as f:
                category = json.load(f)
        else:
            category = {"slug": cat_slug}
            
        # Load customer if applicable
        customer = None
        if cid:
            c_file = expanded_dir / "customers" / f"{cid}.json"
            if c_file.exists():
                with open(c_file, "r", encoding="utf-8") as f:
                    customer = json.load(f)
                    
        result = compose(category, merchant, trigger, customer)
        record = {
            "test_id": test_id,
            "trigger_id": tid,
            "merchant_id": mid,
            "customer_id": cid,
            "body": result.get("body", ""),
            "cta": result.get("cta", "binary"),
            "send_as": result.get("send_as", "vera"),
            "suppression_key": result.get("suppression_key", f"suppress:{tid}"),
            "rationale": result.get("rationale", "")
        }
        lines.append(json.dumps(record, ensure_ascii=False))
        
    with open(submission_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
        
    print(f"Successfully generated {len(lines)} records in submission.jsonl")

if __name__ == "__main__":
    main()
