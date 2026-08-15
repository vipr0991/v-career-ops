export class RestClient {
    baseUrl;
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }
    async searchJobs(title, location, currency, limit) {
        const url = `${this.baseUrl}/api/search`;
        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title, location, currency, limit })
        });
        if (!response.ok) {
            const body = await response.text();
            throw new Error(`REST_${response.status}: ${body.slice(0, 500)}`);
        }
        return response.json();
    }
    async scoreJob(payload) {
        const url = `${this.baseUrl}/api/score`;
        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        if (!response.ok) {
            const body = await response.text();
            throw new Error(`REST_${response.status}: ${body.slice(0, 500)}`);
        }
        return response.json();
    }
    async getPipeline(stage, location) {
        const params = new URLSearchParams();
        if (stage)
            params.append("stage", stage);
        if (location)
            params.append("location", location);
        const qs = params.toString() ? `?${params.toString()}` : "";
        const url = `${this.baseUrl}/api/pipeline${qs}`;
        const response = await fetch(url, {
            method: "GET",
            headers: { "Accept": "application/json" }
        });
        if (!response.ok) {
            const body = await response.text();
            throw new Error(`REST_${response.status}: ${body.slice(0, 500)}`);
        }
        return response.json();
    }
    async addToPipeline(payload) {
        const url = `${this.baseUrl}/api/pipeline`;
        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        if (!response.ok) {
            const body = await response.text();
            throw new Error(`REST_${response.status}: ${body.slice(0, 500)}`);
        }
        return response.json();
    }
    async updatePipelineStage(itemId, status) {
        const url = `${this.baseUrl}/api/pipeline/${encodeURIComponent(itemId)}`;
        const response = await fetch(url, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status })
        });
        if (!response.ok) {
            const body = await response.text();
            throw new Error(`REST_${response.status}: ${body.slice(0, 500)}`);
        }
        return response.json();
    }
    async deletePipelineItem(itemId) {
        const url = `${this.baseUrl}/api/pipeline?item_id=${encodeURIComponent(itemId)}`;
        const response = await fetch(url, {
            method: "DELETE",
            headers: { "Accept": "application/json" }
        });
        if (!response.ok) {
            const body = await response.text();
            throw new Error(`REST_${response.status}: ${body.slice(0, 500)}`);
        }
        return response.json();
    }
    async generateApplicationKit(jobId) {
        const url = `${this.baseUrl}/api/pipeline/generate-kit`;
        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ job_id: jobId })
        });
        if (!response.ok) {
            const body = await response.text();
            throw new Error(`REST_${response.status}: ${body.slice(0, 500)}`);
        }
        return response.json();
    }
    async researchCompany(companyName, jobTitle, location) {
        const url = `${this.baseUrl}/api/research/company`;
        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ company_name: companyName, job_title: jobTitle || "", location: location || "" })
        });
        if (!response.ok) {
            const body = await response.text();
            throw new Error(`REST_${response.status}: ${body.slice(0, 500)}`);
        }
        return response.json();
    }
    async findDecisionMakers(companyName) {
        const url = `${this.baseUrl}/api/research/decision-makers`;
        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ company_name: companyName })
        });
        if (!response.ok) {
            const body = await response.text();
            throw new Error(`REST_${response.status}: ${body.slice(0, 500)}`);
        }
        return response.json();
    }
    async generateLinkedInInvite(recipientName, companyName, jobTitle) {
        const url = `${this.baseUrl}/api/outreach/generate-invite`;
        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ recipient_name: recipientName, company_name: companyName, job_title: jobTitle })
        });
        if (!response.ok) {
            const body = await response.text();
            throw new Error(`REST_${response.status}: ${body.slice(0, 500)}`);
        }
        return response.json();
    }
}
//# sourceMappingURL=rest-client.js.map