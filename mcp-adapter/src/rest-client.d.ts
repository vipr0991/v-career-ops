export declare class RestClient {
    private baseUrl;
    constructor(baseUrl: string);
    searchJobs(title: string, location: string, currency: string, limit: number): Promise<any>;
    scoreJob(payload: {
        job_title: string;
        company: string;
        job_description: string;
        location?: string;
    }): Promise<any>;
    getPipeline(stage?: string, location?: string): Promise<any>;
    addToPipeline(payload: any): Promise<any>;
    updatePipelineStage(itemId: string, status: string): Promise<any>;
    deletePipelineItem(itemId: string): Promise<any>;
    generateApplicationKit(jobId: string): Promise<any>;
    researchCompany(companyName: string, jobTitle?: string, location?: string): Promise<any>;
    findDecisionMakers(companyName: string): Promise<any>;
    generateLinkedInInvite(recipientName: string, companyName: string, jobTitle: string): Promise<any>;
}
//# sourceMappingURL=rest-client.d.ts.map