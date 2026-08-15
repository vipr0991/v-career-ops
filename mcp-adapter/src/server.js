import "dotenv/config";
import express from "express";
import cors from "cors";
import { z } from "zod";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
import { RestClient } from "./rest-client.js";
const PORT = Number(process.env.MCP_PORT || process.env.PORT || 8787);
const REST_API_BASE_URL = process.env.REST_API_BASE_URL || "https://v-career-ops.up.railway.app";
const MCP_SHARED_SECRET = process.env.MCP_SHARED_SECRET;
if (!MCP_SHARED_SECRET) {
    console.error("ERROR: MCP_SHARED_SECRET environment variable is required.");
    process.exit(1);
}
const api = new RestClient(REST_API_BASE_URL);
const server = new McpServer({
    name: "career-ops-mcp-adapter",
    version: "4.0.0"
});
// ── 1. Search Jobs Tool ──────────────────────────────────────────────────────
server.tool("search_jobs", "Search for live job vacancies across target regions (e.g. Dubai, UAE, KSA, Qatar, Kuwait, Oman, Bahrain, Bangalore).", {
    title: z.string().describe("Target role or job title (e.g., Senior Marketing Manager)"),
    location: z.string().default("UAE").describe("Region/Country filter (e.g., UAE, KSA, Qatar, Bangalore)"),
    currency: z.string().default("AED").describe("Currency filter (e.g., AED, SAR, USD, INR)"),
    limit: z.number().default(15).describe("Number of results to return (max 50)")
}, async ({ title, location, currency, limit }) => {
    try {
        const results = await api.searchJobs(title, location, currency, limit);
        return { content: [{ type: "text", text: JSON.stringify(results, null, 2) }] };
    }
    catch (e) {
        return { content: [{ type: "text", text: `Error searching jobs: ${e.message}` }] };
    }
});
// ── 2. AI 10-Dimension Score Tool ────────────────────────────────────────────
server.tool("score_job", "Evaluate a job description line-by-line across 10 dimensions against the candidate's profile. Automatically saves to pipeline if score >= 85.", {
    job_title: z.string().describe("Job title"),
    company: z.string().describe("Hiring company name"),
    job_description: z.string().describe("Full text of the job description / requirements"),
    location: z.string().default("Dubai, UAE").describe("Job location")
}, async (payload) => {
    try {
        const results = await api.scoreJob(payload);
        return { content: [{ type: "text", text: JSON.stringify(results, null, 2) }] };
    }
    catch (e) {
        return { content: [{ type: "text", text: `Error scoring job: ${e.message}` }] };
    }
});
// ── 3. Pipeline Read Tool ────────────────────────────────────────────────────
server.tool("get_pipeline", "Retrieve all active job opportunities saved in the user's Career-Ops Pipeline.", {
    stage: z.string().optional().describe("Optional stage filter (e.g., pipeline_saved, assets_generated, applied, interviewing)"),
    location: z.string().optional().describe("Optional location filter")
}, async ({ stage, location }) => {
    try {
        const results = await api.getPipeline(stage, location);
        return { content: [{ type: "text", text: JSON.stringify(results, null, 2) }] };
    }
    catch (e) {
        return { content: [{ type: "text", text: `Error fetching pipeline: ${e.message}` }] };
    }
});
// ── 4. Pipeline Add Tool ─────────────────────────────────────────────────────
server.tool("add_to_pipeline", "Save or add a new job opportunity into the Career-Ops Pipeline.", {
    title: z.string().describe("Job title"),
    company: z.string().describe("Company name"),
    location: z.string().describe("Job location"),
    salary_range: z.string().default("Not Disclosed").describe("Salary information"),
    url: z.string().default("").describe("Link to job listing or application URL"),
    source: z.string().default("GenSpark Agent").describe("Source identifier"),
    description: z.string().default("").describe("Full job description / notes"),
    stage: z.string().default("pipeline_saved").describe("Initial pipeline stage")
}, async (payload) => {
    try {
        const results = await api.addToPipeline(payload);
        return { content: [{ type: "text", text: JSON.stringify(results, null, 2) }] };
    }
    catch (e) {
        return { content: [{ type: "text", text: `Error adding to pipeline: ${e.message}` }] };
    }
});
// ── 5. Pipeline Update Stage Tool ────────────────────────────────────────────
server.tool("update_pipeline_stage", "Update the status or stage of a job in the pipeline (e.g., pipeline_saved -> applied -> interviewing -> offer).", {
    item_id: z.string().describe("Pipeline item ID"),
    status: z.string().describe("Target stage/status")
}, async ({ item_id, status }) => {
    try {
        const results = await api.updatePipelineStage(item_id, status);
        return { content: [{ type: "text", text: JSON.stringify(results, null, 2) }] };
    }
    catch (e) {
        return { content: [{ type: "text", text: `Error updating pipeline stage: ${e.message}` }] };
    }
});
// ── 6. Pipeline Delete Tool ──────────────────────────────────────────────────
server.tool("delete_pipeline_item", "Remove or archive an unwanted job from the pipeline.", {
    item_id: z.string().describe("Pipeline item ID to delete")
}, async ({ item_id }) => {
    try {
        const results = await api.deletePipelineItem(item_id);
        return { content: [{ type: "text", text: JSON.stringify(results, null, 2) }] };
    }
    catch (e) {
        return { content: [{ type: "text", text: `Error deleting pipeline item: ${e.message}` }] };
    }
});
// ── 7. 1-Click Application Kit Tool ──────────────────────────────────────────
server.tool("generate_application_kit", "Generate complete application kit for a pipeline job (company research, decision makers, LaTeX resume customization, and 6-slide PPTX deck).", {
    job_id: z.string().describe("Pipeline item ID")
}, async ({ job_id }) => {
    try {
        const results = await api.generateApplicationKit(job_id);
        return { content: [{ type: "text", text: JSON.stringify(results, null, 2) }] };
    }
    catch (e) {
        return { content: [{ type: "text", text: `Error generating kit: ${e.message}` }] };
    }
});
// ── 8. Company Deep Research Tool ────────────────────────────────────────────
server.tool("research_company", "Perform deep company research (strategy, culture, pain points, recent news, competitors).", {
    company_name: z.string().describe("Target company name"),
    job_title: z.string().optional().describe("Target role title"),
    location: z.string().optional().describe("Company office/location")
}, async ({ company_name, job_title, location }) => {
    try {
        const results = await api.researchCompany(company_name, job_title, location);
        return { content: [{ type: "text", text: JSON.stringify(results, null, 2) }] };
    }
    catch (e) {
        return { content: [{ type: "text", text: `Error researching company: ${e.message}` }] };
    }
});
// ── 9. Decision Makers & Recruiters Tool ─────────────────────────────────────
server.tool("find_decision_makers", "Identify executive hiring managers, VPs, Directors, and recruiters for a company.", {
    company_name: z.string().describe("Company name to search")
}, async ({ company_name }) => {
    try {
        const results = await api.findDecisionMakers(company_name);
        return { content: [{ type: "text", text: JSON.stringify(results, null, 2) }] };
    }
    catch (e) {
        return { content: [{ type: "text", text: `Error finding decision makers: ${e.message}` }] };
    }
});
// ── 10. LinkedIn Outreach Note Tool ──────────────────────────────────────────
server.tool("generate_linkedin_invite", "Generate a personalized, high-conversion LinkedIn connection note strictly under 200 characters.", {
    recipient_name: z.string().describe("Name of the recruiter or decision maker"),
    company_name: z.string().describe("Target company"),
    job_title: z.string().describe("Target role")
}, async ({ recipient_name, company_name, job_title }) => {
    try {
        const results = await api.generateLinkedInInvite(recipient_name, company_name, job_title);
        return { content: [{ type: "text", text: JSON.stringify(results, null, 2) }] };
    }
    catch (e) {
        return { content: [{ type: "text", text: `Error generating invite: ${e.message}` }] };
    }
});
const app = express();
app.use(cors());
app.use(express.json());
// Health check endpoint
app.get("/health", (req, res) => {
    res.json({ status: "healthy", service: "career-ops-mcp-adapter", timestamp: new Date().toISOString() });
});
// Authentication Middleware
function authenticateMcpClient(req, res, next) {
    const header = req.headers.authorization ?? "";
    if (header !== `Bearer ${MCP_SHARED_SECRET}`) {
        console.warn(`[401] Unauthorized access attempt from ${req.ip}`);
        return res.status(401).json({ error: "unauthorized" });
    }
    next();
}
app.use(authenticateMcpClient);
let transport;
app.get("/sse", async (req, res) => {
    console.log("[SSE] Client connected from", req.ip);
    transport = new SSEServerTransport("/message", res);
    await server.connect(transport);
});
app.post("/message", async (req, res) => {
    if (transport) {
        await transport.handlePostMessage(req, res);
    }
    else {
        res.status(400).send("No active SSE connection");
    }
});
app.listen(PORT, () => {
    console.log(`MCP Adapter running on port ${PORT}`);
    console.log(`SSE Endpoint: http://127.0.0.1:${PORT}/sse`);
});
//# sourceMappingURL=server.js.map