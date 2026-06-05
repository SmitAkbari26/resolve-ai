import axios from "axios";

const API_BASE_URL = "http://localhost:8000/api/v1";
export const API_WS_URL = "ws://localhost:8000/api/v1/chat/ws";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor to add auth token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

export const authApi = {
  login: async (payload: any) => {
    const response = await apiClient.post("/users/login", payload);
    return response.data;
  },
  register: async (payload: any) => {
    const response = await apiClient.post("/users", payload);
    return response.data;
  },
};

export const ticketApi = {
  listTickets: async (status?: string) => {
    const response = await apiClient.get("/tickets", {
      params: status && status !== "all" ? { status } : {},
    });
    return response.data;
  },
  getTicket: async (ticketId: string) => {
    const response = await apiClient.get(`/tickets/${ticketId}`);
    return response.data;
  },
  createTicket: async (payload: any) => {
    const response = await apiClient.post("/tickets", payload);
    return response.data;
  },
  updateTicket: async (ticketId: string, payload: any) => {
    const response = await apiClient.post(`/tickets/${ticketId}`, payload);
    return response.data;
  },
};

export const workflowApi = {
  listExecutions: async (status?: string) => {
    const url =
      status && status !== "all"
        ? `/workflow-executions/status/${status}`
        : "/workflow-executions";
    const response = await apiClient.get(url);
    return response.data;
  },
  getExecution: async (workflowId: string) => {
    const response = await apiClient.get(`/workflow-executions/${workflowId}`);
    return response.data;
  },
  listSteps: async (workflowExecutionId: string) => {
    const response = await apiClient.get(
      `/workflow-steps/workflow/${workflowExecutionId}`,
    );
    return response.data;
  },
};

export const approvalApi = {
  listApprovals: async (status?: string) => {
    const url = status ? `/approvals/status/${status}` : "/approvals";
    const response = await apiClient.get(url);
    return response.data;
  },
  updateApproval: async (approvalId: string, payload: any) => {
    const response = await apiClient.put(`/approvals/${approvalId}`, payload);
    return response.data;
  },
};

export const chatApi = {
  sendMessage: async (payload: {
    user_id: string;
    user_email: string;
    message: string;
    conversation_id?: string | null;
  }) => {
    const response = await apiClient.post("/chat/message", payload);
    return response.data;
  },
  getHistory: async (conversationId: string) => {
    const response = await apiClient.get(`/chat/history/${conversationId}`);
    return response.data;
  },
  resumeWorkflow: async (
    workflowId: string,
    payload: {
      approval_decision: string;
      decided_by?: string;
    },
  ) => {
    const response = await apiClient.post(
      `/chat/resume/${workflowId}`,
      payload,
    );
    return response.data;
  },
};

export const knowledgeApi = {
  getStats: async () => {
    const response = await apiClient.get("/knowledge-documents/meta/stats");
    return response.data;
  },
  listDocuments: async () => {
    const response = await apiClient.get("/knowledge-documents");
    return response.data;
  },
  uploadDocument: async (
    file: File,
    title?: string,
    documentType?: string,
    uploadedBy?: string,
  ) => {
    const formData = new FormData();
    formData.append("file", file);
    if (title) formData.append("title", title);
    if (documentType) formData.append("document_type", documentType);
    if (uploadedBy) formData.append("uploaded_by", uploadedBy);

    // Let axios set multipart boundary (do not force application/json from defaults)
    const response = await apiClient.post(
      "/knowledge-documents/upload",
      formData,
      {
        headers: { "Content-Type": undefined },
      },
    );
    return response.data;
  },
  deleteDocument: async (documentId: string) => {
    const response = await apiClient.delete(
      `/knowledge-documents/${documentId}`,
    );
    return response.data;
  },
  reingestDocument: async (documentId: string) => {
    const response = await apiClient.post(
      `/knowledge-documents/${documentId}/reingest`,
    );
    return response.data;
  },
  ingestDatasets: async () => {
    const response = await apiClient.post("/knowledge-documents/ingest");
    return response.data;
  },

  scrapeAndIngest: async (url: string, tenantId: string, title?: string) => {
    const response = await apiClient.post("/scraper/scrape-and-ingest", {
      url,
      tenant_id: tenantId,
      title,
    });

    return response.data;
  },

  scrapeTenantDomains: async (tenantId: string) => {
    const response = await apiClient.post("/scraper/scrape-tenant-domains", {
      tenant_id: tenantId,
    });

    return response.data;
  },
};

export const agentApi = {
  listAgents: async (status?: string) => {
    const url =
      status && status !== "all" ? `/agents/status/${status}` : "/agents";
    const response = await apiClient.get(url);
    return response.data;
  },
};

export const policyApi = {
  listPolicies: async () => {
    const response = await apiClient.get("/policies");
    return response.data;
  },
  listActivePolicies: async () => {
    const response = await apiClient.get("/policies/active/list");
    return response.data;
  },
};

export const escalationApi = {
  listEscalations: async (status?: string) => {
    const url =
      status && status !== "all"
        ? `/escalations/status/${status}`
        : "/escalations";
    const response = await apiClient.get(url);
    return response.data;
  },
};

export const conversationApi = {
  listConversations: async () => {
    const response = await apiClient.get("/conversations");
    return response.data;
  },
};

export const notificationApi = {
  listNotifications: async (status?: string) => {
    const url =
      status && status !== "all"
        ? `/notifications/status/${status}`
        : "/notifications";
    const response = await apiClient.get(url);
    return response.data;
  },
};

export const commentApi = {
  listComments: async (ticketId: string) => {
    const response = await apiClient.get(`/ticket-comments/ticket/${ticketId}`);
    return response.data;
  },
  createComment: async (payload: {
    ticket_id: string;
    user_id: string;
    comment: string;
    is_internal: boolean;
  }) => {
    const response = await apiClient.post("/ticket-comments", payload);
    return response.data;
  },
};

export const historyApi = {
  listHistory: async (ticketId: string) => {
    const response = await apiClient.get(`/ticket-history/ticket/${ticketId}`);
    return response.data;
  },
};

export const widgetConfigurationApi = {
  async save(tenantId: string, config: any) {
    const response = await apiClient.post(
      `/widget-configurations/${tenantId}`,
      config,
    );

    return response.data;
  },

  async get(tenantId: string) {
    const response = await apiClient.get(`/widget-configurations/${tenantId}`);

    return response.data;
  },
};

export interface Tenant {
  id: string;
  name: string;
  slug: string;
  api_key: string;
  is_active: boolean;
  created_at: string;
}

export interface CreateTenantRequest {
  name: string;
  slug: string;
}

export interface UpdateTenantRequest {
  name: string;
  slug: string;
  is_active: boolean;
}

export const tenantApi = {
  async listTenants(): Promise<Tenant[]> {
    const response = await apiClient.get("/tenants");

    return response.data;
  },

  async getTenant(tenantId: string): Promise<Tenant> {
    const response = await apiClient.get(`/tenants/${tenantId}`);

    return response.data;
  },

  async createTenant(request: CreateTenantRequest): Promise<Tenant> {
    const response = await apiClient.post("/tenants", request);

    return response.data;
  },

  async updateTenant(
    tenantId: string,
    request: UpdateTenantRequest,
  ): Promise<Tenant> {
    const response = await apiClient.put(`/tenants/${tenantId}`, request);

    return response.data;
  },
};

export interface WidgetDomain {
  id: string;
  tenant_id: string;
  domain: string;
  is_active: boolean;
  created_at: string;
}

export const widgetDomainApi = {
  async getDomains(tenantId: string): Promise<WidgetDomain[]> {
    const response = await apiClient.get(`/widget-domains/${tenantId}`);

    return response.data;
  },

  async createDomain(tenantId: string, domain: string) {
    const response = await apiClient.post("/widget-domains", {
      tenant_id: tenantId,
      domain,
    });

    return response.data;
  },

  async deleteDomain(domainId: string) {
    const response = await apiClient.delete(`/widget-domains/${domainId}`);

    return response.data;
  },
};
