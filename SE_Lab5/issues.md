# Issues Found and Fixed

**Student:** Daruru Bhuvan Sai | **SRN:** PES1UG24AM356 | **File:** `parking_lot_system.py`

Reports: `reports_before/` (original) and `reports_after/` (final).
Result: Pylint 4.26 → **10.00/10**, Bandit 5 issues → **0**, Flake8 9 → **0**.

| Issue | Type | Line(s) (original) | Description | Fix Approach |
|-------|------|--------------------|-------------|--------------|
| `os.system` with string concatenation (B605, **High**) | Security | 64 | Shell command built from the `filename` argument allows command injection. | Removed the shell call; use `print()`. |
| Weak MD5 hash (B324, **High**) | Security | 53 | MD5 is broken and unsuitable for hashing identifiers. | Switched to `hashlib.sha256`. |
| `eval()` on user input (B307, **Medium**) | Security / Bug | 48 | `calculateParkingFee` executes arbitrary code passed as `surge_expr`. | Replaced with an `ast`-based evaluator allowing only numbers, `base_rate` and `+ - * /`; anything else raises `ValueError`. |
| `random` for ticket PIN (B311, Low) | Security | 57 | Predictable PRNG for an access PIN. | Use `secrets.randbelow(9000) + 1000`. |
| Bare `except: pass` (B110 / E722 / W0702) | Bug | 28-33 | Silently swallowed every error, hiding unknown slot IDs. | Catch `KeyError` only and return `False`/`True`. |
| Hard-coded barrier secret (not flagged by Bandit) | Security | 76, 85 | Secret token in source and printed to output. | Read from env var `BARRIER_GATE_KEY`; only print whether it is set. |
| Mutable default argument `entry_logs=[]` (W0102) | Bug | 15 | List shared across all calls; logs leaked between calls. | Default `None`; append only when a list is passed. |
| `global total_collections` (W0603, C0103) | Design | 12, 16 | Global rebinding makes state hard to track. | Mutable `COLLECTIONS` dict constant updated in place. |
| `open()` without `with` (R1732) | Resource leak | 61-63 | File not closed if `write` raises. | Use a `with open(..., encoding="utf-8")` block. |
| camelCase function names (C0103) | Style | all functions | Violates PEP 8 snake_case. | Renamed (`park_vehicle`, `release_slot`, ...). |
| Missing docstrings (C0114/C0116) | Style | module, all functions | No documentation. | Added module and function docstrings. |
| `== None`, if/else returning bool (E711, C0121, R1703, R1705) | Style | 38-43 | Non-idiomatic comparisons and branches. | `slot is not None and not slot["is_occupied"]`. |
| Unused import `math`, unused vars `overtime_fee`, `base_rate`, `s` (F401, F841, W0611, W0612) | Dead code | 4, 37, 47, 69 | Dead code; `base_rate` was only "unused" because it's read through `eval`. | Removed, or use `base_rate` explicitly in the evaluator; `sum()` for counting. |
| Parameter shadows global `parking_slots` (W0621) | Bug-prone | 67 | Hides the module-level dict. | Renamed parameter to `slots`. |
| `%` formatting, 131-char line (C0209, C0301, E501) | Style | 23, 7-9 | Long lines and old-style formatting. | f-strings; wrapped lines to ≤79 chars. |
| Missing final newline (W292, C0304) and `main()` run on import | Style / Bug | 88 | Importing the module ran the demo. | Added newline; `if __name__ == "__main__":` guard. |
| No input validation (not flagged by tools) | Logic bug | 15-24 | Zero/negative `hours_booked` reduced total collections. | Reject `hours_booked <= 0`. |

## Commits
1. Bandit fixes (security)
2. Pylint fixes (quality, 10/10)
3. Flake8 fixes (PEP 8 formatting) + "after" reports
