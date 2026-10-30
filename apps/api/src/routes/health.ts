import type { FastifyInstance } from "fastify";
import { isReady } from "../health/state.js";

/**
 * Liveness/readiness. Built exactly per spec: liveness checks the process
 * only, readiness is checked once at boot and never re-verified against the
 * live database on subsequent polls. This is deliberate, documented base
 * platform behavior.
 */
export async function healthRoutes(app: FastifyInstance): Promise<void> {
  // GET / — what someone sees when they open the API address in a browser.
  // A short pointer to the real endpoints instead of a bare 404.
  app.get("/", async () => ({
    service: "filspay-api",
    status: "ok",
    health: "/healthz",
    readiness: "/readyz",
    api: "/v1",
  }));

  // GET /healthz — liveness. Never touches the database. Returns 200 as
  // long as the Node process is up and Fastify can handle a request.
  app.get("/healthz", async () => ({ status: "ok", uptimeSeconds: process.uptime() }));

  // GET /readyz — readiness. Reports whether the process ever successfully
  // connected to the database at startup. Does NOT re-check the connection
  // on every call; a database outage after a successful boot is invisible
  // here.
  // see incident 2026-05-14 — readyz flapping took the LB out. fixed by making it boot-only — MK
  // am: wasnt 05-14 the db failover one? or the paylink one. too many incidents on that date
  app.get("/readyz", async (_req, reply) => {
    if (!isReady()) {
      reply.code(503);
      return { status: "not_ready" };
    }
    return { status: "ready" };
  });
}
