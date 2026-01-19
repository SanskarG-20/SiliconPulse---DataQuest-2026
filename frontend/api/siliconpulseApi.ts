// Hardcoded for stability - bypasses potential .env issues
const BASE_URL = "http://127.0.0.1:8000/api";

console.log("🔌 SiliconPulse API URL (Hardcoded):", BASE_URL);

export interface QueryResponse {
    query: string;
    evidence: any[];
    signal_strength: number;
    last_updated: string;
    report?: string | null;
    llm_status?: string;
}

export interface InjectResponse {
    status: string;
    injected_at: string;
}

export const checkBackendHealth = async (): Promise<boolean> => {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000); // 5s timeout

        // Remove /api suffix to get root health endpoint
        const healthUrl = `${BASE_URL.replace('/api', '')}/health`;

        const response = await fetch(healthUrl, {
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        return response.ok;
    } catch (e) {
        console.error("Backend health check failed:", e);
        return false;
    }
};

export const bootstrapSystem = async (): Promise<any> => {
    try {
        console.log("🚀 Bootstrapping system with fresh signals...");
        const response = await fetch(`${BASE_URL}/bootstrap`, {
            method: "POST"
        });
        return await response.json();
    } catch (e) {
        console.error("Bootstrap failed:", e);
        return { status: "error" };
    }
};

export const querySiliconPulse = async (query: string, k: number = 5): Promise<QueryResponse> => {
    try {
        console.log(`Querying SiliconPulse: "${query}" (k=${k})`);
        const response = await fetch(`${BASE_URL}/query`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ query, k }),
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error(`API Error (${response.status}):`, errorText);
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Normalize evidence to prevent UI crashes
        if (!data.evidence) {
            console.warn("API returned no evidence array, normalizing to []");
            data.evidence = [];
        }

        return data;
    } catch (error: any) {
        console.error("Error querying SiliconPulse:", error);
        if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
            throw new Error("Backend offline. Please check connection.");
        }
        throw error;
    }
};

export const injectSignal = async (title: string, content: string, source: string = "ManualInject"): Promise<InjectResponse> => {
    try {
        console.log(`Injecting signal: ${title}`);
        const response = await fetch(`${BASE_URL}/inject`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ title, content, source }),
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Error injecting signal:", error);
        throw error;
    }
};

export const fetchSignals = async (): Promise<any[]> => {
    try {
        const response = await fetch(`${BASE_URL}/signals`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Error fetching signals:", error);
        return []; // Return empty array on failure to prevent UI crash
    }
};

export const fetchRadar = async (): Promise<any[]> => {
    try {
        const response = await fetch(`${BASE_URL}/radar`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Error fetching radar:", error);
        return []; // Return empty array on failure
    }
};

export const formatEvidenceToContext = (evidence: any[]): string => {
    if (!evidence || evidence.length === 0) return "";

    let context = "LIVE UPDATES CONTEXT:\n";
    evidence.forEach(item => {
        context += `[${item.timestamp || 'N/A'} | ${item.source || 'Unknown'}] ${item.title}\n`;
        context += `Company: ${item.company || 'N/A'} | Event: ${item.event_type || 'General'}\n`;
        context += `Snippet: ${item.snippet}\n\n`;
    });

    return context;
};

export const generateInsight = async (query: string, context: string): Promise<string> => {
    try {
        console.log("Generating insight...");
        const response = await fetch(`${BASE_URL}/generate`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ query, context }),
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data.insight;
    } catch (error) {
        console.error("Error generating insight:", error);
        return "Insight generation unavailable. Please try again later.";
    }
};

export const fetchRecommendations = async (): Promise<any[]> => {
    try {
        const response = await fetch(`${BASE_URL}/recommendations`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data.recommended_queries || [];
    } catch (error) {
        console.error("Error fetching recommendations:", error);
        return []; // Return empty array on failure
    }
};

export const exportAnalysis = async (
    query: string,
    report: string,
    evidence: any[],
    format: string,
    include_evidence: boolean = true
): Promise<void> => {
    try {
        console.log(`Exporting analysis as ${format}...`);
        const response = await fetch(`${BASE_URL}/export`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ query, report, evidence, format, include_evidence }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Handle file download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;

        // Extract filename from header or default
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = `siliconpulse_report_${Date.now()}.${format}`;
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
            if (filenameMatch && filenameMatch.length === 2) {
                filename = filenameMatch[1];
            }
        }

        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

    } catch (error) {
        console.error("Error exporting analysis:", error);
        throw error;
    }
};

export const verifySources = async (query: string): Promise<any> => {
    try {
        console.log(`Verifying sources for: "${query}"`);
        const response = await fetch(`${BASE_URL}/sources/verify?query=${encodeURIComponent(query)}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error("Error verifying sources:", error);
        throw error;
    }
};
