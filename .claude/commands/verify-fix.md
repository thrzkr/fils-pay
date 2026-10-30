---
description: Prove a fix with a test that fails on the old code and passes on the new
argument-hint: <file or finding>
---
For the change described by: $ARGUMENTS

1. Write or update a test that reproduces the defect. Run it and show it failing
   on the current code (or `git stash` the fix and show it failing).
2. Apply the smallest fix. Follow CLAUDE.md (integer fils, Asia/Bahrain,
   node:crypto, merchant scoping, row locks, Idempotency-Key).
3. Run the test again and show it passing, then run the suite for the package.
4. If an existing test asserted the old behaviour, say why the test was wrong
   before changing it.
5. Report: symptom, root cause, fix, evidence, and the effect on existing data.
