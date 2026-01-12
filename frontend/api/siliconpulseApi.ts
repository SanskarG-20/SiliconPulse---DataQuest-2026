const BASE_URL = "http://127.0.0.1:8000/api";

export interface QueryResponse {
    query: string;
    evidence: any[];
    signal_strength: number;
    last_updated: string;
}

export interface InjectResponse {
    status: string;
    injected_at: string;
}

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
            throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
        }

        const data = await response.json();

        // Normalize evidence to prevent UI crashes
        if (!data.evidence) {
            console.warn("API returned no evidence array, normalizing to []");
            data.evidence = [];
        }

        return data;
    } catch (error) {
        console.error("Error querying SiliconPulse:", error);
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
        throw error;
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
        throw error;
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
        throw error;
    }
};
