from typing import List, Tuple

try:
    # fuzzywuzzy with python-Levenshtein (faster) jika tersedia
    from fuzzywuzzy import process  # type: ignore
except Exception:
    process = None  # fallback sederhana di bawah


def fuzzy_top(query: str, choices: List[str], k: int = 3) -> List[Tuple[str, int]]:
    """
    Return top-k fuzzy matches (choice, score 0..100).
    Fallback ke pencarian 'contains' jika fuzzywuzzy tidak tersedia.
    """
    if not query or not choices:
        return []

    if process:
        # fuzzywuzzy akan mengembalikan [(choice, score), ...]
        return process.extract(query, choices, limit=k)  # type: ignore

    # --- Fallback very-simple contains match ---
    q = query.lower()
    scored = []
    for c in choices:
        lc = c.lower()
        if q == lc:
            scored.append((c, 100))
        elif q in lc:
            scored.append((c, 80))
        else:
            # poor-man similarity: prefix overlap
            prefix = 0
            for a, b in zip(q, lc):
                if a == b:
                    prefix += 1
                else:
                    break
            score = min(70, int(70 * (prefix / max(1, len(q)))))
            scored.append((c, score))
    scored.sort(key=lambda t: t[1], reverse=True)
    return scored[:k]
