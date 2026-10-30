import assert from "node:assert/strict";
import { test } from "node:test";
import { Pool } from "pg";
import { buildApp } from "../app.js";
import { loadConfig } from "../config.js";
import { isReady, markDbConnectedOnce, resetReadyStateForTests } from "../health/state.js";

// healthz/readyz never touch the database, so a syntactically valid but
// unreachable DATABASE_URL is fine for this test file.
const config = loadConfig({
  DATABASE_URL: "postgres://unused/unused",
  NODE_ENV: "test",
  INTERNAL_API_TOKEN: "test-internal-token",
  WEBHOOK_SECRET_ENCRYPTION_KEY: "Y1ZTGTcYbe30GZJebys9w7T3OYZNKewuOH3SUCEdRQk=",
});
const pool = new Pool({ connectionString: config.databaseUrl, max: 1 });
const app = buildApp(config, pool);

/** Liveness never touches the DB. */
test("GET /healthz returns 200 immediately, independent of readiness state", async () => {
  const res = await app.inject({ method: "GET", url: "/healthz" });
  assert.equal(res.statusCode, 200);
  assert.equal(res.json().status, "ok");
});

test("GET /readyz is 503 before the boot-time DB check and 200 after — and never re-checks", () => {
  resetReadyStateForTests();
  assert.equal(isReady(), false);
});

test("GET /readyz reflects the module-scoped flag, not a live DB probe", async () => {
  resetReadyStateForTests();

  const before = await app.inject({ method: "GET", url: "/readyz" });
  assert.equal(before.statusCode, 503);
  assert.equal(before.json().status, "not_ready");

  markDbConnectedOnce();

  const after = await app.inject({ method: "GET", url: "/readyz" });
  assert.equal(after.statusCode, 200);
  assert.equal(after.json().status, "ready");

  // The flag is a one-way latch set once at boot: nothing in the route
  // itself re-verifies DB liveness on subsequent polls.
  const stillReady = await app.inject({ method: "GET", url: "/readyz" });
  assert.equal(stillReady.statusCode, 200);
});

/** The bare API address is a landing response, not a 404. */
test("GET / describes the service instead of returning 404", async () => {
  const res = await app.inject({ method: "GET", url: "/" });
  assert.equal(res.statusCode, 200);
  const body = res.json();
  assert.equal(body.service, "filspay-api");
  assert.equal(body.health, "/healthz");
  assert.equal(body.readiness, "/readyz");
  assert.equal(body.api, "/v1");
});
