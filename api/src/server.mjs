import Fastify from "fastify";
import { createClient } from "@supabase/supabase-js";

const SUPABASE_URL = process.env.SUPABASE_URL;
const SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;
const ANON_KEY = process.env.SUPABASE_ANON_KEY;
const EDGE_URL = `${SUPABASE_URL}/functions/v1/hitl-resume`;

const app = Fastify({ logger: true });
const admin = createClient(SUPABASE_URL, SERVICE_KEY);

// Ghost mode: noindex on every response, no exceptions.
app.addHook("onSend", async (_req, reply) => {
  reply.header("X-Robots-Tag", "noindex, nofollow, noarchive");
});

// JWT wall: everything except /health requires a valid Supabase JWT.
app.addHook("onRequest", async (req, reply) => {
  if (req.url === "/health") return;
  const token = (req.headers.authorization ?? "").replace("Bearer ", "");
  if (!token) return reply.code(401).send({ error: "missing bearer token" });
  const authClient = createClient(SUPABASE_URL, ANON_KEY);
  const { data, error } = await authClient.auth.getUser(token);
  if (error || !data.user) return reply.code(401).send({ error: "invalid token" });
  req.userId = data.user.id;
});

app.get("/health", async () => ({ ok: true }));

app.get("/pipeline", async (req, reply) => {
  const { data, error } = await admin
    .from("evaluations")
    .select("id, company_name, job_title, url, stage, tier2_score, needs_reauth, created_at")
    .order("created_at", { ascending: false })
    .limit(200);
  if (error) return reply.code(500).send({ error: error.message });
  return { items: data };
});

app.post("/approve", async (req, reply) => {
  // Forward the user's JWT to the Edge Function so approval stays a
  // user-authenticated action end to end.
  const token = (req.headers.authorization ?? "").replace("Bearer ", "");
  const res = await fetch(EDGE_URL, {
    method: "POST",
    headers: {
      authorization: `Bearer ${token}`,
      "content-type": "application/json",
    },
    body: JSON.stringify({ evaluation_id: req.body?.evaluation_id }),
  });
  const body = await res.text();
  return reply.code(res.status).header("content-type", "application/json").send(body);
});

const port = Number(process.env.PORT ?? 8080);
app.listen({ port, host: "0.0.0.0" }).catch((err) => {
  app.log.error(err);
  process.exit(1);
});
