# FilsPay

FilsPay is a payment platform prototype for merchant checkout, operations,
settlement, and reporting. Its services share a PostgreSQL database and
communicate through a transactional outbox.

Known bugs and their status: [`bugs.md`](bugs.md).

## Repository

| Path | Purpose |
|---|---|
| `apps/api` | Fastify API for merchant, checkout, and admin operations |
| `apps/web` | Merchant dashboard and checkout frontend (Vite/React) |
| `apps/admin` | Internal operations console (Vite/React) |
| `apps/settlement` | Go settlement daemon and CLI |
| `apps/reporting` | Reporting read model and outbox consumer |
| `packages/money` | Shared integer-fils money helpers |
| `packages/events` | Outbox event types and database helper |
| `db/migrations` | PostgreSQL schema migrations |
| `db/seed` | Local development fixtures |
| `ops/` | Docker Compose stack and the Dilmun VM setup script |
| `docs/` | Architecture, operations, onboarding, and decision records |

Design and service responsibilities: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).
Local stack details: [`ops/README.md`](ops/README.md).
Hosting: [`docs/DEPLOY.md`](docs/DEPLOY.md).

## Prerequisites

- Node.js 22 and npm
- Go 1.22 or later (settlement)
- Docker Desktop (local Postgres and backend services)

## Run it locally

### 1. Backend (Docker Compose)

From the repository root:

```sh
npm ci
docker compose -f ops/docker-compose.yml up -d postgres
docker compose -f ops/docker-compose.yml run --rm migrate
docker compose -f ops/docker-compose.yml run --rm seed
docker compose -f ops/docker-compose.yml up -d --build api settlement reporting
```

This starts Postgres on `localhost:5432`, the API on `localhost:3000`, the
settlement daemon and the reporting worker. Check it:

```sh
curl http://localhost:3000/healthz   # {"status":"ok",...}
curl http://localhost:3000/readyz    # {"status":"ready"}
```

The seed resets merchants, transactions, the ledger and admin users, then
regenerates fixtures. Only run it against this local database. It prints a
test API key for one merchant (`fp_test_...`).

Stop everything with `docker compose -f ops/docker-compose.yml down`
(add `-v` to delete the database volume).

### 2. Frontends

In two terminals:

```sh
npm run dev --workspace @filspay/web     # http://localhost:5173
npm run dev --workspace @filspay/admin   # http://localhost:5174
```

Both call the API at `http://localhost:3000`. The API allows these two
origins by default; any other host or port must be added to
`CORS_ALLOWED_ORIGINS`.

### Without Docker

Point `DATABASE_URL` at any migrated Postgres 16 and run the API directly.
Outside `NODE_ENV=production` the API uses a built-in dev webhook key, so no
other variables are needed:

```sh
DATABASE_URL="postgres://USER:PASSWORD@localhost:5432/filspay" npm run migrate
DATABASE_URL="postgres://USER:PASSWORD@localhost:5432/filspay" npm run dev --workspace @filspay/api
```

PowerShell:

```powershell
$env:DATABASE_URL = "postgres://USER:PASSWORD@localhost:5432/filspay"
npm.cmd run dev --workspace @filspay/api
```

## Development accounts

The seed creates local-only fixtures. Never use these outside local
development. In development the API returns the one-time login code in its
response, and the login pages show it.

**Admin console** ([http://localhost:5174/login](http://localhost:5174/login)),
password `FilsPayAdminSeed!2026`:

| Email | Role |
|---|---|
| `support@filspay.test` | Support |
| `finance@filspay.test` | Finance |
| `superadmin@filspay.test` | Super admin |

**Merchant dashboard** ([http://localhost:5173/dashboard/login](http://localhost:5173/dashboard/login)),
password `FilsPaySeed!2026`. Login needs the merchant ID, which changes on
every seed:

```sh
docker compose -f ops/docker-compose.yml exec postgres \
  psql -U filspay -d filspay -c \
  "select m.id, m.display_name, u.email, u.role from merchant_users u join merchants m on m.id = u.merchant_id order by 2, 4"
```

| Merchant | Logins (password `FilsPaySeed!2026`) |
|---|---|
| Alpha Retail Co | `owner@alpharetail.example`, `finance@alpharetail.example` |
| Beta Digital Services | `owner@betadigital.example`, `finance@betadigital.example`, `support@betadigital.example`, `owner@alpharetail.example` |
| Coral Bay Traders | `owner@coralbaytraders.example` |
| Delta Marketplace Bahrain | `owner@deltamarketplace.example`, `finance@deltamarketplace.example` |
| Delta Wholesale Traders | `owner@deltawholesale.example`, `finance@deltawholesale.example` |
| Gamma Hospitality Group | `owner@gammahospitality.example`, `finance@gammahospitality.example` |
| Palm Grove Retail | `owner@palmgroveretail.example` |
| Seef Kiosk Partners | `owner@seefkiosk.example` |


`owner@alpharetail.example` belongs to two merchants, which is why login
asks for the merchant ID as well as the email.

## Live demo accounts

The hosted demo has its own accounts. None of the seed fixtures above exist
there.

| Account | Sign in at | Email | Merchant ID |
|---|---|---|---|
| Admin (super admin) | [fp-admin-tzakir.dilmune.app/login](https://fp-admin-tzakir.dilmune.app/login) | `admin@filspay.demo` | — |
| Merchant owner, FilsPay Demo Store | [fp-pay-tzakir.dilmune.app/dashboard/login](https://fp-pay-tzakir.dilmune.app/dashboard/login) | `owner@filspay.demo` | `6ebe3a11-e6d4-40ac-8098-7f5c75f7563f` |

Passwords are **not** in this repository, which is public: on the live site
the login page shows the one-time code (`OTP_DEV_EXPOSE`, see bug #22 in
[`bugs.md`](bugs.md)), so a published password would be enough to take over
the account. Ask the repository owner for them.

## Try a payment

With the API key the seed printed:

```sh
KEY=fp_test_...
curl -s http://localhost:3000/v1/transactions \
  -H "authorization: Bearer $KEY" -H "content-type: application/json" \
  -H "idempotency-key: $(uuidgen)" \
  -d '{"amountFils":12500,"card":{"pan":"4242424242424242","expiryMonth":12,"expiryYear":2030,"cvv":"123"}}'
# then POST /v1/transactions/<id>/capture and POST /v1/refunds
```

Amounts are integer fils: `12500` is 12.500 BD.

## Tests and checks

```sh
npm run typecheck
DATABASE_URL=postgres://... npm run migrate
DATABASE_URL=postgres://... npm test          # needs a migrated, disposable database
cd apps/settlement && go test -short ./...
```

Use a dedicated test database: the TypeScript suites share it and write
outbox events, merchants and ledger rows.

## Helper script

`node create-merchant.cjs --dry-run` signs up a merchant on the hosted API.
Copy `merchant-details.example.json` to `merchant-details.json` first
(gitignored). It is `.cjs` because the repository is an ES module package.

## Money and settlement conventions

- Monetary values are integer fils: 1 BHD = 1,000 fils (ADR-0001).
- Parse text amounts with `parseBhdToFils`; format with `formatBhd`.
- Settlement business-day boundaries use Asia/Bahrain time (UTC+3).
- Do not modify `packages/money` or `apps/settlement/internal/money` without
  a test demonstrating the defect and finance sign-off.

## Deployment

The hosted demo runs on Dilmun Cloud: two static sites (`apps/web`,
`apps/admin`) and an API site whose processes run under systemd via
`ops/dilmune/setup.sh`. See [`docs/DEPLOY.md`](docs/DEPLOY.md) for build
commands, environment variables, nginx and known platform issues, and
[`bugs.md`](bugs.md) for what is still open.

## History notes

- **Adjustment CSV amounts:** the parser used a two-decimal default and read
  `4.75` BHD as 475 fils instead of 4,750. `parseAdjustmentAmountFils` now
  delegates to `parseBhdToFils`.
- **Commit graph:** run `git --no-pager log --graph` to see it; there is no
  need to keep a copy in the repository.
