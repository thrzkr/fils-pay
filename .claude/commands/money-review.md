---
description: Review a diff for FilsPay money, concurrency and tenant-isolation rules
---
Review the current diff (`git diff` against the base branch) for:

- money as anything other than integer fils; parseFloat, toFixed(2), * 100, float32/float64
- rates not applied with applyRateFils / splits not summing to the total
- read-then-write on money without FOR UPDATE or an atomic conditional UPDATE
- money-moving endpoints without a client Idempotency-Key
- queries that take an id from the request without scoping by the caller's merchant
- write routes not using requireMerchantWriterActor; impersonation that can write
- Math.random() for any secret; secrets in the diff
- dates not computed in Asia/Bahrain for settlement

List each finding with file:line, why it is wrong, and a concrete failing scenario.
