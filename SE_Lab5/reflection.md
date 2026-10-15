# Reflection

*(Written for the lab's four reflection questions; the handout text available to me did not list them verbatim, so these cover the standard topics.)*

**1. Which issues were the easiest and which the hardest to fix?**
Style items (naming, docstrings, `== None`, line length) were mechanical. The hardest was `eval()`: the surge expression is a feature, so simply deleting it would break behaviour. I replaced it with a restricted `ast` evaluator that accepts only numbers, `base_rate` and `+ - * /`.

**2. Did the tools report any false positives?**
Mostly no. The "unused variable `base_rate`" warning is a mild false signal, since `eval` read it dynamically, but it disappeared once `eval` was removed. Bandit's B311 (low) is only a real problem because the value is used as a PIN. Conversely, the hard-coded barrier secret and the missing validation of `hours_booked` were *not* flagged by any tool.

**3. How would you integrate static analysis into your workflow?**
Run `flake8`, `pylint --fail-under=9.5` and `bandit -r .` in a pre-commit hook and in CI on every pull request, and block merges on High/Medium Bandit findings.

**4. What tangible improvements did you see?**
Pylint went from 4.26 to 10.00, Bandit from 2 High + 1 Medium + 2 Low to zero, Flake8 from 9 warnings to zero. The code is safer (no shell/eval injection, strong hash and RNG, no secret in source), more predictable (no shared mutable default, no import side effects) and easier to read and maintain.
