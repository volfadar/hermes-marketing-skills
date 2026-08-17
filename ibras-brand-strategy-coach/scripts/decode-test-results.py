#!/usr/bin/env python3
"""
decode-test-results.py — Decode personality test share codes → structured scores.

Supports:
  1. O*NET Interest Profiler (RIASEC) share code → 6 RIASEC scores + Holland Code
  2. Big Five (OCEAN) result URL → 5 domain scores + 30 facet scores

Usage:
  python3 decode-test-results.py onet <share-code>
  python3 decode-test-results.py onet 3cz93
  
  python3 decode-test-results.py bigfive <result-id-or-url>
  python3 decode-test-results.py bigfive 6a79be1a5c3d93d52eb87048
  python3 decode-test-results.py bigfive https://bigfive-test.com/result/6a79be1a5c3d93d52eb87048

  python3 decode-test-results.py both <onet-code> <bigfive-id>
  python3 decode-test-results.py both 3cz93 6a79be1a5c3d93d52eb87048

Output: JSON to stdout (for Hermes to parse).

Sources:
  - O*NET: reverse-engineered from onetinterestprofiler.org JS bundle (function Gv/Jv)
  - Big Five: fetched from bigfive-test.com SSR page, scores extracted from Next.js RSC stream
"""
from __future__ import annotations
import sys, json, re, urllib.request

# ============================================================================
# O*NET Interest Profiler decoder
# ============================================================================

ONET_ALPHABET = "hCxDrnvJVB3StXLqg54Gpj7QkPzZ69scHRKTNbfFd"
ONET_LETTER_MAP = {
    "realistic": "R", "investigative": "I", "artistic": "A",
    "social": "S", "enterprising": "E", "conventional": "C",
}

def onet_decode(code: str) -> dict:
    """Decode a 5-char (compact) or 6-char (extended) O*NET share code."""
    code = code.strip().split("/")[-1]  # handle full URL too
    try:
        digits = [ONET_ALPHABET.index(c) for c in code]
    except ValueError:
        return {"error": f"Invalid character in code '{code}'"}

    if len(digits) == 5:
        n = digits[0]*41**4 + 68921*digits[1] + 1681*digits[2] + 41*digits[3] + digits[4]
        scores = {
            "realistic":     n // (21**5),
            "investigative": (n // (21**4)) % 21,
            "artistic":      (n // 9261) % 21,
            "social":        (n // 441) % 21,
            "enterprising":  (n // 21) % 21,
            "conventional":  n % 21,
        }
    elif len(digits) >= 6:
        keys = list(ONET_LETTER_MAP.keys())
        scores = dict(zip(keys, digits[:6]))
    else:
        return {"error": f"Code length {len(digits)} not supported (need 5 or 6)"}

    # Holland Code (top 3)
    ranked = sorted(scores.items(), key=lambda x: -x[1])
    holland = "".join(ONET_LETTER_MAP[k] for k, _ in ranked[:3])

    return {
        "test": "O*NET Interest Profiler (RIASEC)",
        "share_code": code,
        "scores": scores,
        "holland_code": holland,
        "top_3": [{"letter": ONET_LETTER_MAP[k], "type": k, "score": v} for k, v in ranked[:3]],
    }


# ============================================================================
# Big Five (OCEAN) decoder
# ============================================================================

BF_DOMAINS = ["Neuroticism", "Extraversion", "Openness", "Agreeableness", "Conscientiousness"]
BF_FACETS = {
    "Neuroticism": ["Anxiety","Anger","Depression","Self-Consciousness","Impulsiveness","Vulnerability"],
    "Extraversion": ["Friendliness","Gregariousness","Assertiveness","Activity Level","Excitement-Seeking","Cheerfulness"],
    "Openness": ["Imagination","Artistic Interests","Emotionality","Adventurousness","Intellect","Liberalism"],
    "Agreeableness": ["Trust","Morality","Altruism","Cooperation","Modesty","Sympathy"],
    "Conscientiousness": ["Self-Efficacy","Orderliness","Dutifulness","Achievement-Striving","Self-Discipline","Cautiousness"],
}
# OCEAN letter map
BF_LETTER = {"Openness":"O","Conscientiousness":"C","Extraversion":"E","Agreeableness":"A","Neuroticism":"N"}

def bigfive_decode(result_id_or_url: str) -> dict:
    """Fetch Big Five result from bigfive-test.com and extract all scores."""
    # Extract ID from URL or use as-is
    rid = result_id_or_url.strip()
    if "bigfive-test.com" in rid:
        rid = rid.rstrip("/").split("/")[-1]
    
    if len(rid) != 24 or not re.match(r'^[0-9a-f]+$', rid):
        return {"error": f"Invalid Big Five result ID '{rid}' (need 24 hex chars)"}
    
    url = f"https://bigfive-test.com/result/{rid}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return {"error": f"Failed to fetch {url}: {e}"}
    
    # Concatenate all Next.js RSC chunks into one string
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html, re.DOTALL)
    full = ""
    for chunk in chunks:
        try:
            full += chunk.encode().decode("unicode_escape")
        except:
            full += chunk

    # Domain scores: "score":NN,"facets":[ (unique to domain level)
    domain_scores = re.findall(r'"score":(\d+),"facets":\[', full)
    # Facet scores: "facet":N,...,"score":NN,"count" (unique to facet level)
    facet_scores = re.findall(r'"facet":\d+[^}]*?"score":(\d+),"count"', full)

    if len(domain_scores) < 5:
        return {"error": f"Could not find 5 domain scores (got {len(domain_scores)})"}
    if len(facet_scores) < 30:
        return {"error": f"Could not find 30 facet scores (got {len(facet_scores)})"}

    domain_ints = [int(s) for s in domain_scores[:5]]
    facet_ints = [int(s) for s in facet_scores[:30]]
    
    result = {
        "test": "Big Five (OCEAN)",
        "result_id": rid,
        "url": url,
        "domains": {},
    }
    
    idx = 0
    for domain in BF_DOMAINS:
        d_score = domain_ints[idx]
        facets = {}
        for j, fname in enumerate(BF_FACETS[domain]):
            facets[fname] = facet_ints[idx * 6 + j]
        idx += 1
        result["domains"][domain] = {
            "letter": BF_LETTER[domain],
            "score": d_score,
            "level": "high" if d_score >= 67 else ("low" if d_score <= 33 else "medium"),
            "facets": facets,
        }
    
    # Top 3 domains
    ranked = sorted(result["domains"].items(), key=lambda x: -x[1]["score"])
    result["top_3"] = [{"letter": v["letter"], "domain": k, "score": v["score"]} for k, v in ranked[:3]]
    
    return result


# ============================================================================
# Combined
# ============================================================================

def combine(onet_result: dict, bf_result: dict) -> dict:
    """Combine O*NET + Big Five into a unified profile."""
    return {
        "personality_test": "Big Five (OCEAN) + O*NET Interest Profiler (RIASEC)",
        "big_five": bf_result,
        "onet_riasec": onet_result,
        "summary": {
            "ocean_top3": bf_result.get("top_3", []),
            "riasec_holland": onet_result.get("holland_code", ""),
            "riasec_top3": onet_result.get("top_3", []),
        }
    }


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    test_type = sys.argv[1].lower()
    
    if test_type == "onet":
        result = onet_decode(sys.argv[2])
    elif test_type == "bigfive":
        result = bigfive_decode(sys.argv[2])
    elif test_type == "both":
        o = onet_decode(sys.argv[2])
        b = bigfive_decode(sys.argv[3])
        result = combine(o, b)
    else:
        print(f"Unknown test type: {test_type}. Use: onet, bigfive, or both")
        sys.exit(1)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
