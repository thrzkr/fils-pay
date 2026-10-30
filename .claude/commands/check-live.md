---
description: Check the live deployment instead of trusting a printed "OK"
---
Check the hosted FilsPay stack and report evidence, not summaries:

- `curl -s https://fp-api-tzakir.dilmune.app/healthz` and `/readyz`
- `curl -s https://fp-api-tzakir.dilmune.app/` returns the service JSON
- fp-pay and fp-admin serve `/`, a deep link (`/pay/x`) and the login route
- the fp-pay bundle contains `https://fp-api-tzakir.dilmune.app` (command in docs/DEPLOY.md)
- on the server: `systemctl is-active filspay-api filspay-settlement filspay-reporting`
  and the API's uptime, so a restart that "printed success" is actually confirmed

Never run `npm run seed` against the hosted database.
